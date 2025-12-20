# Verification Flow API Documentation

## Overview

The Verification Flow API provides a comprehensive KYC (Know Your Customer) onboarding system for Chain Of Record. It enables users to submit identity documents, complete liveness checks, and undergo verification review.

## Architecture

### Components

```
backend/app/
├── domain/verification/
│   ├── models.py          # SQLAlchemy models (VerificationRequest, VerificationDocument, VerificationLiveness)
│   ├── repository.py      # Data access layer
│   ├── service.py         # Business logic
│   └── storage.py         # File storage utilities
├── api/v1/
│   └── verification.py    # API endpoints
└── schemas/
    └── verification.py    # Pydantic schemas for request/response
```

### Database Schema

#### verification_requests
- `id` - Primary key
- `user_id` - Foreign key to users table
- `entity_id` - Optional foreign key to entities table
- `person_id` - Optional foreign key to people table
- `status` - Verification status (pending, in_progress, submitted, approved, rejected, needs_review)
- `personal_info` - JSONB field for personal information
- `created_at`, `updated_at`, `submitted_at` - Timestamps
- `reviewed_by`, `reviewed_at`, `notes` - Admin review fields

#### verification_documents
- `id` - Primary key
- `verification_request_id` - Foreign key to verification_requests
- `document_type` - Type of document (drivers_license, passport, utility_bill, etc.)
- `file_path` - Path to stored file
- `file_name`, `file_size`, `mime_type` - File metadata
- `encrypted` - Boolean flag for encryption
- `uploaded_at` - Upload timestamp
- `verified` - Boolean flag for document verification status
- `verification_notes` - Admin notes

#### verification_liveness
- `id` - Primary key
- `verification_request_id` - Foreign key to verification_requests
- `image_path` - Path to selfie/liveness image
- `encrypted` - Boolean flag for encryption
- `liveness_score` - Numeric score (0-100)
- `passed` - Boolean flag for pass/fail
- `checked_at` - Check timestamp
- `check_metadata` - JSONB field for additional metadata

## API Endpoints

### 1. Start Verification

**POST** `/api/v1/verification/start`

Creates a new verification request for the current user.

**Request Body:**
```json
{
  "entity_id": 123,  // Optional
  "person_id": 456,  // Optional
  "personal_info": {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "ssn_last_4": "1234",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Miami",
    "state": "FL",
    "postal_code": "33101",
    "country": "US",
    "phone": "+1234567890",
    "email": "john.doe@example.com"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 1,
  "entity_id": 123,
  "person_id": 456,
  "status": "pending",
  "personal_info": {...},
  "created_at": "2025-12-20T07:15:00Z",
  "updated_at": "2025-12-20T07:15:00Z",
  "submitted_at": null,
  "reviewed_by": null,
  "reviewed_at": null,
  "notes": null
}
```

### 2. Upload Document

**POST** `/api/v1/verification/{verification_id}/upload-document`

Upload identity or supporting documents.

**Form Data:**
- `document_type` - Type of document (drivers_license, passport, national_id, utility_bill, bank_statement, tax_document)
- `file` - Document file (PDF, JPG, PNG)

**Response:** `201 Created`
```json
{
  "id": 1,
  "verification_request_id": 1,
  "document_type": "drivers_license",
  "file_name": "license.jpg",
  "file_size": 2048576,
  "uploaded_at": "2025-12-20T07:20:00Z",
  "verified": false
}
```

**Supported File Types:**
- PDF: `application/pdf`
- JPEG: `image/jpeg`, `image/jpg`
- PNG: `image/png`

### 3. Liveness Check

**POST** `/api/v1/verification/{verification_id}/liveness-check`

Submit selfie for biometric liveness verification.

**Form Data:**
- `image` - Selfie image file (JPG, PNG)

**Response:** `201 Created`
```json
{
  "id": 1,
  "verification_request_id": 1,
  "liveness_score": 85.0,
  "passed": true,
  "checked_at": "2025-12-20T07:25:00Z"
}
```

**Liveness Detection:**
- Score range: 0-100
- Pass threshold: 70
- Currently uses placeholder scoring (to be integrated with ML model)

### 4. Get Status

**GET** `/api/v1/verification/{verification_id}/status`

Get current verification status and progress.

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "in_progress",
  "created_at": "2025-12-20T07:15:00Z",
  "updated_at": "2025-12-20T07:25:00Z",
  "submitted_at": null,
  "documents_count": 2,
  "liveness_checks_count": 1,
  "can_submit": true
}
```

**Status Values:**
- `pending` - Initial state, no documents uploaded
- `in_progress` - Documents being uploaded
- `submitted` - Submitted for admin review
- `needs_review` - Admin requested more information
- `approved` - Verification approved
- `rejected` - Verification rejected

### 5. Submit for Review

**POST** `/api/v1/verification/{verification_id}/submit`

Submit completed verification for admin review.

**Requirements:**
- At least one document uploaded
- Liveness check completed

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "submitted",
  "submitted_at": "2025-12-20T07:30:00Z",
  "message": "Verification submitted for review successfully"
}
```

### 6. Admin: Get Queue

**GET** `/api/v1/verification/admin/queue`

Get list of verification requests pending review (Admin only).

