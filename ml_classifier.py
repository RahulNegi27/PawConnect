import pickle
import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import re

class FileClassifier:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.ext_encoder = LabelEncoder()
        self.categories = [
            'Images', 'Documents', 'Audio', 'Videos', 
            'Archives', 'Applications', 'Misc'
        ]
        self.model_path = 'file_classifier_model.pkl'
        
        self.category_extensions = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.csv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'Applications': ['.exe', '.app', '.apk', '.deb', '.rpm', '.dmg', '.msi', '.jar'],
        }
        
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_model()
    
    def generate_training_data(self):
        training_data = []
        
        for category, extensions in self.category_extensions.items():
            for ext in extensions:
                for size_range in ['small', 'medium', 'large']:
                    if size_range == 'small':
                        size = np.random.randint(1, 1024)
                    elif size_range == 'medium':
                        size = np.random.randint(1024, 1024*1024)
                    else:
                        size = np.random.randint(1024*1024, 100*1024*1024)
                    
                    name_patterns = [
                        f'file{np.random.randint(1,100)}{ext}',
                        f'document_{np.random.randint(1,100)}{ext}',
                        f'image{np.random.randint(1,100)}{ext}',
                        f'video_{np.random.randint(1,100)}{ext}',
                    ]
                    
                    for name in name_patterns[:2]:
                        training_data.append({
                            'extension': ext,
                            'size': size,
                            'name_length': len(name),
                            'has_underscore': 1 if '_' in name else 0,
                            'has_number': 1 if any(c.isdigit() for c in name) else 0,
                            'category': category
                        })
        
        misc_extensions = ['.tmp', '.log', '.dat', '.bin', '.cfg', '.ini', '.sys', '.bak']
        for ext in misc_extensions:
            for _ in range(5):
                training_data.append({
                    'extension': ext,
                    'size': np.random.randint(100, 10000),
                    'name_length': np.random.randint(5, 20),
                    'has_underscore': np.random.randint(0, 2),
                    'has_number': np.random.randint(0, 2),
                    'category': 'Misc'
                })
        
        return pd.DataFrame(training_data)
    
    def train_model(self):
        df = self.generate_training_data()
        
        self.ext_encoder.fit(df['extension'])
        df['extension_encoded'] = self.ext_encoder.transform(df['extension'])
        
        self.label_encoder.fit(df['category'])
        
        X = df[['extension_encoded', 'size', 'name_length', 'has_underscore', 'has_number']]
        y = self.label_encoder.transform(df['category'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = DecisionTreeClassifier(max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        
        accuracy = self.model.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.2%}")
        
        self.save_model()
    
    def save_model(self):
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'ext_encoder': self.ext_encoder
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
            self.model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            self.ext_encoder = model_data['ext_encoder']
    
    def extract_features(self, file_info):
        name = file_info.get('name', '')
        size = file_info.get('size', 0)
        extension = os.path.splitext(name)[1].lower()
        
        if extension not in self.ext_encoder.classes_:
            extension = '.tmp'
        
        features = {
            'extension_encoded': self.ext_encoder.transform([extension])[0],
            'size': size,
            'name_length': len(name),
            'has_underscore': 1 if '_' in name else 0,
            'has_number': 1 if any(c.isdigit() for c in name) else 0
        }
        
        return features
    
    def predict_file(self, file_info):
        features = self.extract_features(file_info)
        X = np.array([[
            features['extension_encoded'],
            features['size'],
            features['name_length'],
            features['has_underscore'],
            features['has_number']
        ]])
        
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = float(probabilities[prediction])
        
        category = self.label_encoder.inverse_transform([prediction])[0]
        
        return {
            'category': category,
            'confidence': confidence,
            'all_probabilities': {
                self.label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(probabilities)
            }
        }
