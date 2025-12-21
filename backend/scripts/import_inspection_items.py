import csv
from django.db import transaction
from cars.models import Car, InspectionSubSection, InspectionItem

CSV_PATH = "/code/backend/csv/inspection_items.csv"

@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            subsection_key = r.get("subsection_key")
            name = r.get("name")

            if not all([car_code, subsection_key, name]):
                print("❌ Missing required fields, skipping:", r)
                continue

            try:
                car = Car.objects.get(car_code=car_code)
                subsection = InspectionSubSection.objects.get(key=subsection_key)
            except (Car.DoesNotExist, InspectionSubSection.DoesNotExist) as e:
                print("❌ Reference not found:", e)
                continue

            obj, created = InspectionItem.objects.update_or_create(
                car=car,
                subsection=subsection,
                name=name,
                defaults={
                    "status": r.get("status", "pending"),
                    "remarks": r.get("remarks", ""),
                }
            )

            print("🆕 Created" if created else "🔄 Updated", name)

    print("🎉 Inspection items import completed safely")
