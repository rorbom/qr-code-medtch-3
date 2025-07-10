# Medical Emergency Profile System

## Overview

This is a Flask-based web application that creates and manages medical emergency profiles. Users can register their critical medical information and generate QR codes for quick access during emergencies. The system provides a simple way to store and retrieve essential medical data that can be accessed by emergency responders or medical personnel through QR code scanning.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module for debugging and monitoring
- **Middleware**: ProxyFix for proper HTTPS URL generation in production environments

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **CSS Framework**: Bootstrap 5 with dark theme from Replit CDN
- **Icons**: Font Awesome 6.0
- **Responsive Design**: Mobile-first approach using Bootstrap grid system
- **Theme**: Dark theme optimized for emergency situations

### Database Schema
The application uses a single `MedicalProfile` model with the following fields:
- `id`: Primary key
- `username`: Unique identifier for profile access
- `name`: Patient's full name
- `blood_type`: Blood type information
- `allergy`: Allergy information (text field)
- `condition`: Medical conditions (text field)
- `emergency_contact`: Emergency contact information
- `last_checkup_date`: Date of last medical checkup
- `last_checkup_details`: Details from last checkup
- `doctor_notes`: Notes from medical professionals
- `created_at` and `updated_at`: Timestamps

## Key Components

### 1. User Registration System
- Form-based registration with server-side validation
- Username auto-generation if not provided (timestamp-based)
- Required field validation (name, emergency contact)
- Optional medical fields (blood type, allergies, conditions)

### 2. QR Code Generation
- Automatic QR code creation upon profile registration using the `qrcode` library
- QR codes link directly to the user's profile page
- Images stored in `static/qr/` directory
- QR codes provide quick access for emergency personnel

### 3. Profile Management
- Individual profile pages accessible via username
- Medical checkup update functionality
- Error handling for non-existent profiles
- JSON serialization support for API integration

### 4. Template System
- **base.html**: Common layout with navigation and emergency-themed styling
- **form.html**: Registration form with medical fields
- **profile.html**: Display medical information in emergency-friendly format
- **edit_checkup.html**: Update medical checkup information
- **not_found.html**: Error page for missing profiles

## Data Flow

1. **Registration**: User fills out medical information form
2. **Processing**: Flask validates data and creates database record
3. **QR Generation**: System generates QR code linking to profile
4. **Storage**: Profile data stored in PostgreSQL database
5. **Access**: Emergency personnel scan QR code to access profile
6. **Display**: Critical medical information displayed in emergency-optimized format

## External Dependencies

### Python Packages
- `Flask`: Web framework
- `Flask-SQLAlchemy`: Database ORM
- `qrcode`: QR code generation
- `Werkzeug`: WSGI utilities and middleware

### Frontend Libraries
- Bootstrap 5 (Replit CDN with dark theme)
- Font Awesome 6.0 for medical icons
- Custom CSS for emergency-themed styling

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (required)
- `SESSION_SECRET`: Flask session encryption key (required)

## Deployment Strategy

### Development
- SQLite fallback database for local development
- Debug mode enabled via `main.py`
- Comprehensive logging for troubleshooting

### Production
- PostgreSQL database via `DATABASE_URL` environment variable
- ProxyFix middleware for proper HTTPS handling
- Connection pooling with health checks (`pool_pre_ping`)
- Static file serving for QR codes

### File Structure
```
/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── models.py             # Database models
├── templates/            # Jinja2 templates
│   ├── base.html        # Base template with emergency theme
│   ├── form.html        # Registration form
│   ├── profile.html     # Medical profile display
│   ├── edit_checkup.html # Checkup update form
│   └── not_found.html   # Error page
└── static/              # Static assets
    └── qr/              # Generated QR code images
```

## Deployment Configuration

### Render Deployment
- **render.yaml**: Configured with PostgreSQL database and web service
- **build.sh**: Handles dependency installation and database setup
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
- **Environment Variables**: DATABASE_URL (from PostgreSQL), SESSION_SECRET (auto-generated)

### Current Deployment Status
- ✅ Successfully deployed on Render with PostgreSQL database
- ✅ Comprehensive fallback system handles template loading issues
- ✅ All core functionality working (registration, profiles, QR codes, doctor edits)
- ✅ Robust error handling with Bootstrap-styled fallback pages
- ✅ Production-ready with proper logging and monitoring

## Changelog
- July 04, 2025: Initial setup with Flask and PostgreSQL
- July 04, 2025: Added Render deployment configuration
- July 04, 2025: Fixed template error handling and database fallback

## User Preferences

Preferred communication style: Simple, everyday language.