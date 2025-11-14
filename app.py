from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
from pathlib import Path
import shutil
from ml_classifier import FileClassifier
from file_operations import FileManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')

WORKSPACE_ROOT = Path(os.getcwd()).resolve()

file_manager = FileManager()
classifier = FileClassifier()

def validate_path(path):
    """Validate that the path is within the workspace and safe to use."""
    try:
        resolved_path = Path(path).resolve()
        
        try:
            resolved_path.relative_to(WORKSPACE_ROOT)
        except ValueError:
            return None, "Access denied: Path is outside workspace"
        
        return str(resolved_path), None
    except Exception as e:
        return None, f"Invalid path: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/browse', methods=['POST'])
def browse_directory():
    try:
        data = request.json
        directory_path = data.get('path', os.getcwd())
        
        validated_path, error = validate_path(directory_path)
        if error:
            return jsonify({'error': error}), 403
        
        if not os.path.exists(validated_path):
            return jsonify({'error': 'Directory does not exist'}), 404
        
        if not os.path.isdir(validated_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        files_data = file_manager.scan_directory(validated_path)
        
        return jsonify({
            'success': True,
            'path': validated_path,
            'files': files_data
        })
    except PermissionError:
        return jsonify({'error': 'Permission denied to access this directory'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_category():
    try:
        data = request.json
        file_info = data.get('file')
        
        if not file_info:
            return jsonify({'error': 'No file information provided'}), 400
        
        prediction = classifier.predict_file(file_info)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organize-all', methods=['POST'])
def organize_all():
    try:
        data = request.json
        directory_path = data.get('path')
        confidence_threshold = data.get('threshold', 0.7)
        
        if not directory_path:
            return jsonify({'error': 'No directory path provided'}), 400
        
        validated_path, error = validate_path(directory_path)
        if error:
            return jsonify({'error': error}), 403
        
        if not os.path.exists(validated_path):
            return jsonify({'error': 'Invalid directory path'}), 400
        
        results = file_manager.organize_directory(
            validated_path, 
            classifier, 
            confidence_threshold
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/organize-file', methods=['POST'])
def organize_file():
    try:
        data = request.json
        file_path = data.get('file_path')
        target_category = data.get('category')
        confidence_threshold = data.get('threshold', 0.7)
        
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        validated_path, error = validate_path(file_path)
        if error:
            return jsonify({'error': error}), 403
        
        if not os.path.exists(validated_path):
            return jsonify({'error': 'Invalid file path'}), 400
        
        result = file_manager.organize_single_file(
            validated_path, 
            classifier, 
            target_category,
            confidence_threshold
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        logs = file_manager.get_recent_logs(limit=50)
        return jsonify({
            'success': True,
            'logs': logs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-directory', methods=['GET'])
def get_current_directory():
    try:
        current_dir = os.getcwd()
        return jsonify({
            'success': True,
            'path': current_dir
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
