# FastAPI Animal App with Gemini AI

A FastAPI application for animal image selection, AI-powered animal facts, and file upload, ready for EC2 deployment.

## Features

- FastAPI web application
- Animal image selection (cat, dog, elephant)
- **NEW: AI-powered animal facts using Google Gemini**
- File upload functionality
- CORS enabled for frontend integration
- Simple EC2 deployment ready

## Local Development

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Set up environment variables:**
   ```bash
   # Create .env file with your Gemini API key
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   echo "HOST=0.0.0.0" >> .env
   echo "PORT=8000" >> .env
   echo "DEBUG=False" >> .env
   echo "ENVIRONMENT=production" >> .env
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   - Open http://localhost:8000 in your browser

## EC2 Deployment

### Prerequisites

1. **EC2 instance running** (Ubuntu/Amazon Linux recommended)
2. **Python 3.10+** installed on EC2
3. **Security group** configured to allow HTTP/HTTPS traffic on port 8000

### Deployment Steps

1. **Push to your Git repository:**
   ```bash
   git add .
   git commit -m "Initial FastAPI app setup"
   git push origin main
   ```

2. **On your EC2 instance:**
   ```bash
   # Clone the repository
   git clone <your-repo-url>
   cd ERA4_assignment-03
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Set up environment variables
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   echo "HOST=0.0.0.0" >> .env
   echo "PORT=8000" >> .env
   echo "DEBUG=False" >> .env
   echo "ENVIRONMENT=production" >> .env
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python app.py
   ```

3. **Access your application:**
   - Open `http://<your-ec2-public-ip>:8000` in your browser

### Running as a Service (Optional)

To run the application as a background service on EC2:

1. **Create a systemd service file:**
   ```bash
   sudo nano /etc/systemd/system/fastapi-app.service
   ```

2. **Add the following content:**
   ```ini
   [Unit]
   Description=FastAPI Animal App
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ERA4_assignment-03
   Environment=PATH=/home/ubuntu/ERA4_assignment-03/venv/bin
   ExecStart=/home/ubuntu/ERA4_assignment-03/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fastapi-app
   sudo systemctl start fastapi-app
   sudo systemctl status fastapi-app
   ```

## Project Structure

```
├── app.py                    # Main FastAPI application
├── front_page.html          # Frontend HTML
├── images/                  # Static images directory
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## API Endpoints

- `GET /` - Main HTML page
- `GET /animal/{animal_name}` - Get animal image URL
- `GET /animal-facts/{animal_name}` - Get 5 interesting facts about an animal using Gemini AI
- `POST /upload` - Upload file and get file information

## Environment Variables

Create a `.env` file with:
```
HOST=0.0.0.0
PORT=8000
DEBUG=False
ENVIRONMENT=production
GEMINI_API_KEY=your_gemini_api_key_here
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Replace `your_gemini_api_key_here` in the `.env` file with your actual API key

## Notes

- The application runs on all interfaces (0.0.0.0) to accept external connections
- Static files (images) are served from the `/images` directory
- CORS is enabled for all origins (configure as needed for production)
- Make sure your EC2 security group allows inbound traffic on port 8000
- **Gemini API Key is required for the animal facts feature to work**
- The animal facts feature will return an error if the API key is not configured
