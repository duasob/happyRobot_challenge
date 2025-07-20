from flask import Blueprint, render_template, jsonify, request
from database import db_manager
import sys
import os

# Add the parent directory to the path so we can import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

carriers_bp = Blueprint('carriers', __name__)

@carriers_bp.route('/')
def carriers_dashboard():
    """Serve the main carriers dashboard HTML page"""
    return render_template('carriers.html')

@carriers_bp.route('/api/carriers')
def get_carriers():
    """API endpoint to get all carriers as JSON"""
    try:
        carriers = db_manager.get_all_carriers()
        return jsonify({
            'success': True,
            'carriers': carriers,
            'count': len(carriers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'carriers': []
        }), 500

@carriers_bp.route('/api/carriers/<load_id>')
def get_carrier(load_id):
    """API endpoint to get a specific carrier by load_id"""
    try:
        carrier = db_manager.get_carrier_by_id(load_id)
        if carrier:
            return jsonify({
                'success': True,
                'carrier': carrier
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Carrier not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@carriers_bp.route('/api/carriers', methods=['POST'])
def add_carrier():
    """API endpoint to add a new carrier"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['load_id', 'origin', 'destination']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        success = db_manager.add_carrier(data)
        if success:
            return jsonify({
                'success': True,
                'message': 'Carrier added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add carrier'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@carriers_bp.route('/api/carriers/<load_id>', methods=['PUT'])
def update_carrier(load_id):
    """API endpoint to update an existing carrier"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success = db_manager.update_carrier(load_id, data)
        if success:
            return jsonify({
                'success': True,
                'message': 'Carrier updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update carrier'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@carriers_bp.route('/api/carriers/<load_id>', methods=['DELETE'])
def delete_carrier(load_id):
    """API endpoint to delete a carrier"""
    try:
        success = db_manager.delete_carrier(load_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Carrier deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete carrier'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 