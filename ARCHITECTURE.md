# Jetpo Architecture Documentation

## Overview

Jetpo is built with a scalable, modular architecture designed to support future growth and mobile application development. The system follows Django best practices and uses a service-oriented approach.

## Design Principles

1. **Separation of Concerns**: Each app handles a specific domain
2. **DRY (Don't Repeat Yourself)**: Shared functionality in core app
3. **API-First**: REST APIs prepared for mobile app
4. **Extensibility**: User types and features can be added without major refactoring
5. **Security**: Email verification, secure authentication, CORS configuration

## Application Architecture

### Core Apps

#### 1. Accounts App
**Purpose**: User management and authentication

**Models**:
- `User`: Custom user model with email authentication
  - Fields: email, first_name, last_name, user_type, phone_number, date_of_birth
  - User types: STANDARD, PREMIUM, ADVISOR, ADMIN
  - Methods: `get_full_name()`, `get_short_name()`, `is_premium`, `is_advisor`

**Key Features**:
- Email-based authentication (no username)
- Extensible user types for future features
- Profile fields for user preferences
- Custom UserManager for user creation

#### 2. Funds App (To Be Implemented)
**Purpose**: Manage fund data from Gemelnet

**Planned Models**:
- `Fund`: Individual mutual fund
  - Fields: fund_id, name, type, management_company, inception_date
- `FundPerformance`: Historical performance data
  - Fields: fund, date, return_1m, return_3m, return_1y, return_3y
- `FundHolding`: Fund portfolio holdings
  - Fields: fund, security, weight, date

**Data Synchronization**:
- Periodic sync from Gemelnet/Data.gov.il
- Background tasks using Celery (future)
- Data validation and cleaning

#### 3. Portfolios App (To Be Implemented)
**Purpose**: User portfolio management

**Planned Models**:
- `Portfolio`: User's investment portfolio
  - Fields: user, name, description, created_at, updated_at
- `PortfolioHolding`: Funds within a portfolio
  - Fields: portfolio, fund, amount_invested, units, purchase_date
- `PortfolioSnapshot`: Historical portfolio value
  - Fields: portfolio, date, total_value, return_pct

#### 4. Core App
**Purpose**: Shared utilities and base classes

**Planned Components**:
- Base models (TimeStampedModel)
- Utility functions
- Custom template tags
- Shared validators

## Database Schema

### User Model
```
User
├── id (Primary Key)
├── email (Unique, indexed)
├── first_name
├── last_name
├── user_type (indexed)
├── password (hashed)
├── is_active
├── is_staff
├── is_superuser
├── date_joined
├── last_login
├── phone_number
├── date_of_birth
└── email_notifications
```

### Future Schema (Funds)
```
Fund
├── id (Primary Key)
├── fund_id (Unique, from Gemelnet)
├── name
├── type
├── management_company
├── inception_date
└── is_active

FundPerformance
├── id (Primary Key)
├── fund (Foreign Key)
├── date
├── nav (Net Asset Value)
├── return_1m
├── return_3m
├── return_1y
└── return_3y
```

### Future Schema (Portfolios)
```
Portfolio
├── id (Primary Key)
├── user (Foreign Key)
├── name
├── description
├── created_at
└── updated_at

PortfolioHolding
├── id (Primary Key)
├── portfolio (Foreign Key)
├── fund (Foreign Key)
├── amount_invested
├── units
├── purchase_date
└── notes
```

## Authentication Flow

1. **Registration**
   - User provides email, name, and password
   - System sends verification email
   - User clicks verification link
   - Account activated, user logged in

2. **Login**
   - User provides email and password
   - System validates credentials
   - Session created
   - User redirected to dashboard

3. **Password Reset**
   - User requests reset via email
   - System sends reset link
   - User sets new password
   - User can log in with new password

## API Architecture (Future)

### REST API Design
- **Endpoints**: `/api/v1/`
- **Authentication**: JWT tokens
- **Versioning**: URL-based versioning
- **Pagination**: Page number pagination (20 items/page)

### Planned Endpoints
```
Auth:
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/refresh/

Funds:
GET    /api/v1/funds/
GET    /api/v1/funds/{id}/
GET    /api/v1/funds/{id}/performance/

Portfolios:
GET    /api/v1/portfolios/
POST   /api/v1/portfolios/
GET    /api/v1/portfolios/{id}/
PUT    /api/v1/portfolios/{id}/
DELETE /api/v1/portfolios/{id}/
GET    /api/v1/portfolios/{id}/holdings/
POST   /api/v1/portfolios/{id}/holdings/
```

## Frontend Architecture

### Tailwind CSS
- **Utility-First**: Compose designs using utility classes
- **Custom Theme**: Primary colors, fonts configured
- **Components**: Reusable button, input, card classes
- **Responsive**: Mobile-first design approach

### Template Structure
```
base.html (Base template)
├── Navigation bar
├── Messages
├── Content block
└── Footer

home.html (Homepage)
├── Hero section
├── Features
└── Call-to-action

account/*.html (Auth pages)
├── Login
├── Signup
├── Logout
└── Password reset
```

## Security Considerations

1. **Authentication**
   - Email verification required
   - Strong password validation
   - CSRF protection enabled
   - Session security

2. **Authorization**
   - Permission-based access control
   - User type differentiation
   - Portfolio ownership validation

3. **Data Protection**
   - Environment variables for secrets
   - Database password hashing
   - Secure email configuration
   - HTTPS in production

4. **API Security** (Future)
   - JWT token authentication
   - CORS configuration
   - Rate limiting
   - Request validation

## Scalability Considerations

### Current (Phase 1)
- SQLite for development
- Synchronous request handling
- Server-side rendering

### Future (Phase 2+)
- PostgreSQL with connection pooling
- Redis for caching
- Celery for background tasks
- CDN for static files
- Load balancing with multiple servers

## Development Workflow

1. **Local Development**
   - SQLite database
   - Debug mode enabled
   - Console email backend
   - Hot-reload for Tailwind

2. **Testing**
   - pytest for unit tests
   - factory_boy for test data
   - Coverage reporting

3. **Production**
   - PostgreSQL database
   - Gunicorn WSGI server
   - Whitenoise for static files
   - Real email backend
   - Error logging and monitoring

## Mobile App Integration (Future)

### Architecture
```
Mobile App (React Native/Flutter)
    ↓
REST API (Django REST Framework)
    ↓
Django Backend
    ↓
PostgreSQL Database
```

### Authentication Flow
1. User logs in via mobile app
2. App receives JWT access/refresh tokens
3. App stores tokens securely
4. App includes token in API requests
5. Token refreshed when expired

## Future Enhancements

1. **Performance Optimization**
   - Database query optimization
   - Caching strategy
   - Lazy loading
   - Image optimization

2. **Features**
   - Real-time notifications
   - Advanced analytics
   - Social features (share portfolios)
   - Financial advisor tools

3. **Infrastructure**
   - CI/CD pipeline
   - Automated testing
   - Monitoring and alerting
   - Backup strategy

## Technology Decisions

### Why Django?
- Rapid development
- Built-in admin interface
- Strong security features
- Excellent ORM
- Large ecosystem

### Why Tailwind CSS?
- Minimal, modern design
- Highly customizable
- Small bundle size
- Responsive utilities
- Great developer experience

### Why Django Allauth?
- Email authentication support
- Extensible
- Social auth ready (future)
- Well-maintained
- Email verification built-in

### Why DRF?
- Industry standard for Django APIs
- Great serialization
- Built-in authentication
- Browsable API
- Mobile app ready
