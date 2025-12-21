import csv
from cars.models import InspectionSection, InspectionSubSection

def run():
    with open("backend/csv/inspection_sections.csv") as f:
        for r in csv.DictReader(f):
            InspectionSection.objects.get_or_create(
                key=r["key"], defaults={"title": r["title"]}
            )

    with open("backend/csv/inspection_subsections.csv") as f:
        for r in csv.DictReader(f):
            section = InspectionSection.objects.get(key=r["section_key"])
            InspectionSubSection.objects.get_or_create(
                section=section,
                key=r["key"],
                defaults={"title": r["title"]},
            )

    print("✅ Inspection sections imported")