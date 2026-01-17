# VPS Deployment Guide for CarsDedo Backend

This guide will help you deploy the CarsDedo backend API to your VPS at `72.62.247.243`.

## Prerequisites

- SSH access to VPS (root@72.62.247.243)
- Docker and Docker Compose installed on VPS
- Domain names configured (optional, for production)

## Step 1: Clone Repository on VPS

```bash
ssh root@72.62.247.243

# Create deployment directory
mkdir -p /root/carsdedo && cd /root/carsdedo

# Clone backend repository
git clone https://github.com/Raj602-stack/carsdedo-backend backend
cd backend
```

## Step 2: Verify CSV Files

All CSV data files are included in the repository. Verify they exist:

```bash
ls -la backend/csv/
```

You should see 12 CSV files:
- dealers.csv
- cars.csv
- car_images.csv
- car_highlights.csv
- car_specs.csv
- car_features.csv
- car_reasons.csv
- inspection_sections.csv
- inspection_subsections.csv
- inspection_items.csv
- car_inspection_scores.csv
- car_subsection_remarks.csv

## Step 3: Create Environment File

```bash
# Copy example env file
cp ENV_TEMPLATE.txt .env

# Edit with your production values
nano .env
```

**Important values to set in `.env`:**

```env
DJANGO_SECRET_KEY=<generate-a-strong-secret-key>
DJANGO_DEBUG=0
ALLOWED_HOSTS=72.62.247.243,api.carsdedo.com
POSTGRES_PASSWORD=<strong-database-password>
```

**Generate a strong secret key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Step 4: Set Up Docker Compose

The project includes `docker-compose.vps.yml` optimized for VPS deployment.

```bash
# From /root/carsdedo/backend directory
docker compose -f docker-compose.vps.yml up -d --build
```

## Step 5: Verify Deployment

```bash
# Check container status
docker compose -f docker-compose.vps.yml ps

# View logs
docker compose -f docker-compose.vps.yml logs -f backend

# Test API endpoint
curl http://localhost:8000/api/cars/
```

## Step 6: Import Data (Required)

Import all CSV data (cars, dealers, images, specs, features, etc.):

```bash
# Option 1: Using the import script
docker compose -f docker-compose.vps.yml exec backend bash /code/import_data.sh

# Option 2: Direct command
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py import_all_data
```

This will import:
- ✅ Dealers
- ✅ Cars (20 cars with all details)
- ✅ Car Images
- ✅ Car Highlights
- ✅ Car Specifications
- ✅ Car Features
- ✅ Reasons to Buy
- ✅ Inspection Sections & Subsections
- ✅ Inspection Items
- ✅ Inspection Section Scores
- ✅ Subsection Remarks

**Verify data import:**
```bash
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py shell -c "from cars.models import Car, Dealer; print(f'Cars: {Car.objects.count()}, Dealers: {Dealer.objects.count()}')"
```

## Step 7: Create Superuser (Optional)

```bash
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py createsuperuser
```

Or set in `.env`:
```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@carsdedo.com
DJANGO_SUPERUSER_PASSWORD=your-password
```

## Step 8: Configure Nginx (For Domain + HTTPS)

Create Nginx configuration at `/etc/nginx/sites-available/carsdedo-api`:

```nginx
server {
    listen 80;
    server_name api.carsdedo.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
ln -s /etc/nginx/sites-available/carsdedo-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## Step 9: SSL Certificate (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d api.carsdedo.com
```

## Useful Commands

### View Logs
```bash
docker compose -f docker-compose.vps.yml logs -f backend
docker compose -f docker-compose.vps.yml logs -f db
```

### Restart Services
```bash
docker compose -f docker-compose.vps.yml restart backend
docker compose -f docker-compose.vps.yml restart
```

### Stop Services
```bash
docker compose -f docker-compose.vps.yml down
```

### Backup Database
```bash
docker compose -f docker-compose.vps.yml exec db pg_dump -U carsdedo carsdedo > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Update Code
```bash
cd /root/carsdedo/backend
git pull
docker compose -f docker-compose.vps.yml up -d --build
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py migrate
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, change it in `docker-compose.vps.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### Database Connection Issues
Check database logs:
```bash
docker compose -f docker-compose.vps.yml logs db
```

### Static Files Not Loading
Run collectstatic:
```bash
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py collectstatic --noinput
```

### Permission Issues
Ensure media directory is writable:
```bash
chmod -R 755 /root/carsdedo/backend/backend/media
```

## Production Checklist

- [ ] Strong `DJANGO_SECRET_KEY` set
- [ ] `DJANGO_DEBUG=0`
- [ ] Strong database password set
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] CORS settings configured for frontend domain
- [ ] Nginx configured and SSL certificate installed
- [ ] Database backups configured
- [ ] Firewall rules configured (allow 80, 443, 22)
- [ ] Monitoring/logging set up (optional)

## API Endpoints

Once deployed, your API will be available at:
- `http://72.62.247.243:8000/api/cars/` (direct)
- `https://api.carsdedo.com/api/cars/` (with domain + SSL)
