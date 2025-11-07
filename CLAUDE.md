# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

California Cannabis Market Analytics Dashboard - A Streamlit-based web application providing comprehensive analytics and insights into California's cannabis retail market, combining dispensary data with social media sentiment analysis.

**Tech Stack**: Python >=3.10, Streamlit, Pandas, Plotly, Transformers (HuggingFace)

## Development Commands

### Running the Application
```bash
streamlit run app/Home.py
```

### Setup and Installation
```bash
# Install dependencies
poetry install

# Setup environment variables
cp .env.example .env
# Edit .env to add OPENAI_API_KEY
```

### Code Quality
```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8
poetry run pylint app/

# Run tests
poetry run pytest
```

## Architecture

### Streamlit Multi-Page App Structure
- **Entry Point**: `app/Home.py` - Main dashboard with overview metrics
- **Pages**: `app/pages/` - Individual analysis pages (numbered for ordering)
  - `01-Market Overview.py` - YoY growth, license breakdown
  - `02-Geographic Analysis.py` - Choropleth maps, regional analysis
  - `03-Social Insights.py` - Sentiment analysis, temporal trends
  - `04-Data Quality.py` - Data coverage and validation metrics
- **Plots**: `app/plots/` - Reusable Plotly visualization functions
- **Utils**: `app/utils/` - Shared utilities and data loading
  - `data_loader.py` - Centralized data loading with validation
  - `data_utils.py` - County name normalization utilities
  - `data_validation.py` - Comprehensive data quality validation
  - `filters.py` - Filter application logic
  - `error_messages.py` - User-friendly error displays
  - `generate_sidebar.py` - Sidebar generation
  - `plot_helpers.py` - Chart creation utilities
  - `load_geojson.py` - GeoJSON loading and validation
- **Config**: `config/.streamlit/` - Streamlit theming and configuration

### Key Architectural Patterns

#### Data Loading (Centralized)
Every page imports and calls the centralized data loader:
```python
from utils.data_loader import load_data
data = load_data()  # Returns dict with 'dispensaries', 'density', 'tweet_sentiment', 'ca_counties'
```

The `load_data()` function:
- Loads all CSV files from `data/` directory
- Processes sentiment scores (converts star ratings to -1 to 1 scale)
- Handles date parsing for tweet data
- Returns a dictionary with all datasets

#### Sidebar Filters (Consistent UX)
Every page uses the same sidebar generation:
```python
from utils.generate_sidebar import generate_sidebar
sidebar_filters = generate_sidebar()  # Provides consistent filtering UI
```

#### Filter Application (Consistent Logic)
Apply filters using centralized utilities from `utils/filters.py`:
```python
from utils.filters import apply_dispensary_filters, apply_sentiment_filters

# Apply filters to data
dispensaries = apply_dispensary_filters(data['dispensaries'], sidebar_filters)
sentiment = apply_sentiment_filters(data['tweet_sentiment'], sidebar_filters)
```

Filter functions available:
- `apply_dispensary_filters()` - Year, license type, county filters
- `apply_sentiment_filters()` - Year, county filters
- `apply_density_filters()` - Year, county filters
- `get_filter_summary()` - Get human-readable filter description
- `has_active_filters()` - Check if any filters are applied

#### Visualization Functions (Modular)
Chart creation utilities in `app/utils/plot_helpers.py`:

```python
from utils.plot_helpers import (
    create_choropleth_map,
    create_bar_chart,
    create_line_chart,
    create_histogram,
    create_scatter_plot,
    get_california_map_layout
)

# Example: Create a bar chart
fig = create_bar_chart(
    data=df,
    x="County",
    y="Count",
    title="Dispensaries by County",
    x_label="County",
    y_label="Number of Dispensaries",
    color=GREEN_PALETTE["primary"]
)
```

