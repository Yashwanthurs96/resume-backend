import pdfplumber
import io
from fastapi import FastAPI, UploadFile, File
from google import genai
from fastapi.middleware.cors import CORSMiddleware

# --- 1. SETUP THE BRAIN ---
app = FastAPI()
import os # Make sure this is at the very top of your file!

# Replace your client line with this:
client = genai.Client(api_key=os.environ.get("AIzaSyBeZZaiVhjJHtKLjW9-pO3o8CvvfBYD_QY"))

# This allows your Website to talk to your Python code (Very Important!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. THE "UPLOAD" GATEWAY ---
@app.get("/")
def home():
    return {"status": "The Brain is Awake and Healthy!"}
@app.get("/")
def home():
    return {"status": "The Brain is Awake and Healthy!"}
@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    # Read the uploaded PDF file
    pdf_content = await file.read()
    
    # Use pdfplumber to read the text from memory
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    # Send it to Gemini
    # Send it to Gemini with STRICT formatting rules
    # NEW PROMPT: Ask for deep, detailed explanations
    # NEW PROMPT: Strictly forbid tables and enforce clean text
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=f"""You are a Senior Technical Recruiter. Analyze this resume. 
        
        CRITICAL RULES:
        1. DO NOT USE TABLES. Use standard text only.
        2. Keep the formatting clean and readable.
        
        Format exactly like this:
        ## 📊 Comprehensive Evaluation: [Score]/100
        (Write your detailed paragraph of 2-3 sentences here)

        ### 🌟 Expert-Identified Strengths
        * **[Strength 1]:** (Write 1 sentences of deep analysis)
        * **[Strength 2]:** (Write 1 sentences of deep analysis)
        * **[Strength 3]:** (Write 1 sentences of deep analysis)

        ### 🛠️ Strategic Improvements
        * **[Fix 1]:** (Write a detailed explanation of 2 sentences of what to fix and why)
        * **[Fix 2]:** (Write a detailed explanation of 2 sentences of what to fix and why)
        * **[Fix 3]:** (Write a detailed explanation of 2 sentences of what to fix and why)

        ### 💡 Interview Preparation Strategy
        (Write your final paragraph of 2-3 sentences here)

        Resume text: {text}"""
    )
    # Send the result back to the website
    return {"analysis": response.text}

# --- 3. RUN COMMAND ---
# To run this, type: uvicorn app:app --reload