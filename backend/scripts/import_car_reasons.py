import csv
from django.db import transaction
from cars.models import Car, CarReasonToBuy

CSV_PATH = "/code/backend/csv/car_reasons.csv"

@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            title = r.get("title")

            if not car_code or not title:
                print("❌ Missing required fields, skipping:", r)
                continue

            try:
                car = Car.objects.get(car_code=car_code)
            except Car.DoesNotExist:
                print(f"❌ Car not found: {car_code}")
                continue

            obj, created = CarReasonToBuy.objects.update_or_create(
                car=car,
                title=title.strip(),
                defaults={
                    "description": r.get("description", "").strip(),
                    "sort_order": int(r.get("sort_order") or 0),
                }
            )

            print(
                "🆕 Created" if created else "🔄 Updated",
                f"reason '{title}' for {car_code}"
            )

    print("🎉 Reasons import completed safely")
