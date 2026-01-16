# Production Data Migration Guide

## ⚠️ Important: Data Persistence in Production

**Short Answer:** Your data will NOT be lost if you set up production correctly. However, you need to properly migrate your data from development to production.

## Understanding Data Storage

### Development (Local)
- Data is stored in Docker volumes (`postgres_data`)
- Data persists as long as Docker volumes exist
- Data is **separate** from your code

### Production (Hostinger/Other Hosting)
- You need to **migrate** your data from development to production
- Production database is **separate** from development database
- Data persists as long as the production database exists

## Data Migration Strategies

### Option 1: Export/Import Database (Recommended for Initial Setup)

#### Step 1: Export Data from Development

```bash
# Export database from your local Docker setup
docker compose exec db pg_dump -U your_db_user your_db_name > backup.sql

# Or export with specific format
docker compose exec db pg_dump -U your_db_user -F c your_db_name > backup.dump
```

#### Step 2: Import to Production

**If using Hostinger with PostgreSQL:**

1. **Create database on Hostinger:**
   - Log into Hostinger control panel
   - Create a PostgreSQL database
   - Note down: host, port, database name, username, password

2. **Update production `.env`:**
   ```env
   POSTGRES_HOST=your-hostinger-db-host
   POSTGRES_PORT=5432
   POSTGRES_DB=your_production_db_name
   POSTGRES_USER=your_production_db_user
   POSTGRES_PASSWORD=your_production_db_password
   ```

3. **Import data:**
   ```bash
   # On your production server
   psql -h your-hostinger-db-host -U your_production_db_user -d your_production_db_name < backup.sql
   
   # Or using pg_restore for custom format
   pg_restore -h your-hostinger-db-host -U your_production_db_user -d your_production_db_name backup.dump
   ```

### Option 2: Use Django Management Commands (Recommended for Ongoing Updates)

#### Step 1: Export Data as JSON/Fixtures

```bash
# Export all car-related data
docker compose exec web python backend/manage.py dumpdata cars > cars_data.json

# Export specific models
docker compose exec web python backend/manage.py dumpdata cars.Car cars.Dealer cars.CarImage > cars_export.json
```

#### Step 2: Import to Production

```bash
# On production server
python backend/manage.py loaddata cars_data.json
```

### Option 3: Re-import from CSV (Best for Fresh Start)

If you have all your data in CSV files (which you do!):

1. **Deploy your code to production**
2. **Run migrations:**
   ```bash
   python backend/manage.py migrate
   ```
3. **Import all data:**
   ```bash
   python backend/manage.py import_all_data
   ```

This is the **safest** method because:
- ✅ Uses your existing CSV files
- ✅ No data format issues
- ✅ Can be re-run anytime
- ✅ Works across different database versions

## Production Database Options

### Option A: Managed Database Service (Recommended)

**Best for:** Reliability, backups, scalability

**Options:**
- **Hostinger PostgreSQL** (if available)
- **AWS RDS** (Amazon)
- **DigitalOcean Managed Databases**
- **Heroku Postgres**
- **Railway PostgreSQL**

**Advantages:**
- ✅ Automatic backups
- ✅ High availability
- ✅ Easy scaling
- ✅ Managed by provider

### Option B: Docker Volume (For VPS)

**Best for:** Full control, cost-effective

**Setup:**
```yaml
# docker-compose.yml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /var/lib/postgresql/data  # Persistent path
```

**Important:** Set up regular backups!

## Backup Strategy

### 1. Automated Backups Script

Create `backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="your_db_name"
DB_USER="your_db_user"

# Create backup
docker compose exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql"
```

### 2. Schedule Automated Backups

```bash
# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /path/to/backup_db.sh
```

### 3. Manual Backup Before Deployment

```bash
# Always backup before deploying
docker compose exec db pg_dump -U your_user your_db > backup_before_deploy_$(date +%Y%m%d).sql
```

## Step-by-Step: Deploying to Hostinger

### Phase 1: Initial Setup (First Time)

1. **Prepare your production data:**
   ```bash
   # Export from development
   docker compose exec db pg_dump -U your_user your_db > production_backup.sql
   ```

2. **Set up production database on Hostinger:**
   - Create PostgreSQL database
   - Get connection details

3. **Deploy code:**
   ```bash
   # On Hostinger server
   git clone your-repo
   cd carsdedo_backend
   cp .env.example .env
   # Edit .env with production database credentials
   ```

4. **Run migrations:**
   ```bash
   python backend/manage.py migrate
   ```

5. **Import data:**
   ```bash
   # Option A: Import from SQL dump
   psql -h your-host -U user -d dbname < production_backup.sql
   
   # Option B: Re-import from CSV (recommended)
   python backend/manage.py import_all_data
   ```

6. **Create superuser:**
   ```bash
   python backend/manage.py createsuperuser
   ```

### Phase 2: Ongoing Updates

**For code updates (data stays safe):**
```bash
git pull
python backend/manage.py migrate  # Only runs new migrations
# Restart your application
```

**For data updates:**
```bash
# Update CSV files
# Then re-import
python backend/manage.py import_all_data
```

## Important Notes

### ✅ Data WILL Persist If:
- You use a managed database service
- You use Docker volumes properly
- You set up regular backups
- You migrate data correctly during initial setup

### ❌ Data WILL Be Lost If:
- You delete Docker volumes without backup
- You recreate database without importing data
- You don't migrate data from dev to production
- You use ephemeral storage without persistence

## Recommended Production Setup

### For Hostinger:

1. **Use Hostinger's PostgreSQL** (if available)
   - Most reliable
   - Automatic backups
   - Easy to manage

2. **Or use external managed database:**
   - AWS RDS
   - DigitalOcean Managed DB
   - Railway PostgreSQL

3. **Set up automated backups:**
   - Daily backups
   - Keep for 30 days
   - Test restore process

4. **Use environment variables:**
   - Never commit `.env` file
   - Use different credentials for production
   - Rotate passwords regularly

## Quick Checklist Before Production

- [ ] Export/backup development database
- [ ] Set up production database
- [ ] Update `.env` with production credentials
- [ ] Test database connection
- [ ] Run migrations on production
- [ ] Import data (CSV or SQL dump)
- [ ] Verify data in production
- [ ] Set up automated backups
- [ ] Test restore process
- [ ] Document database credentials securely

## Data Migration Commands Reference

```bash
# Export from development
docker compose exec db pg_dump -U user dbname > backup.sql

# Import to production
psql -h host -U user -d dbname < backup.sql

# Or use Django fixtures
python manage.py dumpdata > data.json
python manage.py loaddata data.json

# Or re-import from CSV (safest)
python manage.py import_all_data
```

## Need Help?

If you need assistance with:
- Setting up production database
- Migrating data
- Setting up backups
- Troubleshooting data issues

Just ask! I can help you with the specific steps for your hosting provider.
