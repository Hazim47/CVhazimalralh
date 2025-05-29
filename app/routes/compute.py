import ast
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.cloud_services import CalculatorHistory
from datetime import datetime

compute_bp = Blueprint('compute', __name__)

@compute_bp.route('/compute')
@login_required
def index():
    calculations = CalculatorHistory.query.filter_by(user_id=current_user.id).order_by(CalculatorHistory.created_at.desc()).all()
    return render_template('compute/index.html', calculations=calculations)

@compute_bp.route('/compute/calculate', methods=['POST'])
@login_required
def calculate():
    expression = request.form.get('expression')
    
    if not expression:
        return jsonify({'error': 'Expression is required'}), 400
    
    try:
        # Evaluate the expression safely
        result = str(eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round}))
        
        # Save calculation to history
        calculation = CalculatorHistory(
            expression=expression,
            result=result,
            user_id=current_user.id
        )
        db.session.add(calculation)
        db.session.commit()
        
        return jsonify({
            'expression': expression,
            'result': result,
            'timestamp': calculation.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@compute_bp.route('/compute/<int:calc_id>/delete', methods=['POST'])
@login_required
def delete(calc_id):
    calculation = CalculatorHistory.query.filter_by(id=calc_id, user_id=current_user.id).first_or_404()
    db.session.delete(calculation)
    db.session.commit()
    
    flash('Calculation deleted successfully', 'success')
    return redirect(url_for('compute.index')) 