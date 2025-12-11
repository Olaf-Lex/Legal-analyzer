from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
from werkzeug.utils import secure_filename
import PyPDF2
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file stream"""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text[:4000]  # Limit to first 4000 chars for demo
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def analyze_nda_text(text):
    """
    REAL RAG ANALYSIS WOULD GO HERE
    For now, this is a deterministic risk analyzer
    """
    risks = []
    risk_score = 0
    
    # Risk detection logic (replace with your RAG later)
    if "10 years" in text.lower() or "ten years" in text.lower():
        risks.append({
            "level": "high",
            "title": "Unilateral Confidentiality",
            "text": "Long confidentiality period detected",
            "suggestion": "Negotiate mutual obligations or reduce term to 3-5 years"
        })
        risk_score += 30
    
    if "public domain" in text.lower():
        risks.append({
            "level": "medium",
            "title": "No Carve-outs for Public Domain",
            "text": "Missing specific carve-outs",
            "suggestion": "Add carve-outs for independently developed information"
        })
        risk_score += 20
    
    if "irreparable harm" in text.lower():
        risks.append({
            "level": "high",
            "title": "Overbroad Injunctive Relief",
            "text": "Standard overreach clause",
            "suggestion": "Limit to actual damages where appropriate"
        })
        risk_score += 25
    
    # Default risk score if no issues found
    if not risks:
        risk_score = 15
    
    return {
        "overall_score": min(risk_score, 100),
        "risks": risks,
        "analysis_time": "1.8s",  # Would be real in production
        "document_length": len(text)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF and DOCX allowed'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        file.save(filepath)
        
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            with open(filepath, 'rb') as f:
                text = extract_text_from_pdf(f)
        else:
            # For DOCX, you'd need python-docx library
            text = "DOCX support coming soon. Use PDF for demo."
        
        # Analyze text
        analysis = analyze_nda_text(text)
        
        # Clean up file after analysis
        os.remove(filepath)
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'legaltech-portfolio'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
