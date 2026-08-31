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
    # Extract lab number prefix (e.g. "34" from "34-gsheet-playground-script.py")
    lab_num = filename.split('-')[0].strip() if '-' in filename else ""
    
    # Possible filenames to try
    possible_names = [filename]
    if lab_num == "34":
        possible_names.extend(["34-gsheet-playground.py", "34-gsheet-playground-script.py", "gsheet-playground.py"])
    elif lab_num == "35":
        possible_names.extend(["35-copy-lab-tracker-automation.py", "lab-checker.py"])

    # Possible subfolders to try
    folders = [
        "",
        "python-automation/",
        "python-automation/gsheets-automation/",
        "gsheets-automation/"
    ]

    for fname in possible_names:
        for folder in folders:
            url = f"https://raw.githubusercontent.com/{username}/{repo}/main/{folder}{fname}"
            try:
                response = requests.get(url, timeout=3)
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
color_updates = []

green_format = {
    "backgroundColor": {"red": 0.85, "green": 0.93, "blue": 0.82},
    "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.5, "blue": 0.0}}
}
red_format = {
    "backgroundColor": {"red": 0.96, "green": 0.8, "blue": 0.8},
    "textFormat": {"foregroundColor": {"red": 0.7, "green": 0.0, "blue": 0.0}}
}

for idx, (filename, repo) in enumerate(zip(filenames, repos), start=6):
    if not filename or not filename.strip():
        continue

    # Use 'python-AM' if repo is python-automation or match repo
    repo_name = "python-AM" if repo == "python-automation" else repo

    # Check GitHub
    is_uploaded = check_github_file(github_username, repo_name, filename.strip())
    status = "Yes" if is_uploaded else "No"
    cell_format = green_format if is_uploaded else red_format

    # Read current cell value so we only update if changed
    current_value = sheet.cell(idx, danish_col).value
    
    if current_value != status:
        sheet.update_cell(idx, danish_col, status)
        print(f"Row {idx:<2} | {filename:<40} -> [UPDATED: {status}]")
    else:
        print(f"Row {idx:<2} | {filename:<40} -> [{status}]")

    # Add color formatting for this cell (e.g. "G35")
    color_updates.append({
        "range": f"G{idx}",
        "format": cell_format
    })

# Apply all background colors in a single batch request
if color_updates:
    print("\nApplying Green and Red colors to Google Sheet...")
    sheet.batch_format(color_updates)

print("\n" + "=" * 60)
print("[DONE] Dynamic Lab Checking & Google Sheet Update Complete!")
print("=" * 60 + "\n")