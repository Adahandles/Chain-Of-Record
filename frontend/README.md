# Chain Of Record - Frontend

Modern, responsive web dashboard for the Chain Of Record entity and property intelligence platform. Built with Next.js 14+, TypeScript, and Tailwind CSS.

## 🚀 Features

### Core Functionality
- **Real-time Risk Score Visualization**: Interactive trust score cards and risk grade charts
- **Entity Management**: Search, filter, and explore business entities with detailed views
- **Property Intelligence**: Browse property records with comprehensive financial data
- **Relationship Mapping**: Visualize connections between entities and properties
- **Alert System**: Monitor high-risk entities with real-time notifications

### Technical Highlights
- ✅ **Next.js 14+** with App Router and Server Components
- ✅ **TypeScript** for type safety throughout
- ✅ **Tailwind CSS** for responsive design
- ✅ **shadcn/ui** component library
- ✅ **TanStack Query** for efficient data fetching and caching
- ✅ **Recharts** for data visualization
- ✅ **Mobile-first responsive design**
- ✅ **Dark mode support**

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

## 🛠️ Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 🎯 Usage

### Authentication
Use any email and password to log in (demo mode).

### Searching Entities
1. Navigate to "Entities" from the sidebar
2. Filter by name, jurisdiction, type, or status
3. Click any entity card for details

### Risk Scores
- **Grade A**: Low risk (green)
- **Grade B**: Moderate risk (blue)
- **Grade C**: Medium risk (yellow)
- **Grade D**: High risk (orange)
- **Grade F**: Critical risk (red)

## 📱 Responsive Design

Optimized for mobile, tablet, and desktop devices.

## 📄 License

MIT License - Part of the Chain Of Record platform.
