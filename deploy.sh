#!/bin/bash
# Deployment script for Multimodal Technical Analysis System
# This script helps deploy the application to different environments

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Multimodal Technical Analysis System   ${NC}"
echo -e "${GREEN}           Deployment Script             ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your actual API keys and settings${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Function to deploy to Replit
deploy_to_replit() {
    echo -e "${GREEN}Deploying to Replit...${NC}"
    echo "Make sure you have:"
    echo "1. Added your Groq API key to Replit Secrets"
    echo "2. Set up the proper environment in Replit"
    echo ""
    echo "To deploy on Replit:"
    echo "1. Push your code to a GitHub repository"
    echo "2. Create a new Replit project from that repository"
    echo "3. Add your environment variables in the Replit Secrets tab"
    echo "4. Run the application using 'python run.py'"
    echo ""
    echo -e "${GREEN}Replit deployment instructions complete.${NC}"
}

# Function to deploy locally with Docker
deploy_with_docker() {
    echo -e "${GREEN}Deploying with Docker...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f Dockerfile ]; then
        echo -e "${YELLOW}Creating Dockerfile...${NC}"
        cat > Dockerfile << EOL
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install tesseract for OCR
RUN apt-get update && apt-get install -y tesseract-ocr && apt-get clean

COPY . .

EXPOSE 8000

CMD ["python", "run.py"]
EOL
        echo -e "${GREEN}Dockerfile created.${NC}"
    fi
    
    # Create docker-compose.yml if it doesn't exist
    if [ ! -f docker-compose.yml ]; then
        echo -e "${YELLOW}Creating docker-compose.yml...${NC}"
        cat > docker-compose.yml << EOL
version: '3'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./app:/app/app
EOL
        echo -e "${GREEN}docker-compose.yml created.${NC}"
    fi
    
    # Build and run with Docker Compose
    echo -e "${GREEN}Building and starting Docker container...${NC}"
    docker-compose up --build -d
    
    echo -e "${GREEN}Docker deployment complete. Application is running at http://localhost:8000${NC}"
}

# Function to deploy to Heroku
deploy_to_heroku() {
    echo -e "${GREEN}Deploying to Heroku...${NC}"
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo -e "${RED}Error: Heroku CLI is not installed. Please install it first.${NC}"
        echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Procfile if it doesn't exist
    if [ ! -f Procfile ]; then
        echo -e "${YELLOW}Creating Procfile...${NC}"
        echo "web: uvicorn app.main:app --host=0.0.0.0 --port=\$PORT" > Procfile
        echo -e "${GREEN}Procfile created.${NC}"
    fi
    
    # Create runtime.txt if it doesn't exist
    if [ ! -f runtime.txt ]; then
        echo -e "${YELLOW}Creating runtime.txt...${NC}"
        echo "python-3.9.16" > runtime.txt
        echo -e "${GREEN}runtime.txt created.${NC}"
    fi
    
    # Ask for Heroku app name
    read -p "Enter your Heroku app name (leave blank to create a new one): " app_name
    
    if [ -z "$app_name" ]; then
        echo -e "${YELLOW}Creating a new Heroku app...${NC}"
        heroku create
    else
        # Check if app exists
        if heroku apps:info --app "$app_name" &> /dev/null; then
            echo -e "${GREEN}Using existing Heroku app: $app_name${NC}"
        else
            echo -e "${YELLOW}Creating Heroku app: $app_name${NC}"
            heroku create "$app_name"
        fi
    fi
    
    # Set environment variables from .env
    echo -e "${GREEN}Setting environment variables...${NC}"
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ $line =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        
        # Extract key and value
        key=$(echo "$line" | cut -d '=' -f 1)
        value=$(echo "$line" | cut -d '=' -f 2-)
        
        # Set Heroku config
        heroku config:set "$key"="$value"
    done < .env
    
    # Add Heroku buildpacks
    echo -e "${GREEN}Adding buildpacks...${NC}"
    heroku buildpacks:add --index 1 heroku/python
    heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt
    
    # Create Aptfile for tesseract if it doesn't exist
    if [ ! -f Aptfile ]; then
        echo -e "${YELLOW}Creating Aptfile for tesseract...${NC}"
        echo "tesseract-ocr" > Aptfile
        echo "tesseract-ocr-eng" >> Aptfile
        echo -e "${GREEN}Aptfile created.${NC}"
    fi
    
    # Deploy to Heroku
    echo -e "${GREEN}Deploying to Heroku...${NC}"
    git add .
    git commit -m "Prepare for Heroku deployment" || true
    git push heroku main || git push heroku master
    
    # Open the app
    heroku open
    
    echo -e "${GREEN}Heroku deployment complete.${NC}"
}

