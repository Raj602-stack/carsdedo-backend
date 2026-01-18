

import csv
from pathlib import Path
from django.db import transaction
from cars.models import Car, CarHighlight

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "csv" / "car_highlights.csv"


@transaction.atomic
def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)

        for r in reader:
            car_code = r.get("car_code")
            text = r.get("text")

            if not car_code or not text:
                continue

            try:
                car = Car.objects.get(car_code=car_code)
            except Car.DoesNotExist:
                print("❌ Car not found:", car_code)
                continue

            highlight, created = CarHighlight.objects.get_or_create(
                car=car,
                text=text.strip()
            )

            print("🆕 Created" if created else "⏭️ Skipped", text)

    print("🎉 Car highlights import completed safely")
