import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from typing import Dict, List


class DataLoader:
    """Handles loading data from Google Sheets with caching."""

    def __init__(self, sheet_id: str, machine_options: List[str]):
        """Initialize the data loader.

        Args:
            sheet_id: Google Sheet ID
            machine_options: List of machine types
        """
        self.sheet_id = sheet_id
        self.machine_options = machine_options

    @st.cache_resource
    def get_sheet_client(_self):
        """Create and cache the Google Sheets client.

        Returns:
            Authorized Google Sheets client
        """
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials_dict = st.secrets["spreadsheet"]
        credential = Credentials.from_service_account_info(
            credentials_dict, scopes=scopes
        )
        client = gspread.authorize(credential)
        return client

    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def load_worksheet_data(_self, worksheet_name: str) -> pd.DataFrame:
        """Load data from a specific worksheet with caching.

        Args:
            worksheet_name: Name of the worksheet

        Returns:
            DataFrame containing worksheet data
        """
        try:
            client = _self.get_sheet_client()
            sheet = client.open_by_key(_self.sheet_id)
            worksheet = sheet.worksheet(worksheet_name)
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
        data_frames = {}
        available_worksheets = (
            self.get_sheet_client().open_by_key(self.sheet_id).worksheets()
        )
        worksheet_titles = [ws.title for ws in available_worksheets]

        for machine in self.machine_options:
            if machine in worksheet_titles:
                data_frames[machine] = self.load_worksheet_data(machine)
            else:
                data_frames[machine] = pd.DataFrame()
                st.warning(f"Worksheet for {machine} not found.")

        return data_frames
