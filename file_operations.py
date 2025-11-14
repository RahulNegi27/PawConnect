import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class FileManager:
    def __init__(self):
        self.log_file = 'operation_logs.json'
        self.logs = self.load_logs()
        self.valid_categories = {
            'Images', 'Documents', 'Audio', 'Videos', 
            'Archives', 'Applications', 'Misc'
        }
    
    def load_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def add_log(self, action, file_path, category=None, confidence=None, status='success'):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'file_path': file_path,
            'category': category,
            'confidence': confidence,
            'status': status
        }
        self.logs.append(log_entry)
        self.save_logs()
        return log_entry
    
    def get_recent_logs(self, limit=50):
        return self.logs[-limit:]
    
    def scan_directory(self, directory_path):
        files_data = []
        
        try:
            items = os.listdir(directory_path)
            
            for item in items:
                full_path = os.path.join(directory_path, item)
                
                try:
                    if os.path.isfile(full_path):
                        stat = os.stat(full_path)
                        
                        file_info = {
                            'name': item,
                            'path': full_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'extension': os.path.splitext(item)[1].lower(),
                            'type': 'file'
                        }
                        files_data.append(file_info)
                except (PermissionError, OSError):
                    continue
        except PermissionError:
            raise PermissionError(f"Cannot access directory: {directory_path}")
        
        files_data.sort(key=lambda x: x['name'].lower())
        return files_data
    
    def organize_directory(self, directory_path, classifier, confidence_threshold=0.7):
        files_data = self.scan_directory(directory_path)
        results = {
            'total_files': len(files_data),
            'organized': 0,
            'skipped': 0,
            'errors': 0,
            'details': []
        }
        
        for file_info in files_data:
            try:
                prediction = classifier.predict_file(file_info)
                
                if prediction['confidence'] >= confidence_threshold:
                    category = prediction['category']
                    
                    if category not in self.valid_categories:
                        raise ValueError(f"Invalid category: {category}")
                    
                    category_dir = os.path.join(directory_path, category)
                    
                    if not os.path.exists(category_dir):
                        os.makedirs(category_dir)
                    
                    source_path = file_info['path']
                    dest_path = os.path.join(category_dir, file_info['name'])
                    
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(file_info['name'])
                        counter = 1
                        while os.path.exists(dest_path):
                            new_name = f"{base}_{counter}{ext}"
                            dest_path = os.path.join(category_dir, new_name)
                            counter += 1
                    
                    shutil.move(source_path, dest_path)
                    
                    self.add_log(
                        action='organize',
                        file_path=source_path,
                        category=category,
                        confidence=prediction['confidence'],
                        status='success'
                    )
                    
                    results['organized'] += 1
                    results['details'].append({
                        'file': file_info['name'],
                        'category': category,
                        'confidence': prediction['confidence'],
                        'status': 'organized'
                    })
                else:
                    results['skipped'] += 1
                    results['details'].append({
                        'file': file_info['name'],
                        'category': prediction['category'],
                        'confidence': prediction['confidence'],
                        'status': 'skipped_low_confidence'
                    })
            except Exception as e:
                results['errors'] += 1
                results['details'].append({
                    'file': file_info['name'],
                    'status': 'error',
                    'error': str(e)
                })
                self.add_log(
                    action='organize',
                    file_path=file_info['path'],
                    status='error'
                )
        
        return results
    
    def organize_single_file(self, file_path, classifier, target_category=None, confidence_threshold=0.7):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_info = {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': os.path.getsize(file_path)
        }
        
        prediction = classifier.predict_file(file_info)
        category = target_category if target_category else prediction['category']
        
        if category not in self.valid_categories:
            raise ValueError(f"Invalid category: {category}")
        
        if not target_category and prediction['confidence'] < confidence_threshold:
            return {
                'status': 'skipped',
                'reason': 'Low confidence',
                'confidence': prediction['confidence'],
                'predicted_category': prediction['category']
            }
        
        directory = os.path.dirname(file_path)
        category_dir = os.path.join(directory, category)
        
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        dest_path = os.path.join(category_dir, file_info['name'])
        
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(file_info['name'])
            counter = 1
            while os.path.exists(dest_path):
                new_name = f"{base}_{counter}{ext}"
                dest_path = os.path.join(category_dir, new_name)
                counter += 1
        
        shutil.move(file_path, dest_path)
        
        self.add_log(
            action='organize_single',
            file_path=file_path,
            category=category,
            confidence=prediction['confidence'],
            status='success'
        )
        
        return {
            'status': 'success',
            'category': category,
            'confidence': prediction['confidence'],
            'new_path': dest_path
        }
