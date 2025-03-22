import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from typing import Dict, List


class DataLoader:
    """Handles loading data from Google Sheets."""

    def __init__(self, sheet_id: str, machine_options: List[str]):
        """Initialize the data loader.

        Args:
            sheet_id: Google Sheet ID
            machine_options: List of machine types
        """
        self.sheet_id = sheet_id
        self.machine_options = machine_options
        self.sheet = self._setup_google_sheets()

    def _setup_google_sheets(self):
        """Set up and return Google Sheets client.

        Returns:
            Google Sheet instance
        """
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials_dict = st.secrets["spreadsheet"]
        credential = Credentials.from_service_account_info(
            credentials_dict, scopes=scopes
        )
        client = gspread.authorize(credential)
        return client.open_by_key(self.sheet_id)

    def _load_worksheet_data(self, worksheet_name: str) -> pd.DataFrame:
        """Load data from a specific worksheet.

        Args:
            worksheet_name: Name of the worksheet

        Returns:
            DataFrame containing worksheet data
        """
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            data = worksheet.get_all_values()
            if len(data) < 2:
                return pd.DataFrame()
            headers = data[1]
            rows = data[2:]
            return pd.DataFrame(rows, columns=headers)
        except Exception as e:
            st.error(f"Error loading worksheet {worksheet_name}: {str(e)}")
            return pd.DataFrame()

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load data for all machine types.

        Returns:
            Dictionary mapping machine types to DataFrames
        """
        data_frames = {}
        available_worksheets = [ws.title for ws in self.sheet.worksheets()]

        for machine in self.machine_options:
            if machine in available_worksheets:
                data_frames[machine] = self._load_worksheet_data(machine)
            else:
                # Create empty DataFrame if worksheet not found
                data_frames[machine] = pd.DataFrame()
                st.warning(f"Worksheet for {machine} not found.")

        return data_frames
