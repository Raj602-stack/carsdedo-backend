# Data Import Guide

This guide explains how to import the dummy car data (20 cars with images, highlights, specs, features, and reasons) into your database.

## What's Included

✅ **20 Cars** - Variety of brands (Jaguar, BMW, Honda, Maruti, Hyundai, Toyota, etc.)
✅ **4 Dealers** - Premium and standard tier dealers
✅ **Car Images** - Multiple images per car (exterior, interior views)
✅ **Car Highlights** - Key selling points for each car
✅ **Car Specs** - Engine, mileage, and technical specifications
✅ **Car Features** - Safety, comfort, and technology features
✅ **Reasons to Buy** - Detailed reasons why customers should buy each car

## Import Methods

### Method 1: Using Django Management Command (Recommended)

If you're running the project with Docker:

```bash
# Start the containers
docker compose up -d

# Run the import command
docker compose exec web python backend/manage.py import_all_data
```

If running locally:

```bash
cd backend
python manage.py import_all_data
```

### Method 2: Import Individual Components

You can also import data components individually:

```bash
# Import dealers
docker compose exec web python backend/manage.py shell -c "from scripts.import_dealers import run; run()"

# Import cars
docker compose exec web python backend/manage.py shell -c "from scripts.import_cars import run; run()"

# Import car images
docker compose exec web python backend/manage.py shell -c "from scripts.import_car_images import run; run()"

# Import highlights
docker compose exec web python backend/manage.py shell -c "from scripts.import_car_highlights import run; run()"

# Import specs
docker compose exec web python backend/manage.py shell -c "from scripts.import_car_specs import run; run()"

# Import features
docker compose exec web python backend/manage.py shell -c "from scripts.import_car_features import run; run()"

# Import reasons
docker compose exec web python backend/manage.py shell -c "from scripts.import_car_reasons import run; run()"
```

### Method 3: Using Django Shell

```bash
docker compose exec web python backend/manage.py shell
```

Then in the shell:

```python
from scripts.import_dealers import run as import_dealers
from scripts.import_cars import run as import_cars
from scripts.import_car_images import run as import_car_images
from scripts.import_car_highlights import run as import_car_highlights
from scripts.import_car_specs import run as import_car_specs
from scripts.import_car_features import run as import_car_features
from scripts.import_car_reasons import run as import_car_reasons

# Run imports in order
import_dealers()
import_cars()
import_car_images()
import_car_highlights()
import_car_specs()
import_car_features()
import_car_reasons()
```

## CSV Files Location

All CSV files are located in: `backend/csv/`

- `dealers.csv` - Dealer information
- `cars.csv` - Car basic information (20 cars)
- `car_images.csv` - Car images with categories
- `car_highlights.csv` - Car highlights
- `car_specs.csv` - Car specifications
- `car_features.csv` - Car features
- `car_reasons.csv` - Reasons to buy

## Car Images

**Note:** The car images currently reference `cars/images/suv.png` as a placeholder. 

To add real images:
1. Place your car images in `backend/media/cars/images/`
2. Update `car_images.csv` with the actual image file paths
3. Re-run the import script

Example image paths:
- `cars/images/car001_front.jpg`
- `cars/images/car001_interior.jpg`
- `cars/images/car002_front.jpg`

## Verify Import

After importing, verify the data:

```bash
# Check cars count
docker compose exec web python backend/manage.py shell -c "from cars.models import Car; print(f'Total cars: {Car.objects.count()}')"

# Check dealers count
docker compose exec web python backend/manage.py shell -c "from cars.models import Dealer; print(f'Total dealers: {Dealer.objects.count()}')"

# Check images count
docker compose exec web python backend/manage.py shell -c "from cars.models import CarImage; print(f'Total images: {CarImage.objects.count()}')"
```

## API Endpoints

Once imported, you can access the data via:

- **List all cars:** `GET http://localhost:8000/api/cars/`
- **Get car detail:** `GET http://localhost:8000/api/cars/<car-uuid>/`

## Troubleshooting

### Issue: "Car not found" errors
- Make sure dealers are imported before cars
- Check that `car_code` in CSV files matches exactly

### Issue: Image paths not working
- Ensure images exist in `backend/media/cars/images/`
- Check file permissions
- Verify image paths in `car_images.csv` are correct

### Issue: Import fails partway through
- The scripts use transactions, so partial imports should rollback
- Check the error message for specific issues
- Verify CSV file format is correct (no extra commas, proper quotes)

## Adding More Data

To add more cars:
1. Add rows to `cars.csv` with new `car_code` values
2. Add corresponding rows to other CSV files (images, highlights, specs, features, reasons)
3. Re-run the import command

The import scripts use `update_or_create`, so re-running is safe and will update existing records.
