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
    model = genai.GenerativeModel('gemini-pro')
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
    if not model:
        raise HTTPException(status_code=500, detail="Gemini API not configured. Please set GEMINI_API_KEY environment variable.")
    
    try:
        prompt = f"Give me 5 interesting and educational facts about {animal_name}. Format the response as a JSON array of strings, where each string is one fact. Make the facts engaging and informative."
        
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        try:
            facts = json.loads(response.text)
        except json.JSONDecodeError:
            # If not JSON, split by lines and clean up
            facts_text = response.text.strip()
            facts = [fact.strip() for fact in facts_text.split('\n') if fact.strip()]
            # Take only the first 5 facts
            facts = facts[:5]
        
        return {
            "animal": animal_name,
            "facts": facts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating facts: {str(e)}")

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