import csv
from django.db import transaction
from cars.models import Car, CarSpec, SpecCategory

CSV_PATH = "/code/backend/csv/car_specs.csv"

@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            category_key = r.get("category_key")
            label = r.get("label")

            if not car_code or not category_key or not label:
                print("❌ Missing required fields, skipping:", r)
                continue

            try:
                car = Car.objects.get(car_code=car_code)
            except Car.DoesNotExist:
                print(f"❌ Car not found: {car_code}")
                continue

            category, _ = SpecCategory.objects.get_or_create(
                key=category_key.strip(),
                defaults={
                    "title": (r.get("category_title") or category_key).strip().title()
                },
            )

            obj, created = CarSpec.objects.update_or_create(
                car=car,
                category=category,
                label=label.strip(),
                defaults={
                    "value": (r.get("value") or "").strip()
                }
            )

            print(
                "🆕 Created" if created else "🔄 Updated",
                f"spec '{label}' for {car_code}"
            )

    print("🎉 Car specs import completed safely")
