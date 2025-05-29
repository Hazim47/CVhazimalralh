from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.cloud_services import File, Database, CalculatorHistory
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's resources
    files = File.query.filter_by(user_id=current_user.id).order_by(File.uploaded_at.desc()).limit(5).all()
    databases = Database.query.filter_by(user_id=current_user.id).order_by(Database.created_at.desc()).limit(5).all()
    calculations = CalculatorHistory.query.filter_by(user_id=current_user.id).order_by(CalculatorHistory.created_at.desc()).limit(5).all()
    
    # Calculate total storage used
    total_storage = sum(file.file_size for file in files)
    
    return render_template('main/dashboard.html',
                         files=files,
                         databases=databases,
                         calculations=calculations,
                         total_storage=total_storage)

@main_bp.route('/developers')
def developers():
    return render_template('main/developers.html') 