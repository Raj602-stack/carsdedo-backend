"""
Master script to import all car data from CSV files
Run this from Django shell: python backend/manage.py shell < backend/scripts/import_all_data.py
Or use: python backend/manage.py shell -c "exec(open('backend/scripts/import_all_data.py').read())"
"""

import os
import sys
import django

# Setup Django
sys.path.append('/code/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scripts.import_dealers import run as import_dealers
from scripts.import_cars import run as import_cars
from scripts.import_car_images import run as import_car_images
from scripts.import_car_highlights import run as import_car_highlights
from scripts.import_car_specs import run as import_car_specs
from scripts.import_car_features import run as import_car_features
from scripts.import_car_reasons import run as import_car_reasons

def main():
    print("=" * 60)
    print("🚀 Starting Complete Data Import")
    print("=" * 60)
    
    try:
        # Step 1: Import Dealers
        print("\n📋 Step 1: Importing Dealers...")
        import_dealers()
        
        # Step 2: Import Cars
        print("\n🚗 Step 2: Importing Cars...")
        import_cars()
        
        # Step 3: Import Car Images
        print("\n🖼️  Step 3: Importing Car Images...")
        import_car_images()
        
        # Step 4: Import Car Highlights
        print("\n✨ Step 4: Importing Car Highlights...")
        import_car_highlights()
        
        # Step 5: Import Car Specs
        print("\n⚙️  Step 5: Importing Car Specs...")
        import_car_specs()
        
        # Step 6: Import Car Features
        print("\n🎯 Step 6: Importing Car Features...")
        import_car_features()
        
        # Step 7: Import Car Reasons
        print("\n💡 Step 7: Importing Car Reasons to Buy...")
        import_car_reasons()
        
        print("\n" + "=" * 60)
        print("✅ All Data Imported Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
