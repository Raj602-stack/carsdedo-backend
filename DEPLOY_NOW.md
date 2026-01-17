# Quick VPS Deployment Guide

I can help you deploy the backend to your VPS. Here's how:

## Option 1: Automated Deployment (Recommended)

I'll create a script that handles everything. You just need to provide:

1. **VPS IP Address** (e.g., `192.168.1.100` or `yourdomain.com`)
2. **SSH Username** (usually `root` or your username)
3. **SSH Password** (or use SSH keys - more secure)

### Using the Script

```bash
# Make script executable
chmod +x remote-deploy.sh

# Run deployment
./remote-deploy.sh <VPS_IP> <SSH_USER> <SSH_PASSWORD>

# Example:
./remote-deploy.sh 192.168.1.100 root mypassword
```

### Using SSH Keys (More Secure)

If you have SSH keys set up:

```bash
# First, copy your SSH key to the VPS
ssh-copy-id user@VPS_IP

# Then run deployment without password
./remote-deploy.sh VPS_IP user
```

## Option 2: Manual Step-by-Step

If you prefer to do it manually or the script doesn't work:

### Step 1: Connect to VPS
```bash
ssh user@VPS_IP
```

### Step 2: Install Required Software
```bash
# Update system
apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt-get install -y git
```

### Step 3: Clone Repository
```bash
cd /opt
git clone YOUR_GITHUB_REPO_URL carsdedo_backend
cd carsdedo_backend
```

### Step 4: Set Up Environment
```bash
# Copy environment template
cp ENV_TEMPLATE.txt .env

# Edit with your settings
nano .env
# Set: SECRET_KEY, POSTGRES_PASSWORD, CORS_ALLOWED_ORIGINS_LIST, etc.
```

### Step 5: Deploy
```bash
# Make scripts executable
chmod +x deploy-vps.sh import_data.sh entrypoint.sh

# Build and start
docker-compose -f docker-compose.vps.yml build
docker-compose -f docker-compose.vps.yml up -d

# Wait a bit, then run migrations and import data
sleep 10
docker-compose -f docker-compose.vps.yml exec backend python backend/manage.py migrate
docker-compose -f docker-compose.vps.yml exec backend python backend/manage.py import_all_data
```

### Step 6: Verify
```bash
# Check if services are running
docker-compose -f docker-compose.vps.yml ps

# Test API
curl http://localhost:8000/api/cars/

# View logs
docker-compose -f docker-compose.vps.yml logs -f backend
```

## What I Need From You

To deploy for you, please provide:

1. **VPS IP Address or Hostname**
2. **SSH Username** (usually `root`)
3. **SSH Password** (or confirm you have SSH keys set up)
4. **GitHub Repository URL** (if you want to use git clone instead of file copy)
5. **Domain Name** (optional, if you have one)

## Security Notes

- ⚠️ **Never share passwords in public channels**
- ✅ Use SSH keys when possible (more secure)
- ✅ Change default passwords after first login
- ✅ Set up firewall rules (allow ports 22, 8000)
- ✅ Use SSL/HTTPS for production

## After Deployment

1. **Configure Firewall:**
   ```bash
   ufw allow 22/tcp
   ufw allow 8000/tcp
   ufw enable
   ```

2. **Set Up Domain (Optional):**
   - Point your domain to VPS IP
   - Configure Nginx (see VPS_DEPLOYMENT.md)
   - Set up SSL with Let's Encrypt

3. **Monitor:**
   ```bash
   # View logs
   docker-compose -f docker-compose.vps.yml logs -f
   
   # Check resource usage
   docker stats
   ```

## Troubleshooting

- **Connection refused:** Check firewall and SSH service
- **Permission denied:** Make sure user has sudo access
- **Port already in use:** Stop existing services on port 8000
- **Docker not found:** Install Docker first (script does this)

---

**Ready to deploy?** Share your VPS details and I'll help you get it running! 🚀
