# CSV Data Files

This directory contains all CSV data files that will be imported into the database during deployment.

## CSV Files Included

1. **dealers.csv** - Dealer information
2. **cars.csv** - Main car data (20 cars)
3. **car_images.csv** - Car images with categories
4. **car_highlights.csv** - Car highlights/selling points
5. **car_specs.csv** - Car specifications (4 categories)
6. **car_features.csv** - Car features (4 categories with status)
7. **car_reasons.csv** - Reasons to buy each car
8. **inspection_sections.csv** - Inspection main categories (5 sections)
9. **inspection_subsections.csv** - Inspection subcategories
10. **inspection_items.csv** - Individual inspection items
11. **car_inspection_scores.csv** - Car-specific inspection section scores
12. **car_subsection_remarks.csv** - Car-specific subsection remarks

## Import Process

All CSV files are automatically imported when you run:

```bash
python backend/manage.py import_all_data
```

Or during VPS deployment, the data is imported automatically via the deployment script.

## Data Summary

- **20 Cars** with complete details
- **4 Dealers** (premium and standard)
- **Multiple images** per car
- **Complete specifications** (dimension, engine, fuel, suspension)
- **Features** with status (flawless, little_flaw, damaged)
- **Inspection data** with scores, ratings, and remarks
- **Highlights and reasons** to buy

## Updating Data

To update data:
1. Edit the CSV files
2. Re-run the import command (it will update existing records)
3. Or delete specific records and re-import

## Note

These CSV files are tracked in git to ensure they're available on the VPS after deployment.
