#!/bin/bash
# Deployment script for VPS: 72.62.247.243
# Run this script once SSH connection is working

set -e

VPS_IP="72.62.247.243"
SSH_USER="root"
SSH_PASSWORD="Carsdedo@123"
PROJECT_DIR="/opt/carsdedo_backend"

echo "🚀 CarsDedo Backend - VPS Deployment"
echo "====================================="
echo "VPS: $SSH_USER@$VPS_IP"
echo ""

# Test connection
echo "📡 Testing SSH connection..."
if sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$SSH_USER@$VPS_IP" "echo 'Connection OK'"; then
    echo "✅ Connection successful"
else
    echo "❌ Connection failed. Please check:"
    echo "   - Server is running"
    echo "   - Firewall allows SSH (port 22)"
    echo "   - IP address is correct"
    exit 1
fi

echo ""
echo "🔧 Step 1: Installing required packages..."
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$VPS_IP" << 'ENDSSH'
    apt-get update -qq
    apt-get install -y curl git
    
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
    
    echo "✅ Packages installed"
ENDSSH

echo ""
echo "📦 Step 2: Copying project files..."
# Create directory
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$VPS_IP" "mkdir -p $PROJECT_DIR"

# Copy files using rsync (if available) or scp
if command -v rsync &> /dev/null; then
    echo "Using rsync to copy files..."
    sshpass -p "$SSH_PASSWORD" rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
        --exclude '.env' --exclude 'venv' --exclude '.DS_Store' \
        -e "ssh -o StrictHostKeyChecking=no" \
        ./ "$SSH_USER@$VPS_IP:$PROJECT_DIR/"
else
    echo "Using scp to copy files..."
    sshpass -p "$SSH_PASSWORD" scp -r -o StrictHostKeyChecking=no \
        --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
        ./ "$SSH_USER@$VPS_IP:$PROJECT_DIR/"
fi

echo ""
echo "⚙️  Step 3: Setting up environment and deploying..."
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$SSH_USER@$VPS_IP" << ENDSSH
    cd $PROJECT_DIR
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cp ENV_TEMPLATE.txt .env
        
        # Generate SECRET_KEY
        SECRET_KEY=\$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 32)
        sed -i "s/your-secret-key-here/\$SECRET_KEY/" .env
        
        # Set POSTGRES_PASSWORD
        POSTGRES_PASSWORD=\$(openssl rand -base64 32)
        sed -i "s/your-postgres-password-here/\$POSTGRES_PASSWORD/" .env
        
        echo "⚠️  .env file created. Please review and update if needed."
    fi
    
    # Make scripts executable
    chmod +x deploy-vps.sh import_data.sh entrypoint.sh 2>/dev/null || true
    
    # Stop any existing containers
    docker-compose -f docker-compose.vps.yml down 2>/dev/null || true
    
    # Build and start
    echo "Building Docker images..."
    docker-compose -f docker-compose.vps.yml build --no-cache
    
    echo "Starting containers..."
    docker-compose -f docker-compose.vps.yml up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 15
    
    # Run migrations
    echo "Running migrations..."
    docker-compose -f docker-compose.vps.yml exec -T backend python backend/manage.py migrate || true
    
    # Import data
    echo "Importing CSV data..."
    sleep 5
    docker-compose -f docker-compose.vps.yml exec -T backend python backend/manage.py import_all_data || echo "⚠️  Data import may have failed"
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Service status:"
    docker-compose -f docker-compose.vps.yml ps
ENDSSH

echo ""
echo "✅ Deployment Successful!"
echo ""
echo "🌐 Your API is available at:"
echo "   http://72.62.247.243:8000/api/cars/"
echo ""
echo "📋 Useful commands:"
echo "   View logs: ssh $SSH_USER@$VPS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.vps.yml logs -f'"
echo "   Restart: ssh $SSH_USER@$VPS_IP 'cd $PROJECT_DIR && docker-compose -f docker-compose.vps.yml restart'"
echo ""
