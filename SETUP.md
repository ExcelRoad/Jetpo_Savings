# Jetpo Setup Guide

This guide will help you set up the Jetpo project on your local machine.

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Node.js packages (for Tailwind)
npm install
```

### 2. Run Migrations

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

```bash
# Create an admin account
python manage.py createsuperuser
# Enter your email, first name, last name, and password
```

### 4. Build CSS

```bash
# Build Tailwind CSS
npm run tailwind:build
```

### 5. Run Server

```bash
# Start the development server
python manage.py runserver
```

Visit http://localhost:8000 to see your app!

## Development Setup (With Live Reload)

For the best development experience, run these commands in separate terminals:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Tailwind Watch Mode:**
```bash
npm run tailwind:watch
```

This will automatically rebuild your CSS when you change any HTML templates.

## Environment Variables (Optional)

For development, you can use the default settings. For production or custom configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

### Key Settings:
- `SECRET_KEY`: Django secret key (auto-generated for dev)
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_*`: Email configuration for password resets

## Database Setup

### SQLite (Default - Development)
No setup needed! SQLite file will be created automatically.

### PostgreSQL (Recommended for Production)

1. Install PostgreSQL
2. Create a database:
```sql
CREATE DATABASE jetpo_db;
CREATE USER jetpo_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE jetpo_db TO jetpo_user;
```

3. Update your `.env`:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jetpo_db
DB_USER=jetpo_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

4. Update `config/settings.py` to use environment variables for database.

## Testing the Setup

### 1. Access the Homepage
Visit: http://localhost:8000

You should see the Jetpo homepage with a hero section and features.

### 2. Create an Account
- Click "Sign Up"
- Fill in your email, name, and password
- Check your console for the verification email (development mode)
- Copy the verification link and paste it in your browser

### 3. Sign In
- Click "Sign In"
- Enter your email and password
- You should be redirected to the homepage (logged in)

### 4. Admin Interface
Visit: http://localhost:8000/admin
- Log in with your superuser credentials
- You can manage users, view the database, etc.

## Common Issues

### Issue: "No module named 'decouple'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "No such table: accounts_user"
**Solution**: Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: CSS not loading
**Solution**: Build Tailwind CSS
```bash
npm run tailwind:build
```

### Issue: Email verification not working
**Solution**: In development, emails are printed to the console. Check your terminal running the Django server for the verification link.

To use real emails, configure `EMAIL_*` settings in `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Next Steps

### 1. Explore the Admin
- Create test users
- Explore the user management interface
- Customize the admin as needed

### 2. Start Building Features
- Implement the Funds app
- Set up data synchronization with Gemelnet
- Build the portfolio management system

### 3. Customize the Design
- Update colors in `tailwind.config.js`
- Modify templates in `templates/`
- Add custom CSS in `static/css/input.css`

## Useful Commands

```bash
# Run development server
python manage.py runserver

# Create new app
python manage.py startapp app_name

# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Run Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Build CSS (production)
npm run tailwind:build

# Watch CSS (development)
npm run tailwind:watch
```

## Project Structure

```
Jetpo/
├── accounts/              # User management
├── config/               # Settings and URLs
├── core/                 # Shared utilities
├── funds/                # Fund management (to implement)
├── portfolios/           # Portfolio management (to implement)
├── templates/            # HTML templates
│   ├── base.html
│   ├── home.html
│   └── account/          # Auth templates
├── static/
│   └── css/
│       ├── input.css     # Tailwind input
│       └── output.css    # Generated CSS
├── manage.py
├── requirements.txt
├── package.json
└── tailwind.config.js
```

## Development Best Practices

1. **Always activate your virtual environment** before running commands
2. **Run migrations** after any model changes
3. **Rebuild Tailwind CSS** after template changes (or use watch mode)
4. **Use the admin interface** to manage data during development
5. **Check the console** for email verification links in development
6. **Keep your dependencies updated** but test thoroughly

## Getting Help

- Check the [README.md](README.md) for project overview
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions
- Django documentation: https://docs.djangoproject.com/
- Tailwind CSS documentation: https://tailwindcss.com/docs

## Ready to Go!

You're all set! Start the development server and begin building Jetpo.

```bash
# Terminal 1
python manage.py runserver

# Terminal 2
npm run tailwind:watch
```

Happy coding! 🚀
