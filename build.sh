#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install email-validator flask flask-sqlalchemy gunicorn pillow psycopg2-binary qrcode sqlalchemy werkzeug


# Ensure templates directory exists and is accessible
echo "Setting up template directory..."
if [ ! -d "templates" ]; then
    echo "Templates directory not found, creating it..."
    mkdir -p templates
fi

# Copy template files if they exist in a different location
if [ -d "../templates" ]; then
    echo "Found templates in parent directory, copying..."
    cp -r ../templates/* templates/
fi

# Verify project structure
echo "Final project structure:"
ls -la
echo "Templates directory:"
ls -la templates/

# Set proper permissions
chmod -R 755 templates/
chmod -R 755 static/

# Only run database setup if DATABASE_URL is available
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL found, setting up database..."
    python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
else
    echo "DATABASE_URL not found, skipping database setup (will be handled at runtime)"
fi

echo "Build completed successfully"
