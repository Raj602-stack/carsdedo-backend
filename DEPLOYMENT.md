# Deployment Guide

This guide covers deploying the CarsDedo backend to various platforms.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Production Deployment Options](#production-deployment-options)
  - [AWS EC2 / DigitalOcean Droplet](#aws-ec2--digitalocean-droplet)
  - [Heroku](#heroku)
  - [Railway](#railway)
  - [Render](#render)
- [Environment Variables](#environment-variables)
- [Post-Deployment Checklist](#post-deployment-checklist)

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (or use Docker Compose)
- Python 3.11+ (for local development)
- Git

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd carsdedo_backend
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** with your local settings:
   - Set `DJANGO_DEBUG=1` for development
   - Configure database credentials
   - Set `ALLOWED_HOSTS=localhost,127.0.0.1`

4. **Start services**
   ```bash
   docker compose up --build
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Docker Deployment

### Using Docker Compose (Recommended for VPS)

1. **On your server, clone the repository**
   ```bash
   git clone <repository-url>
   cd carsdedo_backend
   ```

2. **Create `.env` file with production values**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```

3. **Important production settings in `.env`:**
   ```env
   DJANGO_DEBUG=0
   DJANGO_SECRET_KEY=<generate-a-strong-secret-key>
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   POSTGRES_PASSWORD=<strong-password>
   ```

4. **Start the services**
   ```bash
   docker compose up -d --build
   ```

5. **Check logs**
   ```bash
   docker compose logs -f web
   ```

6. **Create superuser (if needed)**
   ```bash
   docker compose exec web python backend/manage.py createsuperuser
   ```

### Using Docker with External Database

If you're using a managed PostgreSQL service (AWS RDS, DigitalOcean Managed DB, etc.):

1. Update `.env`:
   ```env
   POSTGRES_HOST=your-db-host.rds.amazonaws.com
   POSTGRES_PORT=5432
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   ```

2. Update `docker-compose.yml` to remove the `db` service and update the `web` service:
   ```yaml
   services:
     web:
       build: .
       env_file:
         - .env
       ports:
         - "8000:8000"
       volumes:
         - ./backend/media:/code/backend/media
       restart: unless-stopped
   ```

3. Start the web service:
   ```bash
   docker compose up -d --build
   ```

## Production Deployment Options

### AWS EC2 / DigitalOcean Droplet

#### Option 1: Docker Compose (Easiest)

1. **Set up a VPS**
   - Create an EC2 instance or DigitalOcean droplet (Ubuntu 22.04 recommended)
   - Configure security groups/firewall to allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **SSH into your server**
   ```bash
   ssh user@your-server-ip
   ```

3. **Install Docker and Docker Compose**
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

   # Log out and back in for group changes
   ```

4. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd carsdedo_backend
   cp .env.example .env
   nano .env  # Configure production settings
   ```

5. **Start services**
   ```bash
   docker compose up -d --build
   ```

6. **Set up Nginx reverse proxy** (see `nginx.conf` in this repo)
   ```bash
   sudo apt install nginx
   sudo cp nginx.conf /etc/nginx/sites-available/carsdedo
   sudo ln -s /etc/nginx/sites-available/carsdedo /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Set up SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

#### Option 2: Systemd Service (Without Docker)

1. **Install Python and dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx
   ```

2. **Set up PostgreSQL**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE carsdedo_db;
   CREATE USER carsdedo_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE carsdedo_db TO carsdedo_user;
   \q
   ```

3. **Clone and set up application**
   ```bash
   git clone <repository-url>
   cd carsdedo_backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Set production values
   ```

5. **Run migrations and collect static files**
   ```bash
   cd backend
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

6. **Set up Gunicorn systemd service**
   ```bash
   sudo nano /etc/systemd/system/carsdedo.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=CarsDedo Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/carsdedo_backend/backend
   Environment="PATH=/path/to/carsdedo_backend/venv/bin"
   ExecStart=/path/to/carsdedo_backend/venv/bin/gunicorn \
       --workers 3 \
       --bind unix:/path/to/carsdedo_backend/carsdedo.sock \
       backend.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start carsdedo
   sudo systemctl enable carsdedo
   ```

### Heroku

1. **Install Heroku CLI** and login
   ```bash
   heroku login
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**
   ```bash
   heroku config:set DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
   heroku config:set DJANGO_DEBUG=0
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set TWILIO_ACCOUNT_SID=your-sid
   heroku config:set TWILIO_AUTH_TOKEN=your-token
   heroku config:set TWILIO_FROM_NUMBER=your-number
   ```

5. **Create `Procfile`** (if not exists):
   ```
   web: gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --chdir backend
   release: python backend/manage.py migrate --noinput
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

7. **Run migrations and create superuser**
   ```bash
   heroku run python backend/manage.py migrate
   heroku run python backend/manage.py createsuperuser
   ```

### Railway

1. **Connect your GitHub repository** to Railway

2. **Add PostgreSQL service** in Railway dashboard

3. **Set environment variables** in Railway:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=0`
   - `ALLOWED_HOSTS=your-app.railway.app`
   - Database variables (auto-set by Railway PostgreSQL)
   - Twilio credentials

4. **Configure build settings:**
   - Build Command: (leave empty, Railway detects Dockerfile)
   - Start Command: `/code/entrypoint.sh`

5. **Deploy** - Railway will automatically deploy on git push

### Render

1. **Create a new Web Service** on Render

2. **Connect your GitHub repository**

3. **Configure:**
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Context**: `.`

4. **Add PostgreSQL database** in Render dashboard

5. **Set environment variables:**
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=0`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - Database connection string (auto-provided by Render)
   - Twilio credentials

6. **Deploy** - Render will build and deploy automatically

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DJANGO_DEBUG` | Debug mode (0 for production) | `0` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `yourdomain.com,www.yourdomain.com` |
| `POSTGRES_DB` | Database name | `carsdedo_db` |
| `POSTGRES_USER` | Database user | `carsdedo_user` |
| `POSTGRES_PASSWORD` | Database password | `strong-password` |
| `POSTGRES_HOST` | Database host | `db` (for Docker) or `your-db-host.com` |
| `POSTGRES_PORT` | Database port | `5432` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SUPERUSER_USERNAME` | Initial superuser username | - |
| `DJANGO_SUPERUSER_EMAIL` | Initial superuser email | - |
| `DJANGO_SUPERUSER_PASSWORD` | Initial superuser password | - |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | - |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | - |
| `TWILIO_FROM_NUMBER` | Twilio phone number | - |
| `OTP_EXPIRY_SECONDS` | OTP expiration time | `300` |
| `OTP_LENGTH` | OTP code length | `6` |

## Post-Deployment Checklist

- [ ] Verify `DJANGO_DEBUG=0` in production
- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up SSL/HTTPS certificate
- [ ] Configure CORS origins for your frontend
- [ ] Set up database backups
- [ ] Configure media file storage (consider S3 for production)
- [ ] Set up monitoring and logging
- [ ] Test OTP functionality with real Twilio credentials
- [ ] Create admin superuser
- [ ] Test API endpoints
- [ ] Set up domain DNS records
- [ ] Configure firewall rules
- [ ] Set up automated deployments (CI/CD)

## Troubleshooting

### Database Connection Issues
- Verify database credentials in `.env`
- Check network connectivity between app and database
- Ensure database allows connections from your app's IP

### Static Files Not Loading
- Run `python backend/manage.py collectstatic --noinput`
- Verify `STATIC_ROOT` and `STATIC_URL` in settings
- Check web server (Nginx) static file configuration

### Media Files Not Accessible
- Ensure media directory has proper permissions
- Configure web server to serve media files or use cloud storage (S3)

### CORS Errors
- Update `CORS_ALLOWED_ORIGINS` in `settings.py` with your frontend URL
- Or set `CORS_ALLOW_ALL_ORIGINS=True` for development only

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong passwords** for database and Django secret key
3. **Enable HTTPS** in production
4. **Set `DJANGO_DEBUG=0`** in production
5. **Configure proper CORS** origins
6. **Use environment variables** for all secrets
7. **Regularly update dependencies** (`pip list --outdated`)
8. **Set up database backups**
9. **Use managed database services** when possible
10. **Enable security headers** (HSTS, CSP, etc.)

## Support

For issues or questions, please open an issue in the repository.
