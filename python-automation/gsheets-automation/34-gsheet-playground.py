# =======================================================
# METHOD 1: SHORT VERSION (1-liner shortcut)
# =======================================================
#import gspread

#client = gspread.service_account(filename='python-automation/gsheets-automation/credentials.json')


# =======================================================
# METHOD 2: LONG VERSION (Explicit with OAuth2 Scopes)
# =======================================================
from google.oauth2.service_account import Credentials
import gspread

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = Credentials.from_service_account_file(
   'python-automation/gsheets-automation/credentials.json',     scopes=scope
)
client = gspread.authorize(creds)
# Open the sheet and read values
print("Connecting to LabTracker...")
sheet = client.open('LabTracker').sheet1
print("✅ Successfully opened LabTracker!\n")

# 1. Read Danish's GitHub URL from Cell G1
d_url = sheet.acell('G1').value
print(f"Danish's GitHub URL (G1): {d_url}")

# 2. Extract Username from URL
d_username = d_url.split('/')[-1]
print(f"Danish's Username: {d_username}\n")

# 3. Read Task 30 Name from Cell B35
task_30 = sheet.acell('B35').value
print(f"Task 30 (B35): {task_30}")

# 4. Read Danish's Status for Task 30 from Cell G35
task_30_status = sheet.acell('G35').value
print(f"Danish's Status (G35): {task_30_status}")
# 5. Update Task 30 status in Column G to 'Yes'
print("\nUpdating Task 30 status to 'Yes'...")
sheet.update_acell('A1', 'Sheets')
print("[SUCCESS] Updated Cell G35 in Google Sheets!")




