# California Cannabis Market Analytics Dashboard

![Dashboard Preview](public/images/dashboard.png)

## Overview

This Streamlit-based dashboard provides comprehensive analytics and insights into California's cannabis retail market. The application combines dispensary data with social media sentiment analysis to offer a multi-faceted view of the market landscape.

## Features

### 🏠 Home Dashboard
- Key market metrics and trends
- Overall market health indicators
- Quick navigation to detailed analysis sections

### 📊 Market Overview
- Year-over-year market growth analysis
- Regional distribution of dispensaries
- License type breakdown by county
- Interactive filters for custom analysis

### 🗺️ Geographic Analysis
- Interactive choropleth map of California counties
- Population-adjusted retailer density metrics
- Regional market concentration analysis
- County-level license distribution

### 💭 Social Insights
- Social media sentiment analysis by region
- Temporal sentiment trends
- Correlation between market density and public sentiment
- County-level sentiment distribution

## Data Sources

The dashboard utilizes four main data sources in the `data/` directory:
- **`Dispensaries.csv`**: Detailed cannabis retailer license information
- **`Dispensary_Density.csv`**: Population-adjusted retailer density metrics
- **`Tweet_Sentiment.csv`**: Social media sentiment data with BERT scores
- **`California_County_Boundaries.geojson`**: County geographic boundaries

See [DATA_SCHEMA.md](DATA_SCHEMA.md) for complete data file specifications.

## Technology Stack

- **Python**: >= 3.10
- **Key Dependencies**:
  - Streamlit: Web application framework
  - Pandas: Data manipulation and analysis
  - Plotly: Interactive visualizations
  - Transformers: Sentiment analysis models

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/california-cannabis-analytics.git
cd california-cannabis-analytics
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
streamlit run app/Home.py
```

## Project Structure

```
├── app/
│   ├── Home.py                    # Main dashboard entry point
│   ├── pages/                     # Multi-page dashboard pages
│   │   ├── 01-Market Overview.py
│   │   ├── 02-Geographic Analysis.py
│   │   └── 03-Social Insights.py
│   ├── plots/                     # Reusable visualization functions
│   │   ├── choropleth.py
│   │   └── sentiment_distribution.py
│   ├── utils/                     # Utility functions
│   │   ├── data_loader.py        # Centralized data loading with validation
│   │   ├── data_utils.py         # Data transformation utilities
│   │   ├── filters.py            # Filter application functions
│   │   ├── generate_sidebar.py   # Sidebar generation
│   │   └── load_geojson.py       # GeoJSON loading
│   ├── config/                    # Application configuration
│   │   ├── env.py                # Environment variables
│   │   ├── regions.py            # California region definitions
│   │   └── theme.py              # Plotly theme configuration
│   └── style.css                  # Custom CSS styling
├── config/
│   └── .streamlit/                # Streamlit configuration
│       └── config.toml
├── data/                          # Data files (required)
│   ├── Dispensaries.csv
│   ├── Dispensary_Density.csv
│   ├── Tweet_Sentiment.csv
│   └── California_County_Boundaries.geojson
├── tests/                         # Test suite
│   ├── conftest.py               # Pytest fixtures
│   ├── test_data_loader.py       # Data loading tests
│   └── test_config.py            # Configuration tests
├── public/                        # Static assets
├── CLAUDE.md                      # Development guide for AI assistants
├── TODO.md                        # Task tracking
├── DATA_SCHEMA.md                 # Data file specifications
├── SECURITY.md                    # Security policies
└── README.md                      # This file
```

## Development

### Testing

The project includes a comprehensive test suite with 20 passing tests:

```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_data_loader.py
```

### Code Quality

The project uses Poetry for dependency management and includes development tools:

```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .

# Lint code with flake8
poetry run flake8

# Lint with pylint
poetry run pylint app/
```

### Development Tools
- **Black**: Code formatting (line length: 88)
- **isort**: Import sorting (Black-compatible profile)
- **flake8**: Code linting
- **pylint**: Advanced linting
- **pytest**: Testing framework (20 tests, 100% passing)

### Architecture Documentation

- **[CLAUDE.md](CLAUDE.md)**: Comprehensive architectural guide for development
- **[DATA_SCHEMA.md](DATA_SCHEMA.md)**: Complete data file specifications
- **[SECURITY.md](SECURITY.md)**: Security policies and best practices
- **[TODO.md](TODO.md)**: Task tracking and prioritization

### Key Features

- ✅ **Centralized Configuration**: Regions, themes, and settings in `app/config/`
- ✅ **Data Validation**: Comprehensive validation on data load with user-friendly errors
- ✅ **Performance**: Data caching with `@st.cache_data` for fast page loads
- ✅ **Filtering**: Functional sidebar filters for time period, license type, and county
- ✅ **Testing**: Full test suite with fixtures and 100% pass rate
- ✅ **Type Safety**: Clear function signatures and docstrings
- ✅ **Security**: Environment variable management and security guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
