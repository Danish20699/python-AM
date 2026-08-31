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
def check_github_file(username, repo, filename, lab_number=""):
    clean_num = str(lab_number).strip().lstrip('0')
    suffix = filename.split('-', 1)[-1] if '-' in filename else filename
    
    urls_to_try = []

    # 1. Python Basics Repo (Tasks 26-29, 36-40)
    if "python-basics" in repo.lower():
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-basics/main/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-basics/main/{clean_num}-{suffix}")

    # 2. Python Automation Repo (Tasks 30-35)
    elif "automation" in repo.lower() or repo in ["python-automation", "python-AM"]:
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/{filename}")
        if clean_num == "34":
            urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/34-gsheet-playground.py")
        elif clean_num == "35":
            urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/35-copy-lab-tracker-automation.py")

    # 3. Linux Repo (Tasks 8-16)
    elif repo == "linux":
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/labs/linux-fundamentals/lab-{clean_num.zfill(2)}-{suffix}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/labs/linux-fundamentals/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/{filename}")

    # 4. PostgreSQL Repo (Tasks 18-21)
    elif repo == "psql":
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/postgresql-labs/main/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/postgresql-labs/main/{clean_num.zfill(2)}-{suffix}/README.md")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/postgresql-labs/main/{clean_num}-{suffix}/README.md")

    # 5. PHP Repo (Task 22)
    elif repo == "php":
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/php-labs/main/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/php-labs/main/{suffix.replace('.md', '')}/README.md")

    # 6. Any other repo
    else:
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/{repo}/main/{filename}")

    # Test URLs
    for url in urls_to_try:
        try:
            res = requests.get(url, timeout=0.8)
            if res.status_code == 200:
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

# 5. Fetch all Lab Numbers (Column A), Filenames (Column B) and Repo Names (Column C)
print("Scanning lab files from spreadsheet...")
lab_numbers = sheet.col_values(1)[5:]  # Column A starting from row 6
filenames = sheet.col_values(2)[5:]    # Column B starting from row 6
repos = sheet.col_values(3)[5:]        # Column C starting from row 6

print(f"Total labs to check: {len(filenames)}\n")
print("=" * 60)
print(f"  [CHECKING] Starting Dynamic GitHub Lab Checker for {student_name}")
print("=" * 60 + "\n")

# 6. Dynamic Loop: Check GitHub & Prepare Bulk Updates
text_updates = []
color_updates = []

green_format = {
    "backgroundColor": {"red": 0.85, "green": 0.93, "blue": 0.82},
    "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.5, "blue": 0.0}}
}
red_format = {
    "backgroundColor": {"red": 0.96, "green": 0.8, "blue": 0.8},
    "textFormat": {"foregroundColor": {"red": 0.7, "green": 0.0, "blue": 0.0}}
}

for idx, (lab_num, filename, repo) in enumerate(zip(lab_numbers, filenames, repos), start=6):
    if not filename or not filename.strip():
        continue

    # Use 'python-AM' if repo is python-automation or match repo
    repo_name = "python-AM" if repo == "python-automation" else repo

    # Check GitHub
    is_uploaded = check_github_file(github_username, repo_name, filename.strip(), lab_number=lab_num)
    status = "Yes" if is_uploaded else "No"
    cell_format = green_format if is_uploaded else red_format

    print(f"Row {idx:<2} | {filename:<45} -> [{status}]")

    # 1. Add Text Update to bulk list
    text_updates.append(gspread.Cell(idx, danish_col, status))

    # 2. Add Color Update to bulk list
    color_updates.append({
        "range": f"G{idx}",
        "format": cell_format
    })

# Apply all text updates in a single batch request
if text_updates:
    print("\nPushing all Text updates to Google Sheets in bulk...")
    sheet.update_cells(text_updates)

# Apply all background colors in a single batch request
if color_updates:
    print("Applying Green and Red colors to Google Sheets in bulk...")
    sheet.batch_format(color_updates)

print("\n" + "=" * 60)
print("[DONE] Dynamic Lab Checking & Google Sheet Update Complete!")
print("=" * 60 + "\n")