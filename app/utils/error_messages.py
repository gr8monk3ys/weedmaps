"""
Enhanced error messaging utilities with recovery instructions.

This module provides user-friendly error messages with actionable recovery steps.
"""
import streamlit as st
from typing import Optional, List


def show_no_data_error(
    filter_info: Optional[str] = None,
    page_name: Optional[str] = None
) -> None:
    """
    Display a user-friendly error message when filtered data is empty.

    Args:
        filter_info: Description of active filters
        page_name: Name of the current page
    """
    page_text = f" for {page_name}" if page_name else ""

    st.error(f"### ⚠️ No Data Available{page_text}")

    with st.expander("📋 **Why did this happen?**", expanded=True):
        st.markdown(
            """
            Your current filter combination has excluded all data. This typically happens when:
            - The selected time period has no recorded data
            - The chosen counties don't have data for this analysis
            - The license type filter is too restrictive
            """
        )

    with st.expander("🔧 **How to fix this**", expanded=True):
        st.markdown(
            """
            **Try these steps:**

            1. **Expand Time Range** (Sidebar → Time Period)
               - Use the time slider to include more years
               - Try selecting "All Years" to see the full dataset

            2. **Broaden County Selection** (Sidebar → Counties)
               - Select "All Counties" to see statewide data
               - Add more counties to your selection

            3. **Adjust License Types** (Sidebar → License Types)
               - Include all license types to see more results
               - Some license types may have limited data

            4. **Check Active Filters**
               - Review the filter summary at the top of the page
               - Remove restrictive filters one at a time
            """
        )

    if filter_info:
        st.info(f"**Current Filters:** {filter_info}")


def show_file_missing_error(filename: str, expected_path: str) -> None:
    """
    Display error when a required data file is missing.

    Args:
        filename: Name of the missing file
        expected_path: Expected file location
    """
    st.error(f"### ❌ Required Data File Missing: {filename}")

    with st.expander("📋 **What this means**", expanded=True):
        st.markdown(
            f"""
            The application cannot find the required data file `{filename}`.

            **Expected location:**
            ```
            {expected_path}
            ```
            """
        )

    with st.expander("🔧 **How to fix this**", expanded=True):
        st.markdown(
            f"""
            **Step-by-step recovery:**

            1. **Verify File Location**
               - Check if `{filename}` exists at the expected path
               - Ensure the file hasn't been renamed or moved

            2. **Check File Permissions**
               - Ensure the application has read access to the file
               - On Windows: Right-click → Properties → Security tab
               - On Unix/Mac: Check with `ls -la` command

            3. **Download Missing Data**
               - If the file is missing, download it from the data source
               - Place it in the correct directory: `data/`

            4. **Restart Application**
               - After placing the file, restart the Streamlit application
               - Use Ctrl+C to stop, then run `streamlit run app.py`

            **Need help?** Contact your data administrator or check the project README.
            """
        )


def show_column_missing_error(
    filename: str,
    missing_columns: List[str],
    required_columns: List[str]
) -> None:
    """
    Display error when required columns are missing from a dataset.

    Args:
        filename: Name of the file with missing columns
        missing_columns: List of columns that are missing
        required_columns: List of all required columns
    """
    st.error(f"### ❌ Missing Required Columns in {filename}")

    with st.expander("📋 **What's wrong**", expanded=True):
        st.markdown(
            f"""
            The file `{filename}` is missing {len(missing_columns)} required column(s):

            **Missing:**
            ```
            {', '.join(missing_columns)}
            ```

            **All required columns:**
            ```
            {', '.join(required_columns)}
            ```
            """
        )

    with st.expander("🔧 **How to fix this**", expanded=True):
        st.markdown(
            """
            **Step-by-step recovery:**

            1. **Verify Data Source**
               - Check if you're using the correct version of the file
               - Older data files may be missing newer columns

            2. **Update Data File**
               - Download the latest version of the data file
               - Ensure column names match exactly (case-sensitive)

            3. **Check for Typos**
               - CSV column headers must match exactly
               - Look for extra spaces or different capitalization

            4. **Manual Column Addition** (Advanced)
               - If you have the raw data, add missing columns
               - Use Excel/Python/R to add required columns
               - Ensure proper formatting and data types

            **Example CSV structure:**
            ```
            County,Year,License Number,Dispensary Name
            Los Angeles,2023,L12345,ABC Dispensary
            ```
            """
        )


