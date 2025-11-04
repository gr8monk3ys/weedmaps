"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
import pandas as pd
import os


@pytest.fixture
def sample_dispensaries_data():
    """Create sample dispensary data for testing."""
    return pd.DataFrame({
        'County': ['Los Angeles County', 'San Francisco County', 'San Diego County',
                   'Los Angeles County', 'Orange County', 'San Diego County'],
        'License_Date': ['2020-01-15', '2020-02-20', '2020-03-10',
                        '2021-05-20', '2021-06-15', '2022-01-10'],
        'Year': [2020, 2020, 2020, 2021, 2021, 2022],
        'License Type': ['Adult-Use Retail', 'Medicinal Retail', 'Adult-Use Retail',
                        'Adult-Use and Medicinal', 'Adult-Use Retail', 'Medicinal Retail'],
        'License Designation': ['Adult-Use', 'Medicinal', 'Adult-Use',
                               'Adult-Use and Medicinal', 'Adult-Use', 'Medicinal'],
        'License Number': ['C10-0000001-LIC', 'C10-0000002-LIC', 'C10-0000003-LIC',
                          'C10-0000004-LIC', 'C10-0000005-LIC', 'C10-0000006-LIC'],
        'Dispensary Name': ['Test Dispensary 1', 'Test Dispensary 2', 'Test Dispensary 3',
                           'Test Dispensary 4', 'Test Dispensary 5', 'Test Dispensary 6']
    })


@pytest.fixture
def sample_density_data():
    """Create sample density data for testing."""
    return pd.DataFrame({
        'County': ['Los Angeles County', 'San Francisco County', 'San Diego County',
                   'Los Angeles County', 'Orange County', 'San Diego County'],
        'Year': [2020, 2020, 2020, 2021, 2021, 2022],
        'Dispensary_PerCapita': [5.2, 8.1, 4.3, 5.5, 3.2, 4.7],
        'Population': [10000000, 875000, 1400000, 10100000, 3200000, 1450000]
    })


@pytest.fixture
def sample_sentiment_data():
    """Create sample sentiment data for testing."""
    return pd.DataFrame({
        'BERT_Sentiment': [0.5, -0.2, 0.8, 0.3, -0.1, 0.6],
        'Tweet_Date': pd.date_range('2020-01-01', periods=6),
        'Year': [2020, 2020, 2020, 2021, 2021, 2022],
        'County': ['Los Angeles County', 'San Francisco County', 'San Diego County',
                   'Los Angeles County', 'Orange County', 'San Diego County']
    })


@pytest.fixture
def sample_geojson():
    """Create sample GeoJSON data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"NAME": "Los Angeles"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-118, 34], [-118, 35], [-117, 35], [-117, 34], [-118, 34]]]
                }
            }
        ]
    }


@pytest.fixture
def mock_data_dir(tmp_path, sample_dispensaries_data, sample_density_data,
                  sample_sentiment_data, sample_geojson):
    """Create a temporary data directory with sample files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Save sample CSV files
    sample_dispensaries_data.to_csv(data_dir / "Dispensaries.csv", index=False)
    sample_density_data.to_csv(data_dir / "Dispensary_Density.csv", index=False)
    sample_sentiment_data.to_csv(data_dir / "Tweet_Sentiment.csv", index=False)

    # Save sample GeoJSON
    import json
    with open(data_dir / "California_County_Boundaries.geojson", 'w') as f:
        json.dump(sample_geojson, f)

    return data_dir
