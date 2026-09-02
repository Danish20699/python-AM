import os
import gspread
import requests
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1  # Helper to convert coordinates like (6, 4) into "D6"

# ==========================================
# 1. SETUP SECRETS, COLORS & CONNECTION
# ==========================================

# Optional GitHub Personal Access Token (PAT)
GITHUB_TOKEN = os.getenv("LAB_TRK_PAT")

# Define our colors using Google's RGB format (0.0 is zero color, 1.0 is max color)
green_format = {
    "backgroundColor": {"red": 0.85, "green": 0.93, "blue": 0.82},  # Light green background
    "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.5, "blue": 0.0}}  # Dark green text
}
red_format = {
    "backgroundColor": {"red": 0.96, "green": 0.8, "blue": 0.8},  # Light red background
    "textFormat": {"foregroundColor": {"red": 0.7, "green": 0.0, "blue": 0.0}}  # Dark red text
}

print("Connecting to Google Sheets...")
# Tell Google what we want permission to do (read/edit spreadsheets)
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Path to your credentials.json file
creds_path = 'python-automation/gsheets-automation/credentials.json' if os.path.exists('python-automation/gsheets-automation/credentials.json') else 'credentials.json'
creds = Credentials.from_service_account_file(creds_path, scopes=scopes)

# Log in!
client = gspread.authorize(creds)
# Open the specific file and tab
sheet = client.open('LabTracker').sheet1
print("Connected successfully to LabTracker!")

# ==========================================
# 2. GITHUB CHECKER FUNCTION (FAST & RELIABLE)
# ==========================================
def check_github(github_url, repo_name, filename, lab_number=""):
    """Checks if a student uploaded a specific lab file on GitHub."""
    if not github_url or github_url.lower() == "nan":
        return False
        
    username = github_url.rstrip('/').split('/')[-1]
    clean_num = str(lab_number).strip().lstrip('0')
    suffix = filename.split('-', 1)[-1] if '-' in filename else filename

    urls_to_try = []

    # 1. Python Basics Repo (Tasks 26-29, 36-40)
    if "basics" in repo_name.lower():
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-basics/main/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-basics/main/{clean_num}-{suffix}")

    # 2. Python Automation Repo (Tasks 30-35)
    elif "automation" in repo_name.lower() or repo_name in ["python-AM", "python-automation"]:
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/{filename}")
        if clean_num == "34":
            urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/34-gsheet-playground.py")
        elif clean_num == "35":
            urls_to_try.append(f"https://raw.githubusercontent.com/{username}/python-AM/main/python-automation/gsheets-automation/35-copy-lab-tracker-automation.py")

    # 3. Linux Repo
    elif "linux" in repo_name.lower():
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/labs/linux-fundamentals/lab-{clean_num.zfill(2)}-{suffix}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/labs/linux-fundamentals/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/linux/main/{filename}")

    # 4. PostgreSQL Repo
    elif "psql" in repo_name.lower():
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/postgresql-labs/main/{filename}")
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/postgresql-labs/main/{clean_num.zfill(2)}-{suffix}/README.md")

    # 5. PHP Repo
    elif "php" in repo_name.lower():
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/php-labs/main/{filename}")

    # 6. Fallback
    else:
        urls_to_try.append(f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{filename}")

    # Check direct URLs
    for url in urls_to_try:
        try:
            res = requests.get(url, timeout=3.0)
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
github_username = github_url.rstrip('/').split('/')[-1] if github_url else "Danish20699"
print(f"Target GitHub User: {github_username}\n")

# 5. Fetch all Lab Data
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

for idx, (lab_num, filename, repo) in enumerate(zip(lab_numbers, filenames, repos), start=6):
    if not filename or not filename.strip() or not lab_num.strip():
        continue

    is_uploaded = check_github(github_url, repo, filename.strip(), lab_number=lab_num)
    status = "Yes" if is_uploaded else "No"
    cell_format = green_format if is_uploaded else red_format

    print(f"Row {idx:<2} | Lab {lab_num:<2} | {filename:<45} -> [{status}]")

    # 1. Add Text Update to bulk list
    text_updates.append(gspread.Cell(idx, danish_col, status))

    # 2. Add Color Update to bulk list
    cell_name = rowcol_to_a1(idx, danish_col)
    color_updates.append({
        "range": cell_name,
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