import csv
from pathlib import Path
from cars.models import Dealer

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "csv" / "dealers.csv"

def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            Dealer.objects.get_or_create(
                dealer_code=row["dealer_code"],
                defaults={
                    "name": row["name"],
                    "phone": row.get("phone", ""),
                    "email": row.get("email", ""),
                    "address": row.get("address", ""),
                    "city": row.get("city", ""),
                    "state": row.get("state", ""),
                    "postal_code": row.get("postal_code", ""),
                    "tier": row.get("tier", "standard"),
                    "tags": eval(row.get("tags", "[]")),
                },
            )

    print("✅ Dealers imported")