import csv
from cars.models import Car, CarImage, CarImageCategory

CSV_PATH = "/code/backend/csv/car_images.csv"


def run():
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        print("CSV columns:", reader.fieldnames)

        for r in reader:
            car_code = r.get("car_code")
            if not car_code:
                print("❌ Missing car_code, skipping row")
                continue

            car = Car.objects.filter(car_code=car_code).first()
            if not car:
                print(f"❌ Car not found for code: {car_code}")
                continue

            category_key = r.get("category_key")
            category_label = r.get("category_label", category_key)

            category, _ = CarImageCategory.objects.get_or_create(
                key=category_key,
                defaults={"label": category_label},
            )

            image_path = r.get("image")
            if not image_path:
                print("⚠️ Missing image path, skipping")
                continue

            CarImage.objects.create(
                car=car,
                category=category,
                image=image_path.strip(),
                caption=r.get("caption", ""),
                sort_order=int(r.get("sort_order") or 0),
            )

            print(f"✅ Image added → {car_code} | {image_path}")

    print("🎉 Car images import completed")