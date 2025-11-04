# Data Schema Documentation

This document describes the expected schema for all data files used in the Cannabis Analytics Dashboard.

## Overview

The application requires four data files in the `data/` directory:
1. `Dispensaries.csv` - Dispensary license information
2. `Dispensary_Density.csv` - Population-adjusted density metrics
3. `Tweet_Sentiment.csv` - Social media sentiment data
4. `California_County_Boundaries.geojson` - County geographic boundaries

## File Schemas

### Dispensaries.csv

**Description**: Contains detailed information about cannabis retail licenses in California, including location, license type, and temporal data.

**Required Columns**:
- `County` (string): County name (e.g., "Los Angeles County" or "Los Angeles")
  - Will be normalized to remove " County" suffix if present
  - Used for geographic analysis and merging with other datasets

**Additional Columns** (present in dataset):
- `Year` (integer): Year of license data
  - If not present, will be derived from `License_Date`
- `Month` (integer): Month of license data
- `Address` (string): Physical address of dispensary
- `Dispensary Name` (string): Name of the dispensary business
- `License Number` (string): Unique license identifier
- `License Term` (string): Term of the license (e.g., "Annual")
- `License Designation` (string): License designation type
- `Rec License` (0/1): Binary indicator for recreational license
- `Medical` (0/1): Binary indicator for medical license
- `License Type` (string): Type of license (e.g., "Commercial - Retailer")
- `Non-Storefront` (0/1): Binary indicator for non-storefront location
- `License_Date` (date/string): Date license was issued
  - Used to derive `Year` column if `Year` is not present

**Validation**:
- File must exist and contain data
- `County` column must be present
- Rows should not be empty
- `Year` or `License_Date` should be present for temporal analysis

**Example**:
```csv
Year,Month,County,Address,Dispensary Name,License Number,License Term,License Designation,Rec License,Medical,License Type,Non-Storefront
2020,1,Los Angeles County,17499 Adelanto RD,"Jet Room, Inc.",C10-0000057-LIC,Annual,Adult-Use and Medicinal,1,1,Commercial -  Retailer,0
```

---

### Dispensary_Density.csv

**Description**: Population-adjusted metrics for cannabis retailer density by county and year.

**Required Columns**:
- `County` (string): County name
  - Should match format used in Dispensaries.csv
  - Will be normalized for matching
- `Dispensary_PerCapita` (float): Dispensaries per 100,000 residents
  - Used for density visualizations and analysis
  - Must be numeric (no string values)

**Additional Columns** (present in dataset):
- `Year` (string/integer): Year of data
- `Dispensary_Count` (integer): Total count of dispensaries in county
- `Population` (integer): County population
  - Used for population-weighted analysis
  - Required for opportunity scoring in Geographic Analysis page

**Validation**:
- File must exist and contain data
- Both `County` and `Dispensary_PerCapita` columns must be present
- `Dispensary_PerCapita` values must be numeric
- `Population` column recommended for full functionality

**Example**:
```csv
Year,County,Dispensary_Count,Population,Dispensary_PerCapita
2020,Alameda County,76,1682331,4.5175414350684
```

---

### Tweet_Sentiment.csv

**Description**: Social media sentiment data related to cannabis, including sentiment scores from various models.

**Required Columns**:
- `BERT_Sentiment` (numeric or string): Sentiment score from BERT model
  - Accepts numeric values (-1.0 to 1.0)
  - Accepts star ratings ("1 star" to "5 stars") which are converted to -1.0 to 1.0 scale
    - "5 star" → 1.0
    - "3 star" → 0.0
    - "1 star" → -1.0
  - Invalid or missing values converted to 0.0

**Additional Columns** (present in dataset):
- `Year` (integer): Year of tweet/post
- `Month` (integer): Month of tweet/post
- `County` (string): County associated with tweet
- `State` (string): State (should be "California")
- `Key word` (string): Cannabis-related keyword that triggered inclusion
- `Cleaned_Content` (string): Cleaned text content of tweet
- `VADER_Sentiment` (float): Sentiment score from VADER model
- `Predictions` (integer): Prediction category
- `GPT_Sentiment` (string): Sentiment from GPT model

**Date Columns** (at least one recommended):
- `Tweet_Date` (datetime): Date of tweet (preferred column name)
- `Created_At` (datetime): Alternative date column name
- `Date` (datetime): Alternative date column name
  - If none present, synthetic dates will be created starting from 2020-01-01
  - **Warning**: User will be notified if synthetic dates are used

**Validation**:
- File must exist and contain data
- `BERT_Sentiment` column must be present
- At least one date column recommended (synthetic dates created if missing with warning)
- `County` column recommended for county-level sentiment analysis

**Example**:
```csv
Year,Month,County,State,Key word,Cleaned_Content,VADER_Sentiment,BERT_Sentiment,Predictions,GPT_Sentiment
2020,1,Alameda,California,joint,"note i previously had tilda swinton on this list",0,3 stars,1,-1
```

---

### California_County_Boundaries.geojson

**Description**: GeoJSON FeatureCollection containing polygon geometries for California counties.

