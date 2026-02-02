import csv
import ast
from datetime import datetime
from pathlib import Path
from cars.models import Car, Dealer


# Resolve project base directory safely
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "csv" / "cars.csv"


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def run():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row_num, r in enumerate(reader, start=1):
            try:
                # 🔹 Dealer mapping
                dealer = Dealer.objects.get(dealer_code=r["dealer_code"])

                car, created = Car.objects.update_or_create(
                    car_code=r["car_code"],
                    defaults={
                        "dealer": dealer,

                        # --- Core info ---
                        "title": r["title"],
                        "brand": r.get("brand", ""),
                        "model": r.get("model", ""),
                        "year": int(r["year"]) if r.get("year") else None,

                        # --- Pricing ---
                        "price": float(r["price"]) if r.get("price") else 0,
                        "discount_price": float(r["discount_price"]) if r.get("discount_price") else None,

                        "emi": r.get("emi", "").strip(),

                        # --- Usage ---
                        "km": int(r["km"]) if r.get("km") else None,
                        "owner_count": int(r.get("owner_count", 1)),

                        # --- Status ---
                        "availability_status": r.get("availability_status", "available"),

                        # --- Insurance ---
                        "insurance_type": r.get("insurance_type", ""),
                        "insurance_valid_till": parse_date(r.get("insurance_valid_till")),

                        # --- Vehicle details ---
                        "fuel": r.get("fuel", ""),
                        "transmission": r.get("transmission", ""),
                        "body": r.get("body", ""),
                        "seats": int(r.get("seats")) if r.get("seats") else None,
                        "city": r.get("city", ""),
                        "rto": r.get("rto", ""),
                        "colorKey": r.get("colorKey", ""),
                        "registration_number": r.get("registration_number", ""),

                        # --- JSON fields (SAFE parsing) ---
                        "tags": ast.literal_eval(r.get("tags", "[]")),
                        "metadata": ast.literal_eval(r.get("metadata", "{}")),
                    }
                )

                print(
                    f"✅ Row {row_num}:",
                    "Created" if created else "Updated",
                    car.car_code
                )

            except Dealer.DoesNotExist:
                print(f"❌ Row {row_num}: Dealer not found → {r.get('dealer_code')}")

            except Exception as e:
                print(f"❌ Row {row_num}: Error importing car {r.get('car_code')} → {e}")
