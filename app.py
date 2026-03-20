import os
import io
import pdfplumber
from fastapi import FastAPI, UploadFile, File
from google import genai
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv  # <--- 1. Add this

# --- 1. SETUP ---
load_dotenv()  # <--- 2. Add this BEFORE calling os.environ.get

app = FastAPI()

# Now this will actually find the key
# CHANGE THIS:
# api_key = os.environ.get("GEMINI_API_KEY")

# TO THIS:
api_key = "AIzaSyAOKJgpnSFoToBJooAEoswvHnYvxg6Rcng"

if not api_key:
    # This will stop the app immediately if the key is missing
    raise ValueError("CRITICAL ERROR: GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. ROUTES ---

@app.get("/")
@app.head("/")  # This stops the "405 Method Not Allowed" error in Render logs
def home():
    return {"status": "The Brain is Awake and Healthy!"}
@app.get("/list-models")
def list_models():
    # This will show you exactly what names to use
    models = [m.name for m in client.models.list()]
    return {"available_models": models}
@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    # Read the uploaded PDF file
    pdf_content = await file.read()
    
    # Extract text from PDF
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    # Send to Gemini
    # Note: Using 'gemini-2.0-flash' for stability
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=f"""You are a Senior Technical Recruiter. Analyze this resume. 
        
        CRITICAL RULES:
        1. DO NOT USE TABLES. Use standard text only.
        2. Keep the formatting clean and readable.
        
        Format exactly like this:
        ## 📊 Comprehensive Evaluation: [Score]/100
        (Detailed paragraph of 4 sentences here)

        ### 🌟 Expert-Identified Strengths
        * **[Strength 1]:** (Deep analysis of 2 sentences)
        * **[Strength 2]:** (Deep analysis of 2 sentences)
        * **[Strength 3]:** (Deep analysis of 2 sentences)

        ### 🛠️ Strategic Improvements
        * **[Fix 1]:** (What to fix and why of 2 sentences)
        * **[Fix 2]:** (What to fix and why of 2 sentences)
        * **[Fix 3]:** (What to fix and why of 2 sentences)

        ### 💡 Interview Preparation Strategy
        (Final paragraph of 4 sentences here)

        Resume text: {text}"""
    )
    
    return {"analysis": response.text}
if __name__ == "__main__":
    import uvicorn
    # This tells Python to start the server when you run the file
    uvicorn.run(app, host="0.0.0.0", port=8000)