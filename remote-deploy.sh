#!/bin/bash
# Remote VPS Deployment Script
# This script deploys the backend to a VPS server
# Usage: ./remote-deploy.sh [VPS_IP] [SSH_USER] [SSH_PASSWORD]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VPS_IP="${1:-}"
SSH_USER="${2:-root}"
SSH_PASSWORD="${3:-}"
SSH_PORT="${SSH_PORT:-22}"
PROJECT_DIR="/opt/carsdedo_backend"
REPO_URL="${REPO_URL:-}"  # Your GitHub repo URL

# Check if required parameters are provided
if [ -z "$VPS_IP" ]; then
    echo -e "${RED}❌ Error: VPS IP address is required${NC}"
    echo "Usage: $0 <VPS_IP> [SSH_USER] [SSH_PASSWORD]"
    echo "Example: $0 192.168.1.100 root mypassword"
    exit 1
fi

echo -e "${GREEN}🚀 CarsDedo Backend - Remote VPS Deployment${NC}"
echo "=========================================="
echo "VPS IP: $VPS_IP"
echo "SSH User: $SSH_USER"
echo "SSH Port: $SSH_PORT"
echo ""

# Check if sshpass is installed (for password authentication)
if [ -n "$SSH_PASSWORD" ]; then
    if ! command -v sshpass &> /dev/null; then
        echo -e "${YELLOW}⚠️  sshpass not found. Installing...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if ! command -v brew &> /dev/null; then
                echo -e "${RED}❌ Homebrew not found. Please install it or use SSH keys instead.${NC}"
                exit 1
            fi
            brew install hudochenkov/sshpass/sshpass
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y sshpass
        fi
    fi
    SSH_CMD="sshpass -p '$SSH_PASSWORD' ssh -o StrictHostKeyChecking=no -p $SSH_PORT"
    SCP_CMD="sshpass -p '$SSH_PASSWORD' scp -o StrictHostKeyChecking=no -P $SSH_PORT"
else
    SSH_CMD="ssh -o StrictHostKeyChecking=no -p $SSH_PORT"
    SCP_CMD="scp -o StrictHostKeyChecking=no -P $SSH_PORT"
fi

echo -e "${YELLOW}📡 Testing SSH connection...${NC}"
if $SSH_CMD "$SSH_USER@$VPS_IP" "echo 'Connection successful'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed. Please check:${NC}"
    echo "   - IP address is correct"
    echo "   - SSH service is running on VPS"
    echo "   - Firewall allows SSH (port $SSH_PORT)"
    echo "   - Credentials are correct"
    exit 1
fi

echo ""
echo -e "${YELLOW}🔧 Installing required packages on VPS...${NC}"
$SSH_CMD "$SSH_USER@$VPS_IP" << 'ENDSSH'
    # Update system
    apt-get update -qq
    
    # Install Docker if not installed
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Install Docker Compose if not installed
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Install Git if not installed
    if ! command -v git &> /dev/null; then
        apt-get install -y git
    fi
    
    echo "✅ Required packages installed"
ENDSSH

echo ""
echo -e "${YELLOW}📦 Preparing deployment...${NC}"

# Check if we should use git or direct copy
if [ -n "$REPO_URL" ]; then
    echo -e "${YELLOW}📥 Cloning repository from GitHub...${NC}"
    $SSH_CMD "$SSH_USER@$VPS_IP" << ENDSSH
        mkdir -p $PROJECT_DIR
        cd $PROJECT_DIR
        if [ -d ".git" ]; then
            echo "Repository exists, pulling latest changes..."
            git pull origin main
        else
            echo "Cloning repository..."
            git clone $REPO_URL .
        fi
ENDSSH
else
    echo -e "${YELLOW}📤 Copying files to VPS...${NC}"
    # Create project directory
    $SSH_CMD "$SSH_USER@$VPS_IP" "mkdir -p $PROJECT_DIR"
    
    # Copy files (excluding .git, node_modules, etc.)
    echo "Copying project files..."
    rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
        --exclude '.env' --exclude 'venv' --exclude '.DS_Store' \
        -e "$SSH_CMD" \
        ./ "$SSH_USER@$VPS_IP:$PROJECT_DIR/"
fi

echo ""
echo -e "${YELLOW}⚙️  Setting up environment and deploying...${NC}"
$SSH_CMD "$SSH_USER@$VPS_IP" << 'ENDSSH'
    cd /opt/carsdedo_backend
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "Creating .env file from template..."
        cp ENV_TEMPLATE.txt .env
        
        # Generate SECRET_KEY
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        
        # Set POSTGRES_PASSWORD
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        sed -i "s/your-postgres-password-here/$POSTGRES_PASSWORD/" .env
        
        echo "⚠️  Please edit .env file with your production settings:"
        echo "   nano .env"
    fi
    
    # Make scripts executable
    chmod +x deploy-vps.sh import_data.sh entrypoint.sh 2>/dev/null || true
    
    # Deploy using docker-compose
    echo "🚀 Starting deployment..."
    docker-compose -f docker-compose.vps.yml down 2>/dev/null || true
    docker-compose -f docker-compose.vps.yml build --no-cache
    docker-compose -f docker-compose.vps.yml up -d
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Run migrations
    echo "🔄 Running database migrations..."
    docker-compose -f docker-compose.vps.yml exec -T backend python backend/manage.py migrate || true
    
    # Import data
    echo "📊 Importing CSV data..."
    sleep 5
    docker-compose -f docker-compose.vps.yml exec -T backend python backend/manage.py import_all_data || echo "⚠️  Data import may have failed or already imported"
    
    echo ""
    echo "✅ Deployment complete!"
ENDSSH

echo ""
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo ""
echo "🌐 Your API should be available at:"
echo "   http://$VPS_IP:8000/api/cars/"
echo ""
echo "📋 Useful commands:"
echo "   View logs: ssh $SSH_USER@$VPS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.vps.yml logs -f'"
echo "   Stop services: ssh $SSH_USER@$VPS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.vps.yml down'"
echo "   Restart: ssh $SSH_USER@$VPS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.vps.yml restart'"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Configure firewall (allow ports 8000, 22)"
echo "   2. Set up domain and SSL (see VPS_DEPLOYMENT.md)"
echo "   3. Review .env file settings"
echo ""
