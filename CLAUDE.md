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
- **Plots**: `app/plots/` - Reusable Plotly visualization functions
- **Utils**: `app/utils/` - Shared utilities and data loading
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

#### Visualization Functions (Modular)
Plot functions in `app/plots/` are self-contained and reusable:
- Accept data and configuration parameters
- Return Plotly figure objects
- Handle their own GeoJSON loading when needed
- Example: `create_choropleth(data, value_column, location_column)`

#### Data Processing
- **Sentiment Conversion**: The `data_loader.py` contains `convert_sentiment_score()` that normalizes various sentiment formats to a consistent -1 to 1 scale
- **Data Caching**: `load_data()` uses `@st.cache_data` decorator for performance - data loads once per session
- **Data Validation**: Comprehensive validation checks for file existence, required columns, and data integrity
- **County Name Cleaning**: Many pages clean county names to match GeoJSON using `.replace(" County", "").strip()`
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

## Configuration

- **Poetry**: `pyproject.toml` - Dependency management, Black/isort settings
- **Streamlit**: `config/.streamlit/config.toml` - App theming (green color scheme)
- **Environment**: `.env` - Environment variables (OPENAI_API_KEY defined but LLM features not yet implemented)
- **App Config**: `app/config/` - Centralized application configuration
  - `regions.py`: California county-to-region mappings
  - `theme.py`: Plotly visualization theme and color palette

## Testing Strategy

Basic test structure is in place in `tests/` directory:
- Run tests with `poetry run pytest`
- Fixtures available in `tests/conftest.py` for sample data
- Current tests cover:
  - `test_data_loader.py`: Sentiment score conversion and data directory functions
  - `test_config.py`: Region and theme configuration validation

When adding new tests:
- Follow the established code formatting (Black, isort)
- Use the fixtures from `conftest.py` for sample data
- Test data transformations, not Streamlit UI components
- Mock Streamlit functions (`st.error`, `st.stop`) when testing data_loader
