# Smart File Organizer - ML Powered

## Overview
An intelligent file management system that uses Machine Learning (Decision Tree Classifier) to automatically categorize and organize files. The application features a modern web interface with creative animations and provides educational insights into file classification using OS concepts and ML techniques.

## Project Status
- **Date Created**: October 14, 2025
- **Current State**: Fully functional MVP completed
- **Tech Stack**: Python Flask backend + Vanilla JavaScript frontend

## Features Implemented
1. **File System Operations**
   - Browse directories and view file metadata
   - Real-time file scanning with size, extension, and modification date
   - Permission handling and error management

2. **Machine Learning Classification**
   - Decision Tree Classifier trained on file attributes
   - Categories: Images, Documents, Audio, Videos, Archives, Applications, Misc
   - Feature extraction: extension, size, name patterns, special characters
   - Confidence scoring for prediction reliability

3. **Smart Organization**
   - "Organize All" batch processing with ML predictions
   - Individual file prediction and organization
   - Confidence threshold control (50-95%)
   - Automatic folder creation for categories
   - Duplicate file handling with auto-renaming

4. **Operation Logging**
   - JSON-based logging system
   - Tracks all file movements and classifications
   - Confidence scores and timestamps
   - View logs through UI dialog

5. **Modern UI/UX**
   - Dark theme with gradient accents
   - Creative animated dialog boxes
   - Toast notifications for feedback
   - Smooth transitions and hover effects
   - Responsive design for all screen sizes

## Architecture

### Backend (Python)
- **app.py**: Flask application with REST API endpoints
- **ml_classifier.py**: Decision Tree model training and prediction
- **file_operations.py**: File system operations and logging

### Frontend (JavaScript/HTML/CSS)
- **templates/index.html**: Main application structure
- **static/css/styles.css**: Modern dark theme with animations
- **static/js/app.js**: Client-side logic and API communication

### API Endpoints
- `GET /` - Main application page
- `POST /api/browse` - Browse directory and list files
- `POST /api/predict` - Get ML prediction for a file
- `POST /api/organize-all` - Organize all files in directory
- `POST /api/organize-file` - Organize single file
- `GET /api/logs` - Retrieve operation logs
- `GET /api/current-directory` - Get current working directory

## Machine Learning Details

### Model: Decision Tree Classifier
- **Algorithm**: scikit-learn DecisionTreeClassifier
- **Max Depth**: 10
- **Training Accuracy**: ~70%
- **Features Used**:
  1. File extension (encoded)
  2. File size (bytes)
  3. Name length
  4. Has underscore (boolean)
  5. Has number (boolean)

### Category Mapping
- **Images**: jpg, jpeg, png, gif, bmp, svg, webp, ico, tiff
- **Documents**: pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv
- **Audio**: mp3, wav, flac, aac, ogg, m4a, wma
- **Videos**: mp4, avi, mkv, mov, wmv, flv, webm, m4v
- **Archives**: zip, rar, 7z, tar, gz, bz2, xz
- **Applications**: exe, app, apk, deb, rpm, dmg, msi, jar
- **Misc**: Other files (tmp, log, dat, bin, cfg, ini, sys, bak)

## How to Use

1. **Enter Directory Path**: Type or paste the full path to a directory
2. **Browse**: Click "Browse" to load files from the directory
3. **Predict Individual Files**: Click "Predict" on any file to see ML classification
4. **Organize All**: Use "Organize All" to batch process all files
5. **Adjust Confidence**: Use slider to set minimum confidence threshold (default 70%)
6. **View Logs**: Check operation history and confidence scores

## File Organization Process

1. ML model analyzes file attributes
2. Predicts category with confidence score
3. If confidence ≥ threshold:
   - Creates category folder (if needed)
   - Moves file to category folder
   - Logs operation with confidence score
4. If confidence < threshold:
   - Skips file
   - Logs as "low confidence"

## Educational Value

This project demonstrates:
- **OS Concepts**: File I/O, metadata, permissions, directory operations
- **Machine Learning**: Feature extraction, classification, confidence scoring
- **Web Development**: REST APIs, async operations, modern UI/UX
- **Software Architecture**: Layered design, separation of concerns
- **Data Management**: Logging, error handling, data persistence

## Recent Changes
- 2025-10-14: Complete implementation with production-ready security
- ML model trained with ~70% accuracy, saved as pickle file
- Modern UI with creative dialog animations and smooth transitions
- Operation logging system with detailed confidence tracking
- Confidence threshold control (50-95%, default 70%)
- **Security Implementation (Production-Ready)**:
  - Path validation using Path.resolve() + relative_to() for workspace confinement
  - All file paths validated to prevent directory traversal attacks
  - Category whitelist validation prevents malicious destination paths
  - Symlink traversal blocked via realpath resolution
  - All operations strictly confined to WORKSPACE_ROOT
  - Architect-verified security implementation

## User Preferences
None specified yet.

## Technical Notes
- Model is saved as `file_classifier_model.pkl` and reloaded on startup
- Logs stored in `operation_logs.json`
- Server runs on port 5000 (required for Replit environment)
- Uses Flask development server (suitable for educational/demo purposes)
