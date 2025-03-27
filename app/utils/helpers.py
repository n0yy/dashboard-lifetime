import time
import pandas as pd
from typing import Dict, List


def get_date_info() -> Dict[str, str]:
    """Return current date info.

    Returns:
        Dict with today's date and current month
    """
    return {"today": time.strftime("%d-%m-%Y"), "month": time.strftime("%Y-%m")}


def prepare_dataframe(df: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
    """Prepare dataframe for analysis by converting types.

    Args:
        df: Source dataframe
        required_columns: List of required columns

    Returns:
        Prepared dataframe with correct types
    """
    if df.empty:
        return df

    df_copy = df.copy()

    # Ensure all required columns exist
    for col in required_columns:
        if col not in df_copy.columns:
            df_copy[col] = ""

    # Convert data types
    try:
        df_copy["Leadtime (Hari)"] = pd.to_numeric(
            df_copy["Leadtime (Hari)"], errors="coerce"
        )
        df_copy["STATUS"] = df_copy["STATUS"].fillna("")
        df_copy["Penggantian Selanjutnya"] = df_copy["Penggantian Selanjutnya"].fillna(
            ""
        )
    except Exception as e:
        print(f"Error preparing dataframe: {str(e)}")

    return df_copy


def filter_vital_parts(
    df: pd.DataFrame, status_filter: str, category_filter: str
) -> pd.DataFrame:
    """Filter vital and urgent parts based on status.

    Args:
        df: Source dataframe
        status_filter: Status to filter by

    Returns:
        Filtered dataframe
    """
    if df.empty:
        return df

    vital_df = df.copy()

    # Additional filter based on selected status
    if status_filter != "Semua":
        vital_df = vital_df[vital_df["STATUS"].str.contains(status_filter, na=False)]

    if category_filter != "Semua":
        vital_df = vital_df[
            vital_df["Category"].str.contains(category_filter, na=False)
        ]

    return vital_df


def convert_days_to_readable(days):
    """
    Convert total days into a readable format of years, months, and days.

    Args:
    days (int): Total number of days

    Returns:
    str: Formatted string with years, months, and days
    """
    # Calculate years
    years = days // 365
    remaining_days = days % 365

    # Calculate months
    months = remaining_days // 30
    days_left = remaining_days % 30

    # Create the formatted string
    parts = []
    if years > 0:
        parts.append(f"{years} tahun" if years == 1 else f"{years} tahun")
    if months > 0:
        parts.append(f"{months} bulan" if months == 1 else f"{months} bulan")
    if days_left > 0:
        parts.append(f"{days_left} hari" if days_left == 1 else f"{days_left} hari")

    parts.append("lagi")
    # Join the parts or return 0 hari if no time has passed
    return " ".join(parts) if parts else "0 hari"