Available functions:
- `create_choropleth_map()` - County-level choropleth with CA boundaries
- `create_bar_chart()` - Categorical comparisons
- `create_line_chart()` - Temporal trends
- `create_histogram()` - Distribution visualization
- `create_scatter_plot()` - Correlation analysis
- `get_california_map_layout()` - Standard CA map layout configuration

#### Data Processing
- **Sentiment Conversion**: The `data_loader.py` contains `convert_sentiment_score()` that normalizes various sentiment formats to a consistent -1 to 1 scale
- **Data Caching**: `load_data()` uses `@st.cache_data` decorator for performance - data loads once per session
- **Data Validation**: Comprehensive validation checks for file existence, required columns, and data integrity
- **County Name Normalization**: Use `data_utils.py` for consistent county name handling:
  ```python
  from utils.data_utils import normalize_county_name, add_county_suffix, normalize_dataframe_counties

  # Remove " County" suffix and trim whitespace
  clean_name = normalize_county_name("Los Angeles County")  # Returns "Los Angeles"

  # Add " County" suffix
  full_name = add_county_suffix("Los Angeles")  # Returns "Los Angeles County"

  # Normalize entire DataFrame column
  df = normalize_dataframe_counties(df, column_name="County")
  ```
  **Why this matters**: GeoJSON features use "Los Angeles" while some data files use "Los Angeles County". Always normalize before joins/merges.
- **Regional Mapping**: Centralized in `app/config/regions.py` - use `CALIFORNIA_REGIONS` or `SIMPLE_REGIONS`

### Data Dependencies
All pages depend on these data files in `data/`:
- `Dispensaries.csv` - Retailer license information
- `Dispensary_Density.csv` - Population-adjusted metrics
- `Tweet_Sentiment.csv` - Social media sentiment data with BERT scores
- `California_County_Boundaries.geojson` - Geographic boundaries for choropleth maps

### Page Configuration Pattern
Every page includes:
```python
st.set_page_config(
    page_title="Page Name | Cannabis Analytics",
    page_icon="🌿",
    layout="wide"
)
```

### Configuration Module (NEW)
Centralized configuration available in `app/config/`:
- **Regions** (`app/config/regions.py`): California region definitions
  - `CALIFORNIA_REGIONS`: Detailed 3-region breakdown
  - `SIMPLE_REGIONS`: Simplified 4-region breakdown
  - `get_region_for_county()`: Helper function to map counties to regions
- **Theme** (`app/config/theme.py`): Plotly visualization styling
  - `PLOTLY_THEME`: Default template ("plotly_dark")
  - `GREEN_PALETTE`: Cannabis-themed color palette
  - `COLOR_SCALES`: Color scales for different chart types
  - `get_default_layout()`: Returns standard layout configuration
  - `apply_green_theme()`: Apply theme to any Plotly figure

### Plotly Theming
All visualizations should use the centralized theme configuration:
```python
from config.theme import get_default_layout, GREEN_PALETTE, COLOR_SCALES

fig.update_layout(**get_default_layout(height=500, title="My Chart"))
# Or use specific colors
fig.update_traces(marker_color=GREEN_PALETTE["primary"])
```

Legacy approach (still works but should migrate to config):
- `template="plotly_dark"` for consistent dark theme
- Green color scheme (`#4CAF50`, `#81C784`, `"Greens"` scale) for cannabis theme
- Transparent backgrounds: `paper_bgcolor="rgba(0,0,0,0)"`

## Important Development Notes

### Adding New Pages
1. Create file in `app/pages/` with numbered prefix (e.g., `04-New Page.py`)
2. Import and call `load_data()` and `generate_sidebar()`
3. Use `st.set_page_config()` at the top
4. Follow existing pattern for layout and visualizations

### Adding New Visualizations
1. Create function in `app/plots/` that returns a Plotly figure
2. Accept DataFrame and column names as parameters
3. Use the green color scheme and dark template
4. Make it reusable across multiple pages

