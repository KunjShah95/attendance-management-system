# Architecture Documentation

## System Architecture Overview

This document provides a detailed explanation of the Attendance Management System architecture.

## Viewing the Architecture Diagram

### Method 1: GitHub (Recommended)
Simply view the README.md file on GitHub. GitHub natively supports Mermaid diagrams and will render them automatically.

### Method 2: Local HTML File
Open `architecture.html` in your web browser to view an interactive, styled version of the architecture diagram.

**Windows:**
```cmd
start architecture.html
```

**macOS:**
```bash
open architecture.html
```

**Linux:**
```bash
xdg-open architecture.html
```

### Method 3: Mermaid Live Editor
1. Go to [https://mermaid.live/](https://mermaid.live/)
2. Copy the Mermaid code from the README.md
3. Paste it into the editor
4. View and export the diagram

### Method 4: VS Code Extension
1. Install the "Markdown Preview Mermaid Support" extension in VS Code
2. Open README.md
3. Click the preview button (Ctrl+Shift+V)
4. The diagram will render in the preview pane

## Architecture Components

### 1. Input Layer 📹
The input layer consists of two primary sources:

**Webcam/Camera Feed**
- Real-time video capture for live attendance marking
- Uses OpenCV's VideoCapture API
- Supports multiple camera indices (0, 1, 2, etc.)
- Resolution: Recommended 720p or higher

**Dataset Images**
- Organized in `dataset/` directory
- One subdirectory per student
- Contains training images for face recognition
- Supports JPG, JPEG, PNG formats

### 2. Processing Layer ⚙️
This layer handles all computer vision and machine learning operations:

**Haar Cascade Face Detector**
- Uses OpenCV's pre-trained frontal face cascade
- Detects faces in images and video frames
- Returns bounding box coordinates (x, y, width, height)
- Fast and efficient for real-time processing

**LBPH Trainer (train.py)**
- Trains the Local Binary Patterns Histograms face recognizer
- Processes detected faces from dataset images
- Generates the trained model file
- Creates ID-to-name label mappings

**LBPH Recognizer (attendance_runner.py)**
- Loads the trained model
- Predicts identity of detected faces
- Returns label ID and confidence score
- Marks attendance for recognized faces

### 3. Model Layer 🤖
Stores the trained machine learning models:

**trainer.yml**
- Binary file containing LBPH model data
- Generated during training phase
- Used during recognition phase
- Size varies based on training dataset

**labels.pickle**
- Python pickle file
- Maps numeric IDs to student names
- Format: {1: 'john_doe', 2: 'jane_smith', ...}
- Used for label lookup during recognition

### 4. Data Layer 💾
Persistent storage for application data:

**attendance.db (SQLite Database)**
- Stores all attendance records
- Schema: (id, name, date, time)
- Prevents duplicate entries per student per day
- Lightweight and serverless

**students.csv (Student Roster)**
- CSV file with student information
- Columns: id, name, email
- Used for email notifications
- Easy to edit and maintain

**smtp_config.json (Email Configuration)**
- SMTP server settings
- Credentials for email notifications
- Optional: can use environment variables instead
- Should be git-ignored for security

### 5. Interface Layer 🖥️
User-facing applications:

**Streamlit Dashboard (streamlit_app.py)**
- Web-based admin interface
- Features:
  - View attendance records
  - Generate reports
  - Send email notifications
  - Configure settings
  - Diagnostic tools
- Runs on port 8501 by default

**Flask REST API (app.py)**
- RESTful API endpoints
- Endpoints:
  - GET /api/attendance
  - GET /api/students
  - POST /api/send_absent_emails
  - GET /api/export_csv
- Runs on port 5000 by default
- CORS enabled for cross-origin requests

### 6. Utility Layer 🔧
Shared helper functions:

**utils.py**
- Database operations (CRUD)
- CSV file parsing
- Email sending functionality
- Label management
- Directory management
- Common utilities used across all components

## Data Flow Paths

### Training Flow
```
Dataset Images → Haar Cascade Detection → Face Extraction → LBPH Training → Model Generation
```

1. Images loaded from `dataset/` subdirectories
2. Haar Cascade detects faces in each image
3. Detected faces are extracted and labeled
4. LBPH algorithm trains on face samples
5. Model saved to `trainer.yml`
6. Label mapping saved to `labels.pickle`

### Recognition Flow
```
Camera Feed → Face Detection → Face Recognition → Confidence Check → Attendance Marking
```

1. Camera captures video frames continuously
2. Haar Cascade detects faces in each frame
3. LBPH recognizer predicts identity
4. Confidence score compared to threshold
5. If match found, attendance marked in database
6. Visual feedback displayed on screen

### Management Flow
```
User Request → API/UI → Database Query → Data Processing → Response
```

1. User accesses Streamlit UI or makes API call
2. Request processed by appropriate handler
3. Database queried for relevant data
4. Data formatted and processed
5. Response sent back to user
6. UI updated or API response returned

## Component Interactions

### Training Dependencies
- **train.py** requires:
  - Dataset images in proper structure
  - OpenCV with face module
  - Write access to model directory

### Recognition Dependencies
- **attendance_runner.py** requires:
  - Trained model files (trainer.yml, labels.pickle)
  - Working camera/webcam
  - Database file (created if not exists)
  - OpenCV with face module

### UI Dependencies
- **streamlit_app.py** requires:
  - Database file
  - students.csv file
  - Optional: smtp_config.json for emails
  - streamlit_utils.py

### API Dependencies
- **app.py** requires:
  - Database file
  - students.csv file
  - utils.py
  - Flask and dependencies

## Security Considerations

### Data Privacy
- Facial data is sensitive biometric information
- Ensure compliance with privacy regulations (GDPR, CCPA)
- Obtain explicit consent before collection
- Implement data retention policies

### Credential Security
- Never commit smtp_config.json with real credentials
- Use environment variables in production
- Implement proper access controls
- Use secure SMTP connections (TLS)

### Database Security
- SQLite is file-based (file permissions important)
- Consider encryption for production use
- Regular backups recommended
- Access control at OS level

## Scalability Considerations

### Current Limitations
- Single-threaded recognition
- Local file-based database
- No distributed processing
- Single camera support

### Future Improvements
- Multi-camera support
- Database migration to PostgreSQL/MySQL
- Distributed recognition nodes
- Load balancing for API
- Redis caching layer
- Message queue for async processing

## Technology Choices

### Why LBPH?
- Fast and efficient
- Works well with small datasets
- No GPU required
- Good for real-time processing
- Easy to train and deploy

### Why SQLite?
- Serverless (no setup required)
- Single file database
- Perfect for small-medium scale
- Built into Python
- Easy backup and portability

### Why Streamlit?
- Rapid development
- Python-native
- Beautiful UI out of the box
- Easy deployment
- Great for admin dashboards

### Why Flask?
- Lightweight and flexible
- Easy to understand
- Perfect for small APIs
- Extensive ecosystem
- Production-ready with proper deployment

## Monitoring and Debugging

### Logging
- Enable debug mode for detailed logs
- Log file locations configurable
- Streamlit logs to console and file
- Flask logs to console

### Performance Metrics
- Recognition speed (FPS)
- Database query times
- API response times
- Memory usage
- CPU usage

### Health Checks
- Camera availability
- Model file integrity
- Database connectivity
- SMTP server reachability
- Disk space

## Deployment Architecture

### Development
```
Local Machine → Python Virtual Environment → Application Components
```

### Production (Recommended)
```
                          ┌─────────────────┐
                          │  Load Balancer  │
                          └────────┬────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
            ┌──────────────┐              ┌──────────────┐
            │  Flask API   │              │  Streamlit   │
            │  (Gunicorn)  │              │   (Docker)   │
            └──────┬───────┘              └──────┬───────┘
                   │                             │
                   └──────────┬──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  PostgreSQL DB   │
                    └──────────────────┘
```

### Cloud Deployment Options
- **AWS**: EC2 + RDS + S3
- **Azure**: App Service + Azure SQL
- **GCP**: Cloud Run + Cloud SQL
- **Heroku**: Web + Postgres addon
- **DigitalOcean**: Droplets + Managed DB

## Troubleshooting Architecture Issues

### Issue: Diagram Not Showing on GitHub
**Solution:**
1. Ensure Mermaid syntax is correct
2. Check for proper code block formatting
3. Try viewing on GitHub's main site (not mobile)
4. Use alternative viewing methods

### Issue: Component Communication Failure
**Solution:**
1. Check all services are running
2. Verify port configurations
3. Check firewall settings
4. Review logs for errors

### Issue: Performance Degradation
**Solution:**
1. Monitor resource usage
2. Check database size and optimize
3. Review recognition threshold
4. Consider caching strategies

## Further Reading

- [OpenCV Documentation](https://docs.opencv.org/)
- [LBPH Algorithm](https://towardsdatascience.com/face-recognition-how-lbph-works-90ec258c3d6b)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Mermaid Documentation](https://mermaid.js.org/)

---

**Last Updated:** October 6, 2025  
**Author:** Kunj Shah  
**Repository:** [attendance-management-system](https://github.com/KunjShah95/attendance-management-system)
