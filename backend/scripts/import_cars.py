import csv
from cars.models import Car, Dealer

def run():
    with open("/code/backend/csv/cars.csv") as f:
        reader = csv.DictReader(f)

        for r in reader:
            dealer = Dealer.objects.get(dealer_code=r["dealer_code"])

            car, created = Car.objects.update_or_create(
                car_code=r["car_code"],
                defaults={
                    "dealer": dealer,
                    "title": r["title"],
                    "brand": r.get("brand", ""),
                    "model": r.get("model", ""),
                    "year": int(r["year"]) if r["year"] else None,
                    "price": r["price"],
                    "km": int(r["km"]) if r["km"] else None,
                    "fuel": r.get("fuel", ""),
                    "transmission": r.get("transmission", ""),
                    "body": r.get("body", ""),
                    "city": r.get("city", ""),
                    "colorKey": r.get("colorKey", ""),
                    "registration_number": r.get("registration_number", ""),
                    "tags": eval(r.get("tags", "[]")),
                    "metadata": eval(r.get("metadata", "{}")),
                }
            )

            print("✅", "Created" if created else "Updated", car.car_code)