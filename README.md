# Multimodal Technical Analysis System

A powerful tool for analyzing technical images, code snippets, and their relationships to help troubleshoot issues and provide actionable recommendations.

## Features

- **Image Analysis**: Analyze screenshots, diagrams, and technical images to identify issues
- **Code Analysis**: Parse and analyze code to detect bugs, performance issues, and best practices violations
- **Combined Analysis**: Correlate visual information with code to find root causes of technical problems
- **Actionable Recommendations**: Get specific suggestions to resolve identified issues

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **AI Processing**: Groq API for vision and language processing
- **Image Processing**: OpenCV and Pillow
- **OCR**: Pytesseract for text extraction from images
- **Development Environment**: Replit

## Getting Started

### Prerequisites

- Python 3.9+
- Groq API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/multimodal-analyzer.git
   cd multimodal-analyzer
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_API_BASE=https://api.groq.com/openai/v1
   SECRET_KEY=your_app_secret_key_here
   ```

4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

5. Open your browser and navigate to `http://localhost:8000`

## Usage

### Analyzing Images

1. Navigate to the "Image Analysis" tab
2. Upload a technical image (screenshot, diagram, error message, etc.)
3. Click "Analyze Image"
4. Review the analysis results and recommendations

### Analyzing Code

1. Navigate to the "Code Analysis" tab
2. Upload a code file
3. Click "Analyze Code"
4. Review the identified issues, suggestions, and recommendations

### Combined Analysis

1. Navigate to the "Combined Analysis" tab
2. Upload both an image and a related code file
3. Optionally provide additional context about the issue
4. Click "Analyze Both"
5. Review the comprehensive analysis that correlates visual information with code

## API Endpoints

- `POST /api/analyze/image`: Analyze technical images
- `POST /api/analyze/code`: Analyze code files
- `POST /api/analyze/combined`: Analyze both image and code together

## Project Structure

```
/app
  /static
    - styles.css
    - script.js
  /templates
    - index.html
  /utils
    - image_processor.py
    - code_analyzer.py
    - groq_client.py
  - main.py
- requirements.txt
- .env
```

## Development

This project is set up for development on Replit. To work on it:

1. Fork the Replit project
2. Add your Groq API key to the Replit secrets
3. Make your changes
4. Test using the Replit run button

## License

MIT

## Acknowledgements

- Groq for providing the powerful AI models
- Replit for the development environment
- OpenCV and Pillow for image processing capabilities
- FastAPI for the efficient web framework