def show_insufficient_data_warning(
    message: str,
    min_required: int,
    current_count: int,
    data_type: str = "data points"
) -> None:
    """
    Display warning when there's insufficient data for analysis.

    Args:
        message: Brief description of the issue
        min_required: Minimum number of data points needed
        current_count: Current number of data points
        data_type: Type of data (e.g., "counties", "months", "records")
    """
    st.warning(f"### ⚠️ {message}")

    with st.expander("📊 **Data Requirements**", expanded=False):
        st.markdown(
            f"""
            **Current situation:**
            - You have: **{current_count}** {data_type}
            - Need at least: **{min_required}** {data_type}
            - Missing: **{min_required - current_count}** {data_type}
            """
        )

    with st.expander("💡 **Suggestions**", expanded=False):
        st.markdown(
            f"""
            To get meaningful {data_type.split()[0]} analysis:

            1. **Adjust Filters**
               - Expand time range to include more {data_type}
               - Add more counties/regions to your selection

            2. **Check Data Availability**
               - Some analyses require historical data
               - Newer counties may have limited data

            3. **Alternative Views**
               - Try other dashboard pages for different insights
               - Check the Data Quality page for dataset coverage
            """
        )


def show_correlation_warning(county_count: int) -> None:
    """
    Display specific warning for correlation analysis issues.

    Args:
        county_count: Number of counties with matching data
    """
    if county_count == 0:
        st.warning("### ⚠️ Cannot Perform Correlation Analysis")
        with st.expander("🔧 **How to enable correlation analysis**", expanded=True):
            st.markdown(
                """
                **Why this happened:**
                No counties have both sentiment and density data for the selected filters.

                **How to fix:**
                1. **Expand Filters**
                   - Select "All Counties" in the sidebar
                   - Widen the time range to include more data

                2. **Check Data Availability**
                   - Not all counties have sentiment data
                   - Correlation requires both datasets to overlap

                3. **Try Different Pages**
                   - Visit "Social Insights" for sentiment-only analysis
                   - Visit "Market Overview" for density-only analysis
                """
            )
    elif county_count == 1:
        st.warning("### ⚠️ Insufficient Data for Correlation")
        with st.expander("📊 **Requirements**", expanded=False):
            st.markdown(
                """
                **Current situation:**
                Only 1 county has matching data. Correlation requires at least 2 counties.

                **How to fix:**
                - Add more counties to your filter selection
                - Expand the time range to include more data points
                - Try selecting "All Counties" for complete analysis
                """
            )


def show_loading_error(filename: str, error_message: str) -> None:
    """
    Display error when a file fails to load.

    Args:
        filename: Name of the file that failed to load
        error_message: Technical error message
    """
    st.error(f"### ❌ Error Loading {filename}")

    with st.expander("🐛 **Technical Details**", expanded=False):
        st.code(error_message)

    with st.expander("🔧 **Troubleshooting Steps**", expanded=True):
        st.markdown(
            f"""
            **Common causes and solutions:**

            1. **File Format Issues**
               - Ensure `{filename}` is properly formatted
               - Check for corrupted data or encoding issues
               - Try opening the file in Excel to verify structure

            2. **Permission Problems**
               - Verify you have read access to the file
               - Close the file if it's open in another program

            3. **Data Corruption**
               - Re-download the file from the source
               - Check file size matches expected size
               - Verify file isn't empty or truncated

            4. **Character Encoding**
               - CSV files should be UTF-8 encoded
               - Special characters may cause parsing errors
               - Try re-saving the file with UTF-8 encoding

            **Still having issues?**
            - Check the console/terminal for detailed error messages
            - Contact your system administrator
            - Refer to the project documentation
            """
        )


def show_temporal_analysis_error(error: Exception) -> None:
    """
    Display error for temporal analysis failures with recovery steps.

    Args:
        error: The exception that occurred
    """
    st.error("### ❌ Unable to Generate Temporal Analysis")

    with st.expander("📋 **What went wrong**", expanded=True):
        st.markdown(
            """
            The temporal (time-based) analysis couldn't be completed. This usually happens when:
            - Date information is missing or incorrectly formatted
            - There aren't enough data points across time
            - Date values are inconsistent or invalid
            """
        )

    with st.expander("🔧 **How to fix this**", expanded=True):
        st.markdown(
            """
            **Try these solutions:**

            1. **Check Date Columns**
               - Verify that Year/Month/Date columns exist
               - Ensure dates are in valid format (YYYY-MM-DD)
               - Remove rows with invalid or missing dates

            2. **Increase Time Range**
               - Expand the time period filter in the sidebar
               - Temporal analysis needs multiple time points

            3. **Data Quality Check**
               - Visit the "Data Quality" page
               - Check for missing or invalid date values
               - Verify temporal data coverage

            4. **Alternative Analysis**
               - Try other dashboard pages for non-temporal insights
               - Check "Market Overview" for current statistics
            """
        )

    with st.expander("🐛 **Technical Error**", expanded=False):
        st.code(str(error))
