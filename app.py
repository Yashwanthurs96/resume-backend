import os
import io
import pdfplumber
from fastapi import FastAPI, UploadFile, File
from google import genai
from fastapi.middleware.cors import CORSMiddleware

# --- 1. SETUP ---
app = FastAPI()

# This looks for the secret key you set in the Render Dashboard
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY is not set in Environment Variables!")

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
        model="gemini-1.5-flash", 
        contents=f"""You are a Senior Technical Recruiter. Analyze this resume. 
        
        CRITICAL RULES:
        1. DO NOT USE TABLES. Use standard text only.
        2. Keep the formatting clean and readable.
        
        Format exactly like this:
        ## 📊 Comprehensive Evaluation: [Score]/100
        (Detailed paragraph here)

        ### 🌟 Expert-Identified Strengths
        * **[Strength 1]:** (Deep analysis)
        * **[Strength 2]:** (Deep analysis)
        * **[Strength 3]:** (Deep analysis)

        ### 🛠️ Strategic Improvements
        * **[Fix 1]:** (What to fix and why)
        * **[Fix 2]:** (What to fix and why)
        * **[Fix 3]:** (What to fix and why)

        ### 💡 Interview Preparation Strategy
        (Final paragraph here)

        Resume text: {text}"""
    )
    
    return {"analysis": response.text}