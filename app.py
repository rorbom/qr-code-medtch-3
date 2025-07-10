from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import qrcode
import logging
from datetime import datetime
from models import db, MedicalProfile
from werkzeug.middleware.proxy_fix import ProxyFix
from io import BytesIO

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    app.logger.warning("DATABASE_URL environment variable not set, using SQLite fallback")
    database_url = "sqlite:///medical_profiles.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for user registration form and profile creation"""
    if request.method == 'POST':
        # Debug: Log form data
        app.logger.info(f"Form data received: {dict(request.form)}")
        username = request.form.get('username', '').strip().lower()
        
        # Generate username if not provided
        if not username:
            import time
            username = f"profile_{int(time.time())}"
        
        # Check if username already exists
        existing_profile = MedicalProfile.query.filter_by(username=username).first()
        if existing_profile:
            import time
            username = f"{username}_{int(time.time())}"
        
        # Get form data
        name = request.form.get('name', '').strip()
        if not name:
            name = "Anonymous User"
            
        # Parse checkup date
        checkup_date_str = request.form.get('last_checkup_date', '')
        checkup_date = None
        if checkup_date_str:
            try:
                checkup_date = datetime.strptime(checkup_date_str, '%Y-%m-%d').date()
            except ValueError:
                checkup_date = None

        try:
            # Create new profile
            profile = MedicalProfile(
                username=username,
                name=name,
                blood_type=request.form.get('blood_type', ''),
                allergy=request.form.get('allergy', '').strip(),
                condition=request.form.get('condition', '').strip(),
                emergency_contact=request.form.get('emergency_contact', '').strip(),
                last_checkup_date=checkup_date,
                last_checkup_details=request.form.get('last_checkup_details', '').strip()
            )
            
            # Save to database
            db.session.add(profile)
            db.session.commit()

            app.logger.info(f"Profile created successfully for user: {username}")
            return redirect(url_for('view_profile', username=username))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating profile for {username}: {str(e)}")
            return render_template('form.html', error="An error occurred while creating your profile. Please try again.")

    try:
        return render_template('form.html')
    except:
        # Fallback HTML form if template is missing
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Medical Emergency Profile</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        </head>
        <body data-bs-theme="dark">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-lg-8">
                        <div class="card">
                            <div class="card-header bg-danger text-white text-center py-4">
                                <h2>Create Medical Emergency Profile</h2>
                                <p class="mb-0">This information will be accessible via QR code for emergency situations</p>
                            </div>
                            <div class="card-body p-4">
                                <form method="POST" action="/">
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <label for="name" class="form-label">Full Name *</label>
                                            <input type="text" class="form-control" id="name" name="name" required>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="username" class="form-label">Username (optional)</label>
                                            <input type="text" class="form-control" id="username" name="username">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <label for="blood_type" class="form-label">Blood Type</label>
                                            <select class="form-select" id="blood_type" name="blood_type">
                                                <option value="">Select Blood Type</option>
                                                <option value="A+">A+</option>
                                                <option value="A-">A-</option>
                                                <option value="B+">B+</option>
                                                <option value="B-">B-</option>
                                                <option value="AB+">AB+</option>
                                                <option value="AB-">AB-</option>
                                                <option value="O+">O+</option>
                                                <option value="O-">O-</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="emergency_contact" class="form-label">Emergency Contact *</label>
                                            <input type="text" class="form-control" id="emergency_contact" name="emergency_contact" required>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <label for="allergy" class="form-label">Allergies</label>
                                            <textarea class="form-control" id="allergy" name="allergy" rows="3"></textarea>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="condition" class="form-label">Medical Conditions</label>
                                            <textarea class="form-control" id="condition" name="condition" rows="3"></textarea>
                                        </div>
                                    </div>
                                    <div class="text-center">
                                        <button type="submit" class="btn btn-success btn-lg">Create Profile & Generate QR Code</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''

