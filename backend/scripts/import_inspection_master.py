import csv
from cars.models import InspectionSection, InspectionSubSection

CSV_SECTIONS = "/code/backend/csv/inspection_sections.csv"
CSV_SUBSECTIONS = "/code/backend/csv/inspection_subsections.csv"

def run():
    with open(CSV_SECTIONS, newline="") as f:
        for r in csv.DictReader(f):
            section, created = InspectionSection.objects.get_or_create(
                key=r["key"], 
                defaults={
                    "title": r["title"],
                    "description": r.get("description", ""),
                }
            )
            # Update description if section already exists
            if not created:
                section.description = r.get("description", "")
                section.title = r["title"]
                section.save()

    with open(CSV_SUBSECTIONS, newline="") as f:
        for r in csv.DictReader(f):
            if not r.get("section_key") or not r.get("key"):
                continue
            try:
                section = InspectionSection.objects.get(key=r["section_key"])
                subsection, created = InspectionSubSection.objects.get_or_create(
                    section=section,
                    key=r["key"],
                    defaults={
                        "title": r["title"],
                        "order": int(r.get("order", 0)),
                        "remarks": r.get("remarks", ""),
                    },
                )
                # Update order if subsection already exists
                if not created:
                    subsection.title = r["title"]
                    subsection.order = int(r.get("order", 0))
                    subsection.remarks = r.get("remarks", "")
                    subsection.save()
            except InspectionSection.DoesNotExist:
                print(f"❌ Section not found: {r['section_key']}")

    print("✅ Inspection sections imported")