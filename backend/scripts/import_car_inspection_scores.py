import csv
from pathlib import Path
from django.db import transaction
from cars.models import Car, InspectionSection, CarInspectionSectionScore

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "csv" / "car_inspection_scores.csv"


@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            section_key = r.get("section_key")
            score = r.get("score")
            rating = r.get("rating")
            remarks = r.get("remarks", "")

            if not all([car_code, section_key, score, rating]):
                print("❌ Missing required fields, skipping:", r)
                continue

            try:
                car = Car.objects.get(car_code=car_code)
                section = InspectionSection.objects.get(key=section_key)
            except (Car.DoesNotExist, InspectionSection.DoesNotExist) as e:
                print(f"❌ Reference not found: {e}")
                continue

            obj, created = CarInspectionSectionScore.objects.update_or_create(
                car=car,
                section=section,
                defaults={
                    "score": float(score),
                    "rating": rating.lower(),
                    "status": r.get("status", "").strip(),
                    "remarks": remarks.strip(),
                }
            )

            print(
                "🆕 Created" if created else "🔄 Updated",
                f"score {score} ({rating}) for {car_code} - {section_key}"
            )

    print("🎉 Car inspection section scores import completed safely")
