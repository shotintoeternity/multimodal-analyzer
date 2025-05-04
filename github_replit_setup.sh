#!/bin/bash
# Script to automate GitHub upload and Replit import for the Multimodal Technical Analysis System
# This script handles Git initialization, GitHub repository creation, and provides Replit import instructions

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  GitHub and Replit Setup Automation     ${NC}"
echo -e "${GREEN}  for Multimodal Technical Analysis      ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: Git is not installed. Please install Git first.${NC}"
    echo "Visit: https://git-scm.com/downloads"
    exit 1
fi

# Check if GitHub CLI is installed (optional but helpful)
GH_CLI_AVAILABLE=false
if command -v gh &> /dev/null; then
    GH_CLI_AVAILABLE=true
    # Check if logged in
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}GitHub CLI is installed but you're not logged in.${NC}"
        echo -e "Please login with: ${BLUE}gh auth login${NC}"
        GH_CLI_AVAILABLE=false
    fi
else
    echo -e "${YELLOW}GitHub CLI not found. We'll use manual GitHub setup.${NC}"
    echo -e "To install GitHub CLI for easier setup: ${BLUE}brew install gh${NC}"
fi

# Get GitHub username
read -p "Enter your GitHub username: " github_username

# Get repository name
read -p "Enter repository name [multimodal-analyzer]: " repo_name
repo_name=${repo_name:-multimodal-analyzer}

# Get repository visibility
read -p "Make repository private? (y/n) [n]: " private_choice
private_choice=${private_choice:-n}
if [[ $private_choice =~ ^[Yy]$ ]]; then
    private_flag="--private"
    private_text="private"
else
    private_flag="--public"
    private_text="public"
fi

# Initialize Git repository if not already initialized
if [ ! -d .git ]; then
    echo -e "${GREEN}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized.${NC}"
else
    echo -e "${YELLOW}Git repository already initialized.${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo -e "${YELLOW}Creating .gitignore file...${NC}"
    cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Environment variables
.env

# IDE files
.idea/
.vscode/
*.swp
*.swo

# OS specific files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log
EOL
    echo -e "${GREEN}.gitignore file created.${NC}"
fi

# Stage all files
echo -e "${GREEN}Staging files for commit...${NC}"
git add .

# Commit changes
echo -e "${GREEN}Committing files...${NC}"
git commit -m "Initial commit: Multimodal Technical Analysis System"

# Create GitHub repository
echo -e "${GREEN}Creating ${private_text} GitHub repository: ${repo_name}...${NC}"

if [ "$GH_CLI_AVAILABLE" = true ]; then
    # Create repository using GitHub CLI
    gh repo create "$repo_name" $private_flag --source=. --remote=origin --push
    
    # Get the repository URL
    repo_url=$(gh repo view --json url -q .url)
    echo -e "${GREEN}Repository created and code pushed to GitHub.${NC}"
    echo -e "Repository URL: ${BLUE}${repo_url}${NC}"
else
    # Manual repository creation instructions
    echo -e "${YELLOW}Please create a repository manually on GitHub:${NC}"
    echo -e "1. Go to ${BLUE}https://github.com/new${NC}"
    echo -e "2. Repository name: ${BLUE}${repo_name}${NC}"
    echo -e "3. Set visibility to ${BLUE}${private_text}${NC}"
    echo -e "4. Do NOT initialize with README, .gitignore, or license"
    echo -e "5. Click 'Create repository'"
    echo ""
    echo -e "Press Enter after creating the repository on GitHub..."
    read -p ""
    
    # Set remote and push
    echo -e "${GREEN}Setting up remote and pushing code...${NC}"
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    git branch -M main
    git push -u origin main
    
    repo_url="https://github.com/$github_username/$repo_name"
    echo -e "${GREEN}Code pushed to GitHub.${NC}"
    echo -e "Repository URL: ${BLUE}${repo_url}${NC}"
fi

# Replit import instructions
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  Replit Import Instructions             ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "Now that your code is on GitHub, follow these steps to import it to Replit:"
echo -e "1. Open the Replit desktop app"
echo -e "2. Sign in to your Replit account"
echo -e "3. Click on 'Create' or '+' to create a new Repl"
echo -e "4. Select 'Import from GitHub'"
echo -e "5. Paste this repository URL: ${BLUE}${repo_url}${NC}"
echo -e "6. Click 'Import from GitHub'"
echo ""
echo -e "${YELLOW}After importing to Replit:${NC}"
echo -e "1. Set up environment variables:"
echo -e "   - Click on the 'Tools' or 'Secrets' tab"
echo -e "   - Add your GROQ_API_KEY and other environment variables"
echo -e "2. Run your application:"
echo -e "   - Click the 'Run' button or type 'python run.py' in the shell"
echo ""
echo -e "${GREEN}Would you like to open Replit now? (y/n) [y]: ${NC}"
read -p "" open_replit
open_replit=${open_replit:-y}

if [[ $open_replit =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Opening Replit...${NC}"
    open -a Replit
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Setup process complete!                ${NC}"
echo -e "${GREEN}=========================================${NC}"
