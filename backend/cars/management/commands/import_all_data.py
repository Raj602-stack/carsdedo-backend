"""
Django management command to import all car data
Usage: python backend/manage.py import_all_data
"""

import sys
import os
from django.core.management.base import BaseCommand

# Get the backend directory (where manage.py is)
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
scripts_dir = os.path.join(backend_dir, 'scripts')
sys.path.insert(0, scripts_dir)

from import_dealers import run as import_dealers
from import_cars import run as import_cars
from import_car_images import run as import_car_images
from import_car_highlights import run as import_car_highlights
from import_car_specs import run as import_car_specs
from import_car_features import run as import_car_features
from import_car_reasons import run as import_car_reasons
from import_inspection_master import run as import_inspection_master
from import_inspection_items import run as import_inspection_items
from import_car_inspection_scores import run as import_car_inspection_scores
from import_car_subsection_remarks import run as import_car_subsection_remarks


class Command(BaseCommand):
    help = 'Import all car data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🚀 Starting Complete Data Import"))
        self.stdout.write("=" * 60)
        
        try:
            # Step 1: Import Dealers
            self.stdout.write("\n📋 Step 1: Importing Dealers...")
            import_dealers()
            
            # Step 2: Import Cars
            self.stdout.write("\n🚗 Step 2: Importing Cars...")
            import_cars()
            
            # Step 3: Import Car Images
            self.stdout.write("\n🖼️  Step 3: Importing Car Images...")
            import_car_images()
            
            # Step 4: Import Car Highlights
            self.stdout.write("\n✨ Step 4: Importing Car Highlights...")
            import_car_highlights()
            
            # Step 5: Import Car Specs
            self.stdout.write("\n⚙️  Step 5: Importing Car Specs...")
            import_car_specs()
            
            # Step 6: Import Car Features
            self.stdout.write("\n🎯 Step 6: Importing Car Features...")
            import_car_features()
            
            # Step 7: Import Car Reasons
            self.stdout.write("\n💡 Step 7: Importing Car Reasons to Buy...")
            import_car_reasons()
            
            # Step 8: Import Inspection Master Data
            self.stdout.write("\n🔍 Step 8: Importing Inspection Sections & Subsections...")
            import_inspection_master()
            
            # Step 9: Import Inspection Items
            self.stdout.write("\n✅ Step 9: Importing Inspection Items...")
            import_inspection_items()
            
            # Step 10: Import Inspection Section Scores
            self.stdout.write("\n📊 Step 10: Importing Inspection Section Scores...")
            import_car_inspection_scores()
            
            # Step 11: Import Subsection Remarks (optional)
            self.stdout.write("\n📝 Step 11: Importing Subsection Remarks...")
            import_car_subsection_remarks()
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ All Data Imported Successfully!"))
            self.stdout.write("=" * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error during import: {e}"))
            import traceback
            traceback.print_exc()
            raise
