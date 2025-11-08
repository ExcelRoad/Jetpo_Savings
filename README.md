# Jetpo - Israeli Pension & Mutual Funds Portfolio Manager

> Modern web application for managing Israeli pension and mutual fund portfolios with real-time data from Gemelnet.

[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue.svg)](https://www.postgresql.org/)

## 🌟 Features

### ✅ Implemented

- **Fund Management**
  - Browse 1000+ Israeli pension/provident funds
  - Real-time data sync from Gemelnet (data.gov.il)
  - Historical performance data (1999-2025)
  - Detailed fund information and analytics
  - Fund search, filtering, and comparison
  - "Like" favorite funds

- **Portfolio Management**
  - Create multiple portfolios with custom names
  - Track investments with purchase dates and legal IDs
  - Periodic contribution tracking
  - Future value projections
  - Portfolio performance analytics
  - Owner information per portfolio

- **Knowledge Center**
  - User-submitted articles
  - Rich text editor (CKEditor) for content formatting
  - Article review system with status tracking
  - Categories and tags
  - Comment system
  - Article likes and views counter

- **User Management**
  - Email-based authentication (no username)
  - Profile management with photo upload
  - Contact request system with portfolio sharing
  - Dark mode support
  - Hebrew RTL interface

- **Modern UI**
  - Clean, minimal Notion-inspired design
  - Fully responsive (mobile, tablet, desktop)
  - Dark mode throughout
  - Hebrew language with RTL support
  - Interactive charts (Chart.js)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for Tailwind CSS)
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
   ```bash
   cd Jetpo
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt

   # Node.js dependencies (Tailwind CSS)
   npm install
   ```

4. **Environment variables** (optional for development)
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Build CSS**
   ```bash
   npm run tailwind:build
   ```

8. **Import fund data** (optional)
   ```bash
   # Import recent fund data (2016+)
   python manage.py import_historical_data --source recent

   # Import full historical data (1999+)
   python manage.py import_historical_data --source historical
   ```

### Running the Development Server

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Tailwind CSS watch (optional)
npm run tailwind:watch
```

Visit: **http://localhost:8000**

## 📁 Project Structure

```
Jetpo/
├── accounts/              # User authentication & profiles
├── core/                  # Contact requests & shared utilities
├── funds/                 # Fund data & management
│   ├── models.py         # Fund, Company, FundSnapshot models
│   ├── management/       # Data import commands
│   └── templates/        # Fund browsing pages
├── portfolios/           # Portfolio management
│   ├── models.py         # Portfolio & PortfolioHolding models
│   └── templates/        # Portfolio pages
├── knowledge_center/     # Article & knowledge base
│   ├── models.py         # Article, ArticleSubmission models
│   └── templates/        # Knowledge center pages
├── config/               # Django settings
├── templates/            # Base templates
├── static/               # Static files (CSS, images)
└── staticfiles/          # Collected static files
```

## 🛠 Technology Stack

### Backend
- **Django 5.1.4** - Web framework
- **PostgreSQL** - Database (with SQLite for dev)
- **Django Allauth** - Authentication
- **Django REST Framework** - API (future mobile app)
- **Pandas** - Data processing

### Frontend
- **Tailwind CSS 3.4** - Styling
- **Chart.js 4.4** - Interactive charts
- **CKEditor** - Rich text editing
- **Rubik Font** - Hebrew typography

### Data Sources
- **Gemelnet (data.gov.il)** - Israeli pension/provident fund data
  - Recent data: 2016-2025 (~8,300 records)
  - Historical data: 1999-2025 (~155,000 records)

## 📊 Data Management

### Import Historical Data

```bash
# Import recent data (2016-2025)
python manage.py import_historical_data --source recent

# Import historical data (1999-2025)
python manage.py import_historical_data --source historical

# Import both
python manage.py import_historical_data --source both
```

### Data Structure

The system stores:
- **Companies**: Fund management companies
- **Funds**: Individual funds with detailed information
- **FundSnapshots**: Monthly performance data
  - Monthly, YTD, 3-year, 5-year returns
  - Total assets, management fees
  - Exposure metrics (stocks, foreign assets, etc.)

## 👤 User Types

- **Standard User** - Default user with full access
- **Premium User** - Future premium features
- **Financial Advisor** - Future advisor features
- **Administrator** - Full system access

## 🎨 Design Philosophy

- **Minimal & Clean** - Notion-inspired interface
- **Hebrew First** - Full RTL support
- **Dark Mode** - Complete dark theme
- **Responsive** - Mobile-first design
- **Accessible** - WCAG compliance focus

## 📱 API (Future)

REST API prepared for mobile app development:
- JWT authentication
- Fund endpoints
- Portfolio endpoints
- User management

## 🔒 Security Features

- Email verification required
- Secure password reset
- CSRF protection
- SQL injection prevention
- XSS protection

## 📝 Development

### Common Commands

```bash
# Django
python manage.py runserver          # Start server
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py shell              # Django shell

# Tailwind
npm run tailwind:build              # Build CSS
npm run tailwind:watch              # Watch CSS changes

# Data
python manage.py import_historical_data  # Import fund data
```

### Code Quality

```bash
# Format code
black .

# Check code style
flake8

# Run tests
pytest
```

## 🌐 URLs

- **Homepage**: `/`
- **Funds**: `/funds/`
- **Portfolios**: `/portfolios/`
- **Knowledge Center**: `/knowledge-center/`
- **Profile**: `/user/profile/`
- **Admin**: `/admin/`

## 📄 License

Proprietary - All rights reserved

## 🤝 Contributing

This is a private project. For questions or suggestions, please contact the development team.

## 📞 Support

For support or inquiries, please open an issue or contact the development team.

---

**Built with ❤️ for the Israeli investment community**
