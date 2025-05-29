import json
import sqlite3
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.cloud_services import Database
import os

database_bp = Blueprint('database', __name__)

@database_bp.route('/database')
@login_required
def index():
    databases = Database.query.filter_by(user_id=current_user.id).all()
    return render_template('database/index.html', databases=databases)

@database_bp.route('/database/create', methods=['POST'])
@login_required
def create():
    name = request.form.get('name')
    description = request.form.get('description')
    schema = request.form.get('schema')
    
    if not name:
        flash('Database name is required', 'danger')
        return redirect(url_for('database.index'))
    
    # Create database file
    db_path = os.path.join('instance', 'databases', str(current_user.id), f"{name}.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Parse and execute schema
        schema_data = json.loads(schema)
        for table in schema_data:
            create_table_sql = f"CREATE TABLE {table['name']} ({', '.join(table['columns'])})"
            cursor.execute(create_table_sql)
        
        conn.commit()
        
        # Create database record
        new_db = Database(
            name=name,
            description=description,
            schema=schema,
            user_id=current_user.id
        )
        
        db.session.add(new_db)
        db.session.commit()
        
        flash('Database created successfully', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error creating database: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('database.index'))

@database_bp.route('/database/<int:db_id>/query', methods=['POST'])
@login_required
def execute_query(db_id):
    database = Database.query.filter_by(id=db_id, user_id=current_user.id).first_or_404()
    query = request.form.get('query')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    db_path = os.path.join('instance', 'databases', str(current_user.id), f"{database.name}.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            # For SELECT queries, return results
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return jsonify({'results': results})
        else:
            # For other queries, commit changes
            conn.commit()
            return jsonify({'message': 'Query executed successfully'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@database_bp.route('/database/<int:db_id>/delete', methods=['POST'])
@login_required
def delete(db_id):
    database = Database.query.filter_by(id=db_id, user_id=current_user.id).first_or_404()
    
    # Delete database file
    db_path = os.path.join('instance', 'databases', str(current_user.id), f"{database.name}.db")
    try:
        os.remove(db_path)
    except OSError:
        pass  # File might not exist
    
    # Delete database record
    db.session.delete(database)
    db.session.commit()
    
    flash('Database deleted successfully', 'success')
    return redirect(url_for('database.index')) 