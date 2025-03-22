import time
import pandas as pd
from typing import Dict, List


def get_date_info() -> Dict[str, str]:
    """Return current date info.

    Returns:
        Dict with today's date and current month
    """
    return {"today": time.strftime("%Y-%m-%d"), "month": time.strftime("%Y-%m")}


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


def filter_vital_parts(df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
    """Filter vital and urgent parts based on status.

    Args:
        df: Source dataframe
        status_filter: Status to filter by

    Returns:
        Filtered dataframe
    """
    if df.empty:
        return df

    # Filter based on "Vital" category and "Segera" status
    vital_df = df[
        (df["Category"].str.contains("Vital", case=False, na=False))
        & (df["STATUS"].str.contains("Segera", na=False))
    ]

    # Additional filter based on selected status
    if status_filter != "Semua":
        vital_df = vital_df[vital_df["STATUS"].str.contains(status_filter, na=False)]

    return vital_df