@app.route('/profile/<username>')
def view_profile(username):
    """Display user profile with medical information"""
    try:
        profile = MedicalProfile.query.filter_by(username=username).first()
        
        if not profile:
            app.logger.warning(f"Profile not found for username: {username}")
            return render_template('not_found.html', username=username), 404
        
        # Convert profile to dict for template
        info = {
            'name': profile.name,
            'blood_type': profile.blood_type,
            'allergy': profile.allergy,
            'condition': profile.condition,
            'emergency_contact': profile.emergency_contact,
            'last_checkup_date': profile.last_checkup_date.isoformat() if profile.last_checkup_date else None,
            'last_checkup_details': profile.last_checkup_details,
            'doctor_notes': profile.doctor_notes
        }
        
        # Generate QR code
        profile_link = url_for('view_profile', username=username, _external=True)
        qr_dir = os.path.join(app.static_folder, 'qr')
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, f"{username}.png")
        
        if not os.path.exists(qr_path):
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(profile_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_path)
            app.logger.info(f"Generated QR code for {username} at {qr_path}")

        qr_code_url = url_for('static', filename=f'qr/{username}.png')
        
        app.logger.info(f"Profile accessed for user: {username}")
        try:
            return render_template('profile.html', info=info, qr_code_url=qr_code_url, username=username)
        except:
            # Fallback HTML profile display if template is missing
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{info["name"]} - Medical Profile</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            </head>
            <body data-bs-theme="dark">
                <div class="container mt-5">
                    <div class="card">
                        <div class="card-header bg-danger text-white text-center">
                            <h1>{info["name"]}</h1>
                            <p>Emergency Medical Information</p>
                        </div>
                        <div class="card-body">
                            {f'<div class="alert alert-danger"><strong>Blood Type:</strong> {info["blood_type"]}</div>' if info["blood_type"] else ''}
                            {f'<div class="alert alert-success"><strong>Emergency Contact:</strong> {info["emergency_contact"]}</div>' if info["emergency_contact"] else ''}
                            {f'<div class="alert alert-warning"><strong>Allergies:</strong> {info["allergy"]}</div>' if info["allergy"] else ''}
                            {f'<div class="alert alert-info"><strong>Medical Conditions:</strong> {info["condition"]}</div>' if info["condition"] else ''}
                            {f'<div class="alert alert-secondary"><strong>Last Checkup:</strong> {info["last_checkup_date"]}<br>{info["last_checkup_details"]}</div>' if info["last_checkup_date"] or info["last_checkup_details"] else ''}
                            {f'<div class="alert alert-primary"><strong>Doctor Notes:</strong> {info["doctor_notes"]}</div>' if info["doctor_notes"] else ''}
                        </div>
                    </div>
                    <div class="text-center mt-3">
                        <a href="/" class="btn btn-primary">Create New Profile</a>
                        <a href="/edit/{username}" class="btn btn-secondary">Update Checkup</a>
                    </div>
                </div>
            </body>
            </html>
            '''
        
    except Exception as e:
        app.logger.error(f"Error loading profile for {username}: {str(e)}")
        return render_template('not_found.html', username=username, error="Profile data corrupted"), 500

@app.route('/edit/<username>', methods=['GET', 'POST'])
def edit_checkup(username):
    """Doctor edit form for updating checkup information"""
    try:
        profile = MedicalProfile.query.filter_by(username=username).first()
        
        if not profile:
            return render_template('not_found.html', username=username), 404
        
        if request.method == 'POST':
            # Parse checkup date
            checkup_date_str = request.form.get('last_checkup_date', '')
            checkup_date = None
            if checkup_date_str:
                try:
                    checkup_date = datetime.strptime(checkup_date_str, '%Y-%m-%d').date()
                except ValueError:
                    checkup_date = None
            
            # Update checkup fields
            profile.last_checkup_date = checkup_date
            profile.last_checkup_details = request.form.get('last_checkup_details', '').strip()
            
            # Update doctor notes if provided
            doctor_notes = request.form.get('doctor_notes', '').strip()
            if doctor_notes:
                profile.doctor_notes = doctor_notes
            
            try:
                # Save updated data
                db.session.commit()
                
                app.logger.info(f"Checkup updated for user: {username}")
                return redirect(url_for('view_profile', username=username))
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating checkup for {username}: {str(e)}")
                try:
                    return render_template('edit_checkup.html', username=username,
                                         info=profile, error="Failed to update checkup information")
                except:
                    # Fallback response for update error
                    return f'''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Update Error</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
                    </head>
                    <body data-bs-theme="dark">
                        <div class="container mt-5">
                            <div class="alert alert-danger">
                                <h4>Update Failed</h4>
                                <p>Failed to update checkup information. Please try again.</p>
                                <a href="/profile/{username}" class="btn btn-primary">Back to Profile</a>
                                <a href="/edit/{username}" class="btn btn-secondary">Try Again</a>
                            </div>
                        </div>
                    </body>
                    </html>
                    '''
        
        # GET request - show edit form
        try:
            return render_template('edit_checkup.html', username=username, info=profile)
        except:
            # Fallback HTML for edit checkup form if template is missing
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Update Medical Checkup - {profile.name}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            </head>
            <body data-bs-theme="dark">
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-lg-8">
                            <div class="card">
                                <div class="card-header bg-info text-white text-center py-4">
                                    <h2>Update Medical Checkup</h2>
                                    <p class="mb-0">Patient: {profile.name}</p>
                                </div>
                                <div class="card-body p-4">
                                    <form method="POST" action="/edit/{username}">
                                        <div class="row mb-3">
                                            <div class="col-md-6">
                                                <label for="last_checkup_date" class="form-label">Last Checkup Date</label>
                                                <input type="date" class="form-control" id="last_checkup_date" name="last_checkup_date"
                                                       value="{profile.last_checkup_date or ''}">
                                            </div>
                                            <div class="col-md-6">
                                                <label for="blood_type" class="form-label">Blood Type</label>
                                                <select class="form-select" id="blood_type" name="blood_type">
                                                    <option value="">Select Blood Type</option>
                                                    {''.join([f'<option value="{bt}" {"selected" if profile.blood_type == bt else ""}>{bt}</option>' for bt in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]])}
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label for="last_checkup_details" class="form-label">Checkup Details</label>
                                            <textarea class="form-control" id="last_checkup_details" name="last_checkup_details" rows="4">{profile.last_checkup_details or ''}</textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label for="doctor_notes" class="form-label">Doctor Notes</label>
                                            <textarea class="form-control" id="doctor_notes" name="doctor_notes" rows="4">{profile.doctor_notes or ''}</textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label for="allergy" class="form-label">Allergies</label>
                                            <textarea class="form-control" id="allergy" name="allergy" rows="3">{profile.allergy or ''}</textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label for="condition" class="form-label">Medical Conditions</label>
                                            <textarea class="form-control" id="condition" name="condition" rows="3">{profile.condition or ''}</textarea>
                                        </div>
                                        <div class="text-center">
                                            <button type="submit" class="btn btn-success btn-lg">Update Medical Information</button>
                                            <a href="/profile/{username}" class="btn btn-secondary btn-lg ms-2">Cancel</a>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
        
    except Exception as e:
        app.logger.error(f"Error loading profile for edit: {str(e)}")
        # Fallback error page
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Profile Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        </head>
        <body data-bs-theme="dark">
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="text-danger">Profile Not Found</h1>
                    <p>The profile for username "{username}" could not be found.</p>
                    <a href="/" class="btn btn-primary">Create New Profile</a>
                </div>
            </div>
        </body>
        </html>
        ''', 404


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    try:
        return render_template('not_found.html'), 404
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        </head>
        <body data-bs-theme="dark">
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="text-danger">404 - Page Not Found</h1>
                    <p>The requested page could not be found.</p>
                    <a href="/" class="btn btn-primary">Create New Profile</a>
                </div>
            </div>
        </body>
        </html>
        ''', 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Internal server error: {str(error)}")
    try:
        return render_template('not_found.html', error="Internal server error"), 500
    except:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Server Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        </head>
        <body data-bs-theme="dark">
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="text-danger">500 - Internal Server Error</h1>
                    <p>An internal server error occurred. Please try again later.</p>
                    <a href="/" class="btn btn-primary">Create New Profile</a>
                </div>
            </div>
        </body>
        </html>
        ''', 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
