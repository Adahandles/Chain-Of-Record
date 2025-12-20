# Verification Flow Implementation

This feature adds a comprehensive KYC (Know Your Customer) verification system to Chain Of Record.

## What's Implemented

### Backend API (8 Endpoints)
1. **POST /api/v1/verification/start** - Start new verification request
2. **POST /api/v1/verification/{id}/upload-document** - Upload identity documents
3. **POST /api/v1/verification/{id}/liveness-check** - Submit selfie for liveness check
4. **GET /api/v1/verification/{id}/status** - Get verification status
5. **POST /api/v1/verification/{id}/submit** - Submit for admin review
6. **GET /api/v1/verification/admin/queue** - Get admin review queue
7. **GET /api/v1/verification/admin/{id}** - Get detailed verification info
8. **POST /api/v1/verification/admin/{id}/review** - Admin approve/reject/request more info

### Database Schema
- **verification_requests** - Main verification tracking table
- **verification_documents** - Uploaded document storage
- **verification_liveness** - Liveness/selfie check results
- **Migration 002** - Added verification tables and columns

### Domain Layer
- **Models** - SQLAlchemy models for all verification entities
- **Repository** - Data access layer with CRUD operations
- **Service** - Business logic for verification workflow
- **Storage** - File storage utility with encryption support
- **Schemas** - Pydantic models for API validation

## File Structure

```
backend/
├── alembic/versions/
│   └── 002_add_verification_tables.py    # Database migration
├── app/
│   ├── api/v1/
│   │   └── verification.py               # API endpoints
│   ├── domain/verification/
│   │   ├── __init__.py
│   │   ├── models.py                     # SQLAlchemy models
│   │   ├── repository.py                 # Data access layer
│   │   ├── service.py                    # Business logic
│   │   └── storage.py                    # File storage
│   ├── schemas/
│   │   └── verification.py               # Pydantic schemas
│   └── core/
│       └── config.py                     # Updated with verification settings
└── test_verification_api.py              # API test script

docs/
└── VERIFICATION_API.md                   # Comprehensive API documentation
```

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
# Set up database URL in .env
echo "DATABASE_URL=postgresql://user:pass@localhost:5432/chain" > .env

# Run migration
alembic upgrade head
```

### 3. Start API Server
```bash
uvicorn app.main:app --reload
```

### 4. Test API
```bash
# Run test script
python test_verification_api.py

# Or view API docs
open http://localhost:8000/docs
```

## Usage Example

### User Workflow

```bash
# 1. Start verification
curl -X POST http://localhost:8000/api/v1/verification/start \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1990-01-15",
      "address_line1": "123 Main St",
      "city": "Miami",
      "state": "FL",
      "postal_code": "33101"
    }
  }'

# Response: {"id": 1, "status": "pending", ...}

# 2. Upload driver's license
curl -X POST http://localhost:8000/api/v1/verification/1/upload-document \
  -F "document_type=drivers_license" \
  -F "file=@license.jpg"

# 3. Submit selfie
curl -X POST http://localhost:8000/api/v1/verification/1/liveness-check \
  -F "image=@selfie.jpg"

# 4. Check status
curl http://localhost:8000/api/v1/verification/1/status

# Response: {"status": "in_progress", "can_submit": true, ...}

# 5. Submit for review
curl -X POST http://localhost:8000/api/v1/verification/1/submit

# Response: {"status": "submitted", "message": "Verification submitted for review successfully"}
```

### Admin Workflow

```bash
# 1. View pending verifications
curl http://localhost:8000/api/v1/verification/admin/queue

# 2. Get details for review
curl http://localhost:8000/api/v1/verification/admin/1

# 3. Approve verification
curl -X POST http://localhost:8000/api/v1/verification/admin/1/review \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "notes": "All documents verified successfully"
  }'

# Response: {"status": "approved", "message": "Verification approved successfully"}
```

## Features

### Implemented
- ✅ Multi-step verification workflow
- ✅ Document upload with type validation (PDF, JPG, PNG)
- ✅ Liveness check with scoring
- ✅ Real-time status tracking
- ✅ Admin review queue and decision workflow
- ✅ Integration with entities and people tables
- ✅ File storage with encryption support
- ✅ Comprehensive API documentation
- ✅ Test script for validation

### Placeholders (To Be Enhanced)
- ⚠️ Authentication (uses placeholder user IDs)
- ⚠️ File encryption (flag tracked, encryption to be implemented)
- ⚠️ Liveness detection (placeholder scoring, needs ML model)
- ⚠️ Rate limiting (to be added)
- ⚠️ Fraud detection (to be added)

## Configuration

Settings in `backend/app/core/config.py`:

```python
# Verification file storage
verification_file_storage_path: str = "/tmp/verification_files"

# Max file size in MB
verification_max_file_size_mb: int = 10

# Allowed document types
verification_allowed_document_types: str = "drivers_license,passport,national_id,utility_bill,bank_statement,tax_document"
```

## Testing

```bash
# Run API test script
cd backend
python test_verification_api.py

# Expected output:
# ✓ All tests passed!
# - App info endpoint works
# - API info endpoint works
# - Health check works
# - OpenAPI schema includes verification endpoints
```

## Integration

### With Entities
When a verification is approved:
- Sets `entities.verification_status = 'verified'`
- Sets `entities.verified_at = NOW()`
- Updates entity risk score

### With People
When a verification is approved:
- Sets `people.verification_status = 'verified'`
- Sets `people.verified_at = NOW()`

## Security Considerations

### Current Implementation
- Personal information stored in JSONB field
- SSN stored as last 4 digits only
- Files stored with encryption flag
- Admin-only endpoints for review

### Production Requirements
1. **Authentication**: Implement JWT tokens with role-based access
2. **Encryption**: Add AES-256 encryption for stored files
3. **Rate Limiting**: Prevent abuse and spam
4. **Audit Trail**: Log all verification actions
5. **GDPR/CCPA**: Implement data retention and deletion policies
6. **IP Tracking**: Track submissions for fraud detection

## Future Enhancements

### Near-term
- [ ] JWT authentication and role-based access control
- [ ] Real file encryption (AES-256)
- [ ] Rate limiting per user/IP
- [ ] Email/SMS notifications

### Long-term
- [ ] Third-party KYC provider integration (Onfido, Persona, Jumio)
- [ ] ML-based liveness detection
- [ ] Document OCR for automatic field extraction
- [ ] Facial recognition matching
- [ ] Fraud detection with duplicate checking
- [ ] WebSocket notifications
- [ ] Mobile-optimized camera capture
- [ ] Multi-language support
- [ ] Analytics dashboard

## Documentation

- **API Documentation**: `docs/VERIFICATION_API.md`
- **OpenAPI Spec**: http://localhost:8000/openapi.json (when running)
- **Interactive Docs**: http://localhost:8000/docs (when running)

## Support

For issues or questions:
- GitHub Issues: https://github.com/Adahandles/Chain-Of-Record/issues
- See documentation at `/docs` endpoint

## License

MIT License - See LICENSE file for details
