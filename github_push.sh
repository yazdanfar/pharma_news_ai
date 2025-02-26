#!/bin/bash

# Script to push the PharmaNewsAI project to GitHub
# Make this script executable with: chmod +x github_push.sh

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PharmaNewsAI GitHub Setup Script${NC}"
echo "This script will help you push your PharmaNewsAI project to GitHub."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git and try again.${NC}"
    exit 1
fi

# Prompt for GitHub username
read -p "Enter your GitHub username: " github_username

# Prompt for repository name
read -p "Enter the name for your GitHub repository (default: pharma_news_ai): " repo_name
repo_name=${repo_name:-pharma_news_ai}

# Prompt for repository description
read -p "Enter a short description for your repository: " repo_description

# Prompt for GitHub personal access token
echo "You'll need a GitHub personal access token with 'repo' scope."
echo "If you don't have one, create it at: https://github.com/settings/tokens"
read -sp "Enter your GitHub personal access token: " github_token
echo ""

# Update setup.py with user's GitHub info
echo -e "${YELLOW}Updating setup.py with your GitHub information...${NC}"
sed -i "s/yourusername/$github_username/g" setup.py
sed -i "s/Your Name/$github_username/g" setup.py

# Update LICENSE with user's name
echo -e "${YELLOW}Updating LICENSE with your name...${NC}"
sed -i "s/\[Your Name\]/$github_username/g" LICENSE

# Create GitHub repository
echo -e "${YELLOW}Creating GitHub repository...${NC}"
curl -u "$github_username:$github_token" https://api.github.com/user/repos -d "{\"name\":\"$repo_name\",\"description\":\"$repo_description\",\"private\":false}"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create GitHub repository. Please check your credentials and try again.${NC}"
    exit 1
fi

# Initialize git and commit files
echo -e "${YELLOW}Initializing git repository and committing files...${NC}"
git init
git add .
git commit -m "Initial commit: PharmaNewsAI project"

# Set the remote origin
echo -e "${YELLOW}Setting remote origin...${NC}"
git remote add origin https://github.com/$github_username/$repo_name.git

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push -u origin master

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to push to GitHub. Please check your credentials and try again.${NC}"
    echo -e "${YELLOW}You can try manually with:${NC}"
    echo "git push -u origin master"
    exit 1
fi

echo -e "${GREEN}Success! Your PharmaNewsAI project is now on GitHub at:${NC}"
echo -e "${GREEN}https://github.com/$github_username/$repo_name${NC}"
echo ""
echo -e "To install the package in development mode, run:"
echo -e "${YELLOW}pip install -e .${NC}"
echo ""
echo -e "To run the agent, use:"
echo -e "${YELLOW}python -m pharma_news_ai.examples.run_agent${NC}"
echo ""
echo -e "Or after installation:"
echo -e "${YELLOW}pharma-news-ai${NC}"