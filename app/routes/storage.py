import os
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.cloud_services import File
from datetime import datetime

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/storage')
@login_required
def index():
    files = File.query.filter_by(user_id=current_user.id).order_by(File.uploaded_at.desc()).all()
    return render_template('storage/index.html', files=files)

@storage_bp.route('/storage/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('storage.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('storage.index'))
    
    if file:
        filename = secure_filename(file.filename)
        # Create unique filename
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        # Create user's upload directory if it doesn't exist
        user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_upload_dir, unique_filename)
        file.save(file_path)
        
        # Create database record
        new_file = File(
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_type=file.content_type,
            user_id=current_user.id
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        flash('File uploaded successfully', 'success')
    
    return redirect(url_for('storage.index'))

@storage_bp.route('/storage/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    return send_file(file.file_path, as_attachment=True, download_name=file.original_filename)

@storage_bp.route('/storage/delete/<int:file_id>', methods=['POST'])
@login_required
def delete(file_id):
    file = File.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    
    # Delete physical file
    try:
        os.remove(file.file_path)
    except OSError:
        pass  # File might not exist
    
    # Delete database record
    db.session.delete(file)
    db.session.commit()
    
    flash('File deleted successfully', 'success')
    return redirect(url_for('storage.index')) 