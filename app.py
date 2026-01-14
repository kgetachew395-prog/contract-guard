"""
Contract Guard - SIMPLE WORKING VERSION
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
API_KEY = os.getenv('GEMINI_API_KEY')  # Your key: AIzaSyAnNPIhYopvQUeZ6joxxmPIWi22a2VKPCo
PORT = 5000

print("\n" + "="*60)
print("🚀 STARTING CONTRACT GUARD BACKEND")
print("="*60)

# Initialize Gemini - SIMPLE WAY
try:
    print(f"🔑 API Key: {API_KEY[:20]}...")
    genai.configure(api_key=API_KEY)
    
    # Use the basic model that always works
    MODEL_NAME = "gemini-pro"  # This is the basic model that always exists
    
    print(f"🤖 Using model: {MODEL_NAME}")
    
    # Create the model
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Quick test
    test_response = model.generate_content("Say 'OK' if working")
    print(f"✅ Gemini test: {test_response.text}")
    
    print("🎉 Gemini AI initialized successfully!")
    gemini_ready = True
    
except Exception as e:
    print(f"❌ Gemini error: {str(e)[:100]}")
    print("⚠️  Using fallback mode (Gemini responses will be simulated)")
    gemini_ready = False
    model = None

print("="*60 + "\n")

# API endpoint to check health
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "gemini": gemini_ready,
        "message": "Contract Guard API"
    })

# API endpoint to test Gemini
@app.route('/api/test', methods=['GET'])
def test():
    if gemini_ready and model:
        try:
            response = model.generate_content("Say: 'Gemini AI is working with Contract Guard'")
            return jsonify({
                "success": True,
                "message": response.text,
                "model": MODEL_NAME
            })
        except:
            return jsonify({
                "success": False,
                "message": "Gemini test failed"
            })
    else:
        return jsonify({
            "success": False,
            "message": "Gemini not available"
        })

# Main analysis endpoint
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        contract_text = data.get('contract_text', '').strip()
        analysis_type = data.get('analysis_type', 'Important')
        
        if not contract_text:
            return jsonify({"error": "No contract text"}), 400
        
        print(f"📝 Analysis request: {analysis_type}, {len(contract_text)} chars")
        
        # If Gemini is ready, use it
        if gemini_ready and model:
            # Create prompt
            prompt = f"""
            Analyze this contract as a legal expert:
            
            CONTRACT TEXT:
            {contract_text[:3000]}
            
            ANALYSIS TYPE: {analysis_type}
            
            Provide:
            1. Key issues found
            2. Risks identified  
            3. Recommendations
            4. Action items
            
            Use bullet points and be concise.
            """
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            
            return jsonify({
                "status": "success",
                "analysis_type": analysis_type,
                "analysis": response.text,
                "model": MODEL_NAME,
                "length": len(contract_text)
            })
        
        # Fallback if Gemini not available
        else:
            fallback_response = f"""
            ⚠️ Gemini AI not available - Using Fallback Analysis
            
            Analysis Type: {analysis_type}
            Contract Length: {len(contract_text)} characters
            
            RECOMMENDED CHECKS:
            • Review payment terms and amounts
            • Check termination and renewal clauses
            • Verify liability and warranty sections
            • Examine confidentiality requirements
            • Confirm dispute resolution process
            
            NOTE: This is a simulated response. For real AI analysis, ensure Gemini API is configured.
            """
            
            return jsonify({
                "status": "fallback",
                "analysis_type": analysis_type,
                "analysis": fallback_response,
                "length": len(contract_text)
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home page
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contract Guard API</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #4361ee; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .endpoint { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Contract Guard API</h1>
            <p>AI-powered contract analysis backend</p>
            
            <div class="status """ + ("success" if gemini_ready else "error") + """">
                <strong>Gemini AI Status:</strong> """ + ("✅ Connected" if gemini_ready else "❌ Not Connected") + """
            </div>
            
            <h2>📡 API Endpoints:</h2>
            
            <div class="endpoint">
                <strong>GET</strong> <a href="/api/health">/api/health</a><br>
                Check API status
            </div>
            
            <div class="endpoint">
                <strong>GET</strong> <a href="/api/test">/api/test</a><br>
                Test Gemini connection
            </div>
            
            <div class="endpoint">
                <strong>POST</strong> /api/analyze<br>
                Analyze contract text<br>
                <small>Requires: contract_text, analysis_type</small>
            </div>
            
            <h2>🔗 Frontend Integration:</h2>
            <p>Your frontend should send POST requests to:</p>
            <div class="endpoint">http://localhost:5000/api/analyze</div>
            
            <h2>📁 Project Structure:</h2>
            <pre>
contract-guard/
├── frontend/
│   ├── index.html
│   ├── login.html
│   └── app.html
└── backend/
    ├── app.py
    ├── .env
    └── requirements.txt
            </pre>
        </div>
    </body>
    </html>
    """

# Run the server
if __name__ == '__main__':
    print(f"🌐 Server starting at: http://localhost:{PORT}")
    print(f"🔗 Health check: http://localhost:{PORT}/api/health")
    print(f"🤖 AI Test: http://localhost:{PORT}/api/test")
    print("\n📢 Press Ctrl+C to stop the server")
    print("="*60)
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