# Function to deploy to AWS Elastic Beanstalk
deploy_to_aws() {
    echo -e "${GREEN}Deploying to AWS Elastic Beanstalk...${NC}"
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}Error: AWS CLI is not installed. Please install it first.${NC}"
        echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    # Check if EB CLI is installed
    if ! command -v eb &> /dev/null; then
        echo -e "${RED}Error: Elastic Beanstalk CLI is not installed. Please install it first.${NC}"
        echo "Run: pip install awsebcli"
        exit 1
    fi
    
    # Initialize EB if not already done
    if [ ! -d .elasticbeanstalk ]; then
        echo -e "${YELLOW}Initializing Elastic Beanstalk...${NC}"
        eb init
    fi
    
    # Create .ebextensions directory if it doesn't exist
    if [ ! -d .ebextensions ]; then
        mkdir -p .ebextensions
    fi
    
    # Create config file for packages
    if [ ! -f .ebextensions/01_packages.config ]; then
        echo -e "${YELLOW}Creating EB packages config...${NC}"
        cat > .ebextensions/01_packages.config << EOL
packages:
  yum:
    tesseract: []
    tesseract-langpack-eng: []
EOL
        echo -e "${GREEN}EB packages config created.${NC}"
    fi
    
    # Create config file for environment variables
    if [ ! -f .ebextensions/02_environment.config ]; then
        echo -e "${YELLOW}Creating EB environment config...${NC}"
        cat > .ebextensions/02_environment.config << EOL
option_settings:
  aws:elasticbeanstalk:application:environment:
EOL
        
        # Add environment variables from .env
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Skip comments and empty lines
            [[ $line =~ ^#.*$ ]] && continue
            [[ -z "$line" ]] && continue
            
            # Extract key and value
            key=$(echo "$line" | cut -d '=' -f 1)
            value=$(echo "$line" | cut -d '=' -f 2-)
            
            # Add to config
            echo "    $key: $value" >> .ebextensions/02_environment.config
        done < .env
        
        echo -e "${GREEN}EB environment config created.${NC}"
    fi
    
    # Create Procfile if it doesn't exist
    if [ ! -f Procfile ]; then
        echo -e "${YELLOW}Creating Procfile...${NC}"
        echo "web: uvicorn app.main:app --host=0.0.0.0 --port=5000" > Procfile
        echo -e "${GREEN}Procfile created.${NC}"
    fi
    
    # Deploy to EB
    echo -e "${GREEN}Deploying to Elastic Beanstalk...${NC}"
    eb deploy
    
    echo -e "${GREEN}AWS Elastic Beanstalk deployment complete.${NC}"
}

# Main menu
echo "Select deployment target:"
echo "1) Replit"
echo "2) Docker (local)"
echo "3) Heroku"
echo "4) AWS Elastic Beanstalk"
echo "q) Quit"

read -p "Enter your choice: " choice

case $choice in
    1)
        deploy_to_replit
        ;;
    2)
        deploy_with_docker
        ;;
    3)
        deploy_to_heroku
        ;;
    4)
        deploy_to_aws
        ;;
    q|Q)
        echo "Exiting deployment script."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}      Deployment process complete        ${NC}"
echo -e "${GREEN}=========================================${NC}"
