# Quick VPS Deployment Commands

## On Your VPS (72.62.247.243)

```bash
# 1. SSH into VPS
ssh root@72.62.247.243

# 2. Clone repository
cd /root
git clone https://github.com/Raj602-stack/carsdedo-backend backend
cd backend

# 3. Verify CSV files are present (they should be in the repo)
ls -la backend/csv/*.csv
# Should show 12 CSV files

# 4. Create .env file (copy from ENV_TEMPLATE.txt)
cat > .env << 'EOF'
DJANGO_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DJANGO_DEBUG=0
ALLOWED_HOSTS=72.62.247.243,localhost,127.0.0.1,api.carsdedo.com
POSTGRES_DB=carsdedo
POSTGRES_USER=carsdedo
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432
CORS_ALLOWED_ORIGINS=https://carsdedo.com,https://www.carsdedo.com
EOF

# Edit .env and set actual values (especially SECRET_KEY and POSTGRES_PASSWORD)
nano .env

# 5. Deploy
docker compose -f docker-compose.vps.yml up -d --build

# 6. Check status
docker compose -f docker-compose.vps.yml ps
docker compose -f docker-compose.vps.yml logs -f backend

# 7. Test API
curl http://localhost:8000/api/cars/

# 8. Import all CSV data (cars, dealers, images, specs, features, etc.)
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py import_all_data

# 9. Verify data import
docker compose -f docker-compose.vps.yml exec backend python backend/manage.py shell -c "from cars.models import Car, Dealer; print(f'Cars: {Car.objects.count()}, Dealers: {Dealer.objects.count()}')"
```

## Generate Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Generate Database Password

```bash
openssl rand -base64 32
```
