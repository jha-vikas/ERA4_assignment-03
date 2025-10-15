from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

app = FastAPI()

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create images directory if it doesn't exist
os.makedirs("images", exist_ok=True)

# Serve static files (if you have an images folder)
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("front_page.html")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API configuration"""
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "api_key_format_valid": bool(GEMINI_API_KEY and GEMINI_API_KEY.startswith('AIza')),
        "model_available": bool(model)
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify the server is working"""
    print("🧪 Test endpoint called")
    return {"message": "Server is working!", "timestamp": "2024-10-15"}

@app.get("/animal/{animal_name}")
async def get_animal_image(animal_name: str):
    """Return the path to the animal image"""
    animal_images = {
        "cat": "/images/cat.jpg",
        "dog": "/images/dog.jpg",
        "elephant": "/images/elephant.jpg"
    }
    
    if animal_name.lower() in animal_images:
        return {"image_url": animal_images[animal_name.lower()]}
    return {"error": "Animal not found"}

@app.get("/animal-facts/{animal_name}")
async def get_animal_facts(animal_name: str):
    """Get 5 interesting facts about an animal using Gemini AI"""
    print(f"🐾 Received request for animal facts: {animal_name}")
    
    if not model:
        print("❌ Gemini model not configured")
        raise HTTPException(status_code=500, detail="Gemini API not configured. Please set GEMINI_API_KEY environment variable.")
    
    try:
        prompt = f"Give me 5 interesting and educational facts about {animal_name}. Return ONLY a JSON array of strings, no other text, no markdown, no code blocks. Each string should be one fact. Example: [\"Fact 1\", \"Fact 2\", \"Fact 3\", \"Fact 4\", \"Fact 5\"]"
        
        response = model.generate_content(prompt)
        
        # Clean up the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Try to parse the response as JSON
        try:
            facts = json.loads(response_text)
            # Ensure it's a list
            if not isinstance(facts, list):
                raise ValueError("Response is not a list")
            # Clean up each fact
            facts = [fact.strip().strip('"').strip("'") for fact in facts if fact.strip()]
        except (json.JSONDecodeError, ValueError):
            # If not JSON, split by lines and clean up
            facts_text = response_text.strip()
            # Remove any remaining JSON brackets
            facts_text = facts_text.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            # Split by commas or newlines
            facts = []
            for line in facts_text.split(','):
                if line.strip():
                    fact = line.strip().strip('"').strip("'").strip()
                    if fact and not fact.startswith('```'):
                        facts.append(fact)
            
            # If still no facts, try splitting by newlines
            if not facts:
                for line in facts_text.split('\n'):
                    if line.strip():
                        fact = line.strip().strip('"').strip("'").strip()
                        if fact and not fact.startswith('```'):
                            facts.append(fact)
        
        # Take only the first 5 facts and clean them up
        facts = facts[:5]
        facts = [fact.strip() for fact in facts if fact.strip()]
        
        return {
            "animal": animal_name,
            "facts": facts
        }
    
    except Exception as e:
        error_detail = f"Error generating facts: {str(e)}"
        print(f"❌ Gemini API Error: {error_detail}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   API Key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
        if GEMINI_API_KEY:
            print(f"   API Key format: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and return file information"""
    # Read file content to get size
    content = await file.read()
    file_size = len(content)
    
    # Format file size
    if file_size < 1024:
        size_str = f"{file_size} B"
    elif file_size < 1024 * 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    else:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    
    return {
        "filename": file.filename,
        "size": size_str,
        "type": file.content_type
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)