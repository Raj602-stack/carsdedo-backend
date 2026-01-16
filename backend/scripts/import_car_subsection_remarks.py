import csv
from django.db import transaction
from cars.models import Car, InspectionSubSection, CarInspectionSubSectionRemarks

CSV_PATH = "/code/backend/csv/car_subsection_remarks.csv"

@transaction.atomic
def run():
    # Check if CSV file exists
    try:
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            print("CSV columns:", reader.fieldnames)

            for r in reader:
                car_code = r.get("car_code")
                subsection_key = r.get("subsection_key")
                status = r.get("status", "").strip()
                remarks = r.get("remarks", "")

                if not all([car_code, subsection_key]):
                    print("❌ Missing required fields, skipping:", r)
                    continue

                try:
                    car = Car.objects.get(car_code=car_code)
                    subsection = InspectionSubSection.objects.get(key=subsection_key)
                except (Car.DoesNotExist, InspectionSubSection.DoesNotExist) as e:
                    print(f"❌ Reference not found: {e}")
                    continue

                obj, created = CarInspectionSubSectionRemarks.objects.update_or_create(
                    car=car,
                    subsection=subsection,
                    defaults={
                        "status": status if status else "",
                        "remarks": remarks.strip(),
                    }
                )

                print(
                    "🆕 Created" if created else "🔄 Updated",
                    f"remarks for {car_code} - {subsection_key}"
                )

        print("🎉 Car inspection subsection remarks import completed safely")
    except FileNotFoundError:
        print(f"⚠️  CSV file not found: {CSV_PATH}")
        print("   Skipping subsection remarks import (optional)")