**Query Parameters:**
- `limit` - Maximum results (default: 100, max: 500)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "submitted",
    "created_at": "2025-12-20T07:15:00Z",
    "submitted_at": "2025-12-20T07:30:00Z",
    "documents_count": 2,
    "liveness_checks_count": 1
  }
]
```

### 7. Admin: Get Details

**GET** `/api/v1/verification/admin/{verification_id}`

Get detailed verification information (Admin only).

**Response:** `200 OK`
```json
{
  "id": 1,
  "user_id": 1,
  "entity_id": 123,
  "person_id": 456,
  "status": "submitted",
  "personal_info": {...},
  "created_at": "2025-12-20T07:15:00Z",
  "updated_at": "2025-12-20T07:30:00Z",
  "submitted_at": "2025-12-20T07:30:00Z",
  "reviewed_by": null,
  "reviewed_at": null,
  "notes": null,
  "documents": [
    {
      "id": 1,
      "verification_request_id": 1,
      "document_type": "drivers_license",
      "file_name": "license.jpg",
      "file_size": 2048576,
      "uploaded_at": "2025-12-20T07:20:00Z",
      "verified": false
    }
  ],
  "liveness_checks": [
    {
      "id": 1,
      "verification_request_id": 1,
      "liveness_score": 85.0,
      "passed": true,
      "checked_at": "2025-12-20T07:25:00Z"
    }
  ]
}
```

### 8. Admin: Review

**POST** `/api/v1/verification/admin/{verification_id}/review`

Approve, reject, or request more information (Admin only).

**Request Body:**
```json
{
  "decision": "approve",  // or "reject", "request_more_info"
  "notes": "Verification approved. All documents valid."
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "approved",
  "reviewed_by": 2,
  "reviewed_at": "2025-12-20T08:00:00Z",
  "notes": "Verification approved. All documents valid.",
  "message": "Verification approved successfully"
}
```

**Decision Options:**
- `approve` - Sets status to "approved", updates entity/person verification status
- `reject` - Sets status to "rejected"
- `request_more_info` - Sets status to "needs_review", user can resubmit

## Workflow

### User Flow

1. **Start** - User calls `/verification/start` with personal information
2. **Upload Documents** - User uploads required documents (ID, utility bills, etc.)
3. **Liveness Check** - User completes selfie/liveness verification
4. **Review Status** - User checks `/verification/{id}/status` to see progress
5. **Submit** - When ready, user calls `/verification/{id}/submit`
6. **Wait for Review** - System queues for admin review
7. **Result** - User receives approval or rejection notification

### Admin Flow

1. **View Queue** - Admin calls `/verification/admin/queue` to see pending requests
2. **Review Details** - Admin calls `/verification/admin/{id}` to view full details
3. **Make Decision** - Admin calls `/verification/admin/{id}/review` with decision
4. **Updates Applied** - System updates verification status and linked entities

## Security Features

### File Storage
- Files stored in `/tmp/verification_files` by default (configurable)
- Directory structure: `{base_path}/{verification_id}/{document_type}/{timestamp}_{filename}`
- Encryption flag tracked in database (placeholder for AES-256 implementation)

### Authentication
- Currently uses placeholder user ID functions
- TODO: Implement JWT-based authentication
- Admin endpoints should check for admin role

### Data Protection
- Personal information stored as JSONB
- Sensitive fields (SSN) stored as last 4 digits only
- Document retention policy to be implemented

### Rate Limiting
- TODO: Implement rate limiting per user
- Prevent spam and abuse

## Integration Points

### Entity Verification
When a verification is approved:
- Updates `entities.verification_status` to "verified"
- Sets `entities.verified_at` timestamp
- Updates risk scoring for the entity

### Person Verification
When a verification is approved:
- Updates `people.verification_status` to "verified"
- Sets `people.verified_at` timestamp

## Configuration

Settings in `backend/app/core/config.py`:

```python
verification_file_storage_path: str = "/tmp/verification_files"
verification_max_file_size_mb: int = 10
verification_allowed_document_types: str = "drivers_license,passport,national_id,utility_bill,bank_statement,tax_document"
```

## Testing

Run the test suite:

```bash
cd backend
python test_verification_api.py
```

Test endpoints with curl:

```bash
# Start verification
curl -X POST http://localhost:8000/api/v1/verification/start \
  -H "Content-Type: application/json" \
  -d '{"personal_info": {"first_name": "John", "last_name": "Doe", "date_of_birth": "1990-01-15", "address_line1": "123 Main St", "city": "Miami", "state": "FL", "postal_code": "33101"}}'

# Upload document
curl -X POST http://localhost:8000/api/v1/verification/1/upload-document \
  -F "document_type=drivers_license" \
  -F "file=@/path/to/license.jpg"

# Check status
curl http://localhost:8000/api/v1/verification/1/status
```

## Future Enhancements

### Planned Features
- [ ] Integration with third-party KYC providers (Onfido, Persona, Jumio)
- [ ] Real biometric liveness detection with ML model
- [ ] Document OCR for automatic field extraction
- [ ] Facial recognition matching between ID and selfie
- [ ] Fraud detection with duplicate checking
- [ ] WebSocket notifications for status updates
- [ ] Multi-language support
- [ ] Mobile-optimized camera capture
- [ ] Document retention and cleanup policies
- [ ] GDPR/CCPA compliance tools
- [ ] Analytics dashboard for verification metrics

### Security Enhancements
- [ ] AES-256 encryption for stored documents
- [ ] End-to-end encryption for uploads
- [ ] JWT authentication with role-based access
- [ ] Rate limiting per user/IP
- [ ] Audit logging for all actions
- [ ] IP tracking and geolocation
- [ ] Device fingerprinting
- [ ] Anti-fraud checks

## Support

For issues or questions about the verification API:
- GitHub Issues: https://github.com/Adahandles/Chain-Of-Record/issues
- Documentation: See `/docs` endpoint when running locally
- OpenAPI Spec: http://localhost:8000/openapi.json
