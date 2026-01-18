import csv
from pathlib import Path
from django.db import transaction
from cars.models import Car, CarFeature, FeatureCategory

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "csv" / "car_features.csv"


@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            category_key = r.get("category_key")
            name = r.get("name")

            if not car_code or not category_key or not name:
                print("❌ Missing required fields, skipping:", r)
                continue

            try:
                car = Car.objects.get(car_code=car_code)
            except Car.DoesNotExist:
                print(f"❌ Car not found: {car_code}")
                continue

            category, _ = FeatureCategory.objects.get_or_create(
                key=category_key.strip(),
                defaults={
                    "title": (r.get("category_title") or category_key).strip().title()
                },
            )

            feature, created = CarFeature.objects.get_or_create(
                car=car,
                category=category,
                name=name.strip(),
                defaults={
                    "status": r.get("status", "flawless").strip(),
                }
            )
            # Update status if feature already exists
            if not created:
                feature.status = r.get("status", "flawless").strip()
                feature.save()

            print(
                "🆕 Created" if created else "⏭️ Skipped",
                f"feature '{name}' for {car_code}"
            )

    print("🎉 Car features import completed safely")