**Required Structure**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "NAME": "County Name",
        ...
      },
      "geometry": {
        "type": "Polygon" or "MultiPolygon",
        "coordinates": [...]
      }
    }
  ]
}
```

**Required Properties**:
- Root object must be `type: "FeatureCollection"`
- Must contain `features` array
- Each feature must have:
  - `type: "Feature"`
  - `properties` object with `NAME` property (county name)
  - `geometry` object with valid GeoJSON geometry

**Properties.NAME**:
- Should contain county name without " County" suffix for matching
- Examples: "Los Angeles", "San Francisco", "Alameda"
- Used as the key for matching with other datasets via `featureidkey="properties.NAME"`

**Validation**:
- File must exist
- Valid JSON structure
- Valid GeoJSON format (FeatureCollection with features array)
- Each feature must have geometry and properties with NAME

**Note**: County names in properties.NAME should match the normalized county names from CSV files (without " County" suffix).

---

## Data Loading Process

### Automatic Processing

The `load_data()` function in `app/utils/data_loader.py` automatically:

1. **Validates Files**:
   - Checks all required files exist
   - Reports missing files with full paths

2. **Validates Columns**:
   - Checks required columns exist in each CSV
   - Reports missing columns with specific error messages

3. **Processes Data**:
   - Converts sentiment scores to consistent numeric scale
   - Parses dates from multiple possible column names
   - Creates synthetic dates if none present (with warning)
   - Normalizes county names for matching

4. **Returns Dictionary**:
   ```python
   {
       "dispensaries": pd.DataFrame,
       "density": pd.DataFrame,
       "tweet_sentiment": pd.DataFrame,
       "ca_counties": dict  # GeoJSON object
   }
   ```

### County Name Normalization

County names are normalized using `normalize_county_name()` from `app/utils/data_utils.py`:

```python
from utils.data_utils import normalize_county_name

# "Los Angeles County" → "Los Angeles"
# "Los Angeles" → "Los Angeles"
# "  San Diego County  " → "San Diego"
```

Use this function when:
- Matching counties across datasets
- Preparing data for GeoJSON matching
- Creating county-based aggregations

## Data Update Instructions

### Adding New Data Files

1. **Export Data**:
   - Export from source system in CSV format
   - Ensure column names match schema exactly
   - Verify data types match requirements

2. **Validate Data**:
   ```bash
   # Check for required columns
   head -1 new_data.csv

   # Verify no empty rows
   grep -v "^$" new_data.csv | wc -l

   # Check for county name consistency
   cut -d',' -f3 new_data.csv | sort | uniq
   ```

3. **Place Files**:
   - Place in `data/` directory
   - Use exact filenames as specified above
   - Backup old files before replacing

4. **Test Loading**:
   ```python
   from app.utils.data_loader import load_data
   data = load_data()
   # Should load without errors
   ```

### Updating Existing Data

When updating existing data files:

1. **Maintain Schema**:
   - Keep all column names identical
   - Maintain data types
   - Preserve county name format

2. **Validate Before Deployment**:
   - Run the application locally
   - Check all visualizations load
   - Verify no error messages appear

3. **Update Documentation**:
   - Update `README.md` with data version/date
   - Note any schema changes in commit message
   - Update `DATA_SCHEMA.md` if columns change

### Adding New Columns

To add new columns to existing files:

1. Add column to CSV with appropriate values
2. Update this DATA_SCHEMA.md file
3. Update validation in `data_loader.py` if column is required
4. Update visualizations to use new column

## Common Issues and Solutions

### Issue: "County not found in GeoJSON"

**Cause**: County name mismatch between CSV and GeoJSON

**Solution**:
```python
# Check county names in CSV
df['County'].unique()

# Check county names in GeoJSON
data['ca_counties']['features'][0]['properties']['NAME']

# Normalize both using normalize_county_name()
```

### Issue: "BERT_Sentiment has non-numeric values"

**Cause**: Sentiment column contains unexpected strings

**Solution**:
- The `convert_sentiment_score()` function handles "star" formats
- Other string values will be converted to 0.0
- Verify source data format matches expectations

### Issue: "No date column found - using synthetic dates"

**Cause**: Tweet data missing all recognized date columns

**Solution**:
- Add column named `Tweet_Date`, `Created_At`, or `Date`
- Format as YYYY-MM-DD or other pandas-parseable format
- Or accept synthetic dates (data will still load but temporal analysis may be inaccurate)

### Issue: "Dispensary_PerCapita column not found"

**Cause**: Required column missing or renamed

**Solution**:
- Verify exact spelling: `Dispensary_PerCapita` (case-sensitive)
- Check for extra spaces or special characters
- Rename column to match expected name

## Testing Data Files

Use these commands to verify data integrity:

```bash
# Check CSV structure
head -5 data/Dispensaries.csv
head -5 data/Dispensary_Density.csv
head -5 data/Tweet_Sentiment.csv

# Check GeoJSON validity
cat data/California_County_Boundaries.geojson | python -m json.tool > /dev/null && echo "Valid JSON"

# Count records
wc -l data/*.csv

# Check for required columns
head -1 data/Dispensaries.csv | grep "County"
head -1 data/Dispensary_Density.csv | grep "Dispensary_PerCapita"
head -1 data/Tweet_Sentiment.csv | grep "BERT_Sentiment"
```

## Data Privacy and Security

When working with data files:

- **No PII**: Ensure no personally identifiable information in datasets
- **Business Sensitivity**: Retailer data may be business-sensitive
- **Public Data**: Only use publicly available data
- **Compliance**: Ensure CCPA and relevant data regulations are met
- **Gitignore**: If data becomes sensitive, add to `.gitignore`

See [SECURITY.md](SECURITY.md) for more information.

---

**Last Updated**: November 2025
**Version**: 1.0
**Maintainer**: Project team
