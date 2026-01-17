# Push CSV Files to GitHub

The CSV files are now configured to be included in git. To push them to your repository:

## Steps

1. **Stage all CSV files:**
   ```bash
   git add backend/csv/*.csv
   git add .gitignore
   ```

2. **Commit the changes:**
   ```bash
   git commit -m "Add CSV data files for VPS deployment"
   ```

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```

## Verify CSV Files are Tracked

After pushing, verify on GitHub that all 12 CSV files are visible in the `backend/csv/` directory:

- ✅ dealers.csv
- ✅ cars.csv
- ✅ car_images.csv
- ✅ car_highlights.csv
- ✅ car_specs.csv
- ✅ car_features.csv
- ✅ car_reasons.csv
- ✅ inspection_sections.csv
- ✅ inspection_subsections.csv
- ✅ inspection_items.csv
- ✅ car_inspection_scores.csv
- ✅ car_subsection_remarks.csv

## Important Note

The `.gitignore` file has been updated to **include** CSV files (the ignore rule is commented out). This ensures all CSV data is available on the VPS after cloning the repository.
