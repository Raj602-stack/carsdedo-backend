# Hostinger Deployment Guide

This guide will help you deploy your CarsDedo backend to Hostinger.

## Hostinger Hosting Options

Hostinger offers different hosting plans. For Django/Python applications, you need:

### Option 1: VPS Hosting (Recommended)
- **Best for:** Full control, Docker support, custom configurations
- **Requirements:** VPS plan with root access
- **Cost:** ~$4-10/month

### Option 2: Shared Hosting (Limited)
- **Not recommended** for Django apps
- Limited Python/Django support
- No Docker support
- Better for static sites

## Prerequisites

1. **Hostinger VPS account** with:
   - Ubuntu 20.04/22.04
   - Root/SSH access
   - At least 1GB RAM (2GB+ recommended)
   - PostgreSQL database access

2. **Domain name** (optional but recommended)
   - Point DNS to Hostinger's nameservers

## Step-by-Step Deployment

### Step 1: Prepare Your Local Environment

1. **Create a backup of your data:**
   ```bash
   # Export database
   docker compose exec db pg_dump -U your_user your_db > backup.sql
   
   # Or use the backup script
   ./scripts/backup_db.sh
   ```

2. **Prepare your code:**
   ```bash
   # Make sure all changes are committed
   git add .
   git commit -m "Ready for production deployment"
   git push origin main
   ```

### Step 2: Connect to Hostinger VPS

1. **Get SSH credentials from Hostinger:**
   - Log into Hostinger hPanel
   - Go to VPS section
   - Find SSH credentials (IP, username, password/key)

2. **Connect via SSH:**
   ```bash
   ssh root@your-server-ip
   # Or
   ssh username@your-server-ip
   ```

### Step 3: Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y

# Install PostgreSQL client (if needed)
sudo apt install postgresql-client -y

# Log out and back in for Docker group to take effect
exit
# Then SSH back in
```

### Step 4: Clone Your Repository

```bash
# Create project directory
mkdir -p /var/www
cd /var/www

# Clone your repository
git clone https://github.com/yourusername/carsdedo_backend.git
# Or use SSH: git clone git@github.com:yourusername/carsdedo_backend.git

cd carsdedo_backend
```

### Step 5: Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit environment file
nano .env
```

**Update `.env` with production values:**

```env
# Django Settings
DJANGO_SECRET_KEY=your-strong-secret-key-here
DJANGO_DEBUG=0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database Configuration
# Option A: Use Hostinger's PostgreSQL (if available)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=carsdedo_prod
POSTGRES_USER=carsdedo_user
POSTGRES_PASSWORD=your-strong-password

# Option B: Use Docker PostgreSQL (recommended for VPS)
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=carsdedo_prod
POSTGRES_USER=carsdedo_user
POSTGRES_PASSWORD=your-strong-password

# Django Superuser (optional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=your-admin-password

# Twilio (if using SMS)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_FROM_NUMBER=your-number
```

**Generate a strong secret key:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Set Up Database

**Option A: Use Docker PostgreSQL (Easier)**

Your `docker-compose.yml` already includes PostgreSQL. Just make sure the database volume persists.

**Option B: Use Hostinger's PostgreSQL**

1. Create database in Hostinger hPanel
2. Update `.env` with Hostinger database credentials
3. Modify `docker-compose.yml` to remove the `db` service

### Step 7: Build and Start Services

```bash
# Build Docker images
docker compose build

# Run migrations
docker compose run --rm web python backend/manage.py migrate

# Import your data
docker compose run --rm web python backend/manage.py import_all_data

# Or import from backup
# docker compose exec db psql -U user -d dbname < backup.sql

# Start services
docker compose up -d

# Check logs
docker compose logs -f web
```

### Step 8: Set Up Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/carsdedo

# Edit configuration
sudo nano /etc/nginx/sites-available/carsdedo
```

**Update `nginx.conf` with your domain:**
- Replace `yourdomain.com` with your actual domain
- Update paths if needed

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/carsdedo /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 9: Set Up SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure Nginx for HTTPS
```

### Step 10: Configure Firewall

```bash
# Install UFW (if not installed)
sudo apt install ufw -y

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Step 11: Set Up Automatic Backups

```bash
# Create backups directory
mkdir -p /var/www/carsdedo_backend/backups

# Make backup script executable
chmod +x /var/www/carsdedo_backend/scripts/backup_db.sh

# Set up cron job for daily backups
crontab -e
```

Add this line (runs daily at 2 AM):
```
0 2 * * * cd /var/www/carsdedo_backend && ./scripts/backup_db.sh >> /var/log/carsdedo_backup.log 2>&1
```

### Step 12: Set Up Auto-restart on Reboot

```bash
# Create systemd service for Docker Compose
sudo nano /etc/systemd/system/carsdedo.service
```

Add:
```ini
[Unit]
Description=CarsDedo Backend
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/carsdedo_backend
ExecStart=/usr/local/bin/docker compose up -d
ExecStop=/usr/local/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable carsdedo
sudo systemctl start carsdedo
```

## Post-Deployment Checklist

- [ ] Test API endpoints: `https://yourdomain.com/api/cars/`
- [ ] Verify database connection
- [ ] Check all data is imported correctly
- [ ] Test admin panel: `https://yourdomain.com/admin/`
- [ ] Verify SSL certificate is working
- [ ] Set up monitoring/logging
- [ ] Configure domain DNS (if using custom domain)
- [ ] Test backup restoration process
- [ ] Set up error monitoring (Sentry, etc.)

## Updating Your Application

### For Code Updates:

```bash
cd /var/www/carsdedo_backend

# Pull latest code
git pull origin main

# Rebuild containers (if needed)
docker compose build

# Run migrations
docker compose exec web python backend/manage.py migrate

# Restart services
docker compose restart web
```

### For Data Updates:

```bash
# Update CSV files
# Then re-import
docker compose exec web python backend/manage.py import_all_data
```

## Troubleshooting

### Check Container Status:
```bash
docker compose ps
docker compose logs web
docker compose logs db
```

### Check Nginx Status:
```bash
sudo systemctl status nginx
sudo nginx -t
```

### Check Database Connection:
```bash
docker compose exec web python backend/manage.py dbshell
```

### View Application Logs:
```bash
docker compose logs -f web
```

### Restart Services:
```bash
docker compose restart
sudo systemctl restart nginx
```

## Important Security Notes

1. **Never commit `.env` file** to Git
2. **Use strong passwords** for database and Django secret key
3. **Keep Django secret key secret** - never share it
4. **Regularly update** system and Docker images
5. **Set up firewall** rules
6. **Use HTTPS** (SSL certificate)
7. **Regular backups** are essential

## Alternative: Using Hostinger Shared Hosting

If you only have shared hosting (not VPS), you'll need to:

1. **Use a different deployment method:**
   - Deploy to Railway, Render, or Heroku instead
   - These platforms are better suited for Django apps

2. **Or use Hostinger's Python hosting** (if available):
   - Check if Hostinger supports Python/Django
   - May require different setup

## Need Help?

If you encounter issues:
1. Check logs: `docker compose logs`
2. Verify environment variables
3. Check database connection
4. Verify Nginx configuration
5. Check firewall rules

## Quick Reference Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f web

# Run migrations
docker compose exec web python backend/manage.py migrate

# Import data
docker compose exec web python backend/manage.py import_all_data

# Create superuser
docker compose exec web python backend/manage.py createsuperuser

# Backup database
./scripts/backup_db.sh

# Restart Nginx
sudo systemctl restart nginx

# Check SSL certificate
sudo certbot certificates
```
