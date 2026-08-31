import os
import requests
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup Google Sheets Authentication
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file(
    'python-automation/gsheets-automation/credentials.json',
    scopes=scope
)
client = gspread.authorize(creds)

# 2. Open LabTracker Spreadsheet
print("Connecting to LabTracker...")
sheet = client.open('LabTracker').sheet1
print("Successfully connected to LabTracker!\n")



# 3. Helper Function: Check if a file exists on GitHub
def check_github_file(username, repo, filename):
    possible_urls = [
        f"https://raw.githubusercontent.com/{username}/{repo}/main/{filename}",
        f"https://raw.githubusercontent.com/{username}/{repo}/main/python-automation/{filename}"
    ]
    
    for url in possible_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except Exception:
            pass
    return False

# 4. Find Danish's Column Dynamically
student_name = "Danish"
row_4_students = sheet.row_values(4)
if student_name in row_4_students:
    danish_col = row_4_students.index(student_name) + 1  # Column G = 7
    print(f"Found '{student_name}' at Column index: {danish_col} (Column G)")
else:
    danish_col = 7  # Fallback to Column G

# Get Danish's GitHub Username from Row 1
github_url = sheet.cell(1, danish_col).value
github_username = github_url.split('/')[-1] if github_url else "Danish20699"
print(f"Target GitHub User: {github_username}\n")

# 5. Fetch all Lab Filenames (Column B) and Repo Names (Column C)
print("Scanning lab files from spreadsheet...")
filenames = sheet.col_values(2)[5:]  # Column B starting from row 6
repos = sheet.col_values(3)[5:]      # Column C starting from row 6

print(f"Total labs to check: {len(filenames)}\n")
print("=" * 60)
print(f"  [CHECKING] Starting Dynamic GitHub Lab Checker for {student_name}")
print("=" * 60 + "\n")

# 6. Dynamic Loop: Check GitHub & Update Google Sheet
for idx, (filename, repo) in enumerate(zip(filenames, repos), start=6):
    if not filename or not filename.strip():
        continue

    # Use 'python-AM' if repo is python-automation or match repo
    repo_name = "python-AM" if repo == "python-automation" else repo

    # Check GitHub
    is_uploaded = check_github_file(github_username, repo_name, filename.strip())
    status = "Yes" if is_uploaded else "No"

    # Read current cell value so we only update if changed
    current_value = sheet.cell(idx, danish_col).value
    
    if current_value != status:
        sheet.update_cell(idx, danish_col, status)
        print(f"Row {idx:<2} | {filename:<40} -> [UPDATED: {status}]")
    else:
        print(f"Row {idx:<2} | {filename:<40} -> [{status}]")

print("\n" + "=" * 60)
print("[DONE] Dynamic Lab Checking & Google Sheet Update Complete!")
print("=" * 60 + "\n")
# Format background to Green for "Yes"
if status == "Yes":
    sheet.format(f"G{idx}", {
        "backgroundColor": {
            "red": 0.85,
            "green": 0.93,
            "blue": 0.83
        }
    })