### Working with Sentiment Data
- Sentiment scores are pre-processed by `data_loader.py`
- Already normalized to -1 to 1 scale via `convert_sentiment_score()`
- Handles star ratings (converts "5 star" to 1.0, "3 star" to 0.0, "1 star" to -1.0)
- Check for NaN values and handle with `.fillna(0)` if needed

### Working with Regional Data
Use the centralized region definitions instead of hardcoding:
```python
from config.regions import CALIFORNIA_REGIONS, get_region_for_county

# Get region for a county
region = get_region_for_county("Los Angeles")  # Returns "Southern California"

# Iterate over regions
for region, counties in CALIFORNIA_REGIONS.items():
    # Analyze each region
```

### GeoJSON Path Handling
**IMPORTANT**: Always use the centralized data loader for GeoJSON:
```python
from utils.data_loader import load_data

data = load_data()
ca_counties = data["ca_counties"]  # Use this for all choropleth maps
```

Do NOT manually load GeoJSON files or use hardcoded paths.

### Error Handling Pattern
Use standardized error displays from `utils/error_messages.py`:

```python
from utils.error_messages import (
    show_no_data_error,
    show_file_missing_error,
    show_column_missing_error,
    show_insufficient_data_warning,
    show_loading_error
)

# Example: Show friendly error when filters return no data
if filtered_data.empty:
    show_no_data_error(
        filter_info=sidebar_filters,
        page_name="Market Overview"
    )
    st.stop()
```

Available error functions:
- `show_no_data_error()` - When filters exclude all data
- `show_file_missing_error()` - When required data files don't exist
- `show_column_missing_error()` - When CSV columns are missing
- `show_insufficient_data_warning()` - When data is too sparse for analysis
- `show_loading_error()` - Generic data loading errors
- `show_correlation_warning()` - When correlation analysis has too few points
- `show_temporal_analysis_error()` - When time-series analysis fails

Each error includes:
- Clear problem explanation
- Why it happened (expandable)
- Step-by-step recovery instructions (expandable)

## Configuration

- **Poetry**: `pyproject.toml` - Dependency management, Black/isort settings
- **Streamlit**: `config/.streamlit/config.toml` - App theming (green color scheme)
- **Environment**: `.env` - Environment variables (OPENAI_API_KEY defined but LLM features not yet implemented)
- **App Config**: `app/config/` - Centralized application configuration
  - `regions.py`: California county-to-region mappings
  - `theme.py`: Plotly visualization theme and color palette
  - `env.py`: Environment variable management and configuration
    - `Config.get_api_key()` - Get OpenAI API key
    - `Config.validate()` - Validate environment setup
    - `Config.is_production()` - Check environment mode

## Testing Strategy

Comprehensive test suite in `tests/` directory with 7 test modules:
- Run all tests: `poetry run pytest`
- Run specific file: `poetry run pytest tests/test_filters.py`
- Run with coverage: `poetry run pytest --cov=app tests/`

**Test Files**:
- `test_data_loader.py` - Data loading, caching, sentiment conversion
- `test_config.py` - Region and theme configuration validation
- `test_data_utils.py` - County normalization, name validation
- `test_data_validation.py` - Data quality checks, ValidationResult class
- `test_filters.py` - Filter application logic
- `test_load_geojson.py` - GeoJSON loading and structure validation
- `test_plots/` - Visualization function tests

**Fixtures** (`tests/conftest.py`):
- `sample_dispensaries_data` - 6 rows of dispensary data
- `sample_density_data` - 6 rows of density data
- `sample_sentiment_data` - 6 rows with sentiment scores
- `sample_geojson` - Minimal valid GeoJSON structure
- `mock_data_dir` - Temporary data directory with all files

**Testing Guidelines**:
- Follow established code formatting (Black, isort)
- Use fixtures from `conftest.py` for sample data
- Test data transformations, not Streamlit UI components
- Mock Streamlit functions (`st.error`, `st.stop`) when testing data_loader
- Add new fixtures to `conftest.py` for reusable test data
