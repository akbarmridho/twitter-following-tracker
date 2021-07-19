from typing import List
import gspread
from gspread import Client, Spreadsheet
from gspread.models import Worksheet
from src import Config


class Sheets:
    client: Client
    sheet: Spreadsheet
    worksheet: Worksheet
    next_row: int = 1

    def __init__(self, config: Config):
        self.client = gspread.service_account(
            config.GOOGLE_APPLICATION_CREDENTIALS)
        self.sheet = self.client.open_by_url(config.SPREADSHEET_URL)
        self.worksheet = self.sheet.sheet1

        row_count = len(self.worksheet.col_values(1))

        if row_count == 0:
            self.worksheet.insert_row(
                ["user_watched", "following", "date", "followers_count", "description"])
            self.next_row = 2
        else:
            self.next_row = row_count + 1

    def append(self, values: List[List[str]]):
        """Append worksheet row

        Args:
            values (List[str]): ['user_watched', 'following', 'date'],
        """
        self.worksheet.insert_rows(values, row=self.next_row)
        self.next_row += len(values)
