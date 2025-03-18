import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'access.json'
SPREADSHEET_KEY = '1XEt1-TN_0_-_qZZT5_0vG4MBbOUC57YqPGR1HuhLbvY'
SHEET_NAME = 'Sheet1'  # Change if necessary

def test_google_sheet_access():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(SPREADSHEET_KEY)
    
    # Print available worksheets
    worksheets = sh.worksheets()
    print("Worksheets found:", [ws.title for ws in worksheets])
    
    worksheet = sh.worksheet(SHEET_NAME)
    texts = worksheet.col_values(1)
    print("Texts from the sheet:", texts)

if __name__ == '__main__':
    test_google_sheet_access()
