"""Authentication views for WorkFrame."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user


def create_auth_blueprint(app):
    """Create authentication blueprint with access to WorkFrame app instance."""
    
    auth = Blueprint('auth', __name__)
    
    @auth.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and handler."""
        # Redirect if already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            if not username or not password:
                flash('Please enter both username and password.', 'danger')
                return render_template('auth/login.html')
            
            # Find user by username or email
            user = app.User.query.filter(
                (app.User.username == username) | (app.User.email == username)
            ).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash('Your account has been disabled. Please contact an administrator.', 'danger')
                    return render_template('auth/login.html')
                
                # Log the user in
                login_user(user, remember=remember)
                user.update_last_login()
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        
        return render_template('auth/login.html')
    
    @auth.route('/logout')
    @login_required
    def logout():
        """Logout handler."""
        user_name = current_user.full_name
        logout_user()
        flash(f'Goodbye, {user_name}!', 'info')
        return redirect(url_for('auth.login'))
    
    @auth.route('/profile')
    @login_required
    def profile():
        """User profile page."""
        return render_template('auth/profile.html', user=current_user)
    
    @auth.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """Edit user profile page."""
        # Use the existing User model from the app instead of recreating it
        User = app.User
        
        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validate email is provided
            if not email:
                flash('Email is required.', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('This email is already in use by another account.', 'danger')
                return render_template('auth/edit_profile.html', user=current_user)
            
            # Update user profile
            current_user.first_name = first_name or None
            current_user.last_name = last_name or None
            current_user.email = email
            
            app.db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        return render_template('auth/edit_profile.html', user=current_user)
    
    @auth.route('/profile/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        """Change user password page."""
        if request.method == 'POST':
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate new password
            if len(new_password) < 3:
                flash('Password must be at least 3 characters long.', 'danger')
                return render_template('auth/change_password.html')
            
            # Validate password confirmation
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('auth/change_password.html')
            
            # Update password
            current_user.set_password(new_password)
            app.db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        
        return render_template('auth/change_password.html')
    
    return auth


def login_required_decorator(f):
    """Decorator for views that require login."""
    return login_required(f)


def admin_required(f):
    """Decorator for views that require admin privileges."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function