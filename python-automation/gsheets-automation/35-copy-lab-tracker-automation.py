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
# 2. GITHUB CHECKER FUNCTION
# ==========================================
def check_github(github_url, repo_name, lab_number):
    """Takes a student's URL, finds their username, and checks their GitHub repo."""
    
    # Safety Check: If the spreadsheet has a blank cell or "NaN" for the URL, skip it.
    if not github_url or github_url.lower() == "nan":
        return False
        
    # Extract username from URL (e.g. https://github.com/Danish20699 -> Danish20699)
    username = github_url.rstrip('/').split('/')[-1]
    
    # Prepare to show GitHub token if available
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
    # Try both original repo name and repo variants (like python-AM)
    possible_repos = [repo_name]
    if "python" in repo_name.lower():
        possible_repos.extend(["python-AM", "python-automation"])

    # Try both root directory and subfolders
    subpaths = ["", "python-automation/", "gsheets-automation/"]

    for repo in set(possible_repos):
        for sub in subpaths:
            api_link = f"https://api.github.com/repos/{username}/{repo}/contents/{sub}"
            try:
                response = requests.get(api_link, headers=headers, timeout=5)
                if response.status_code == 200:
                    for file in response.json():
                        if isinstance(file, dict) and 'name' in file:
                            # Matches lab number at start (e.g. "30-ping-check.py" matches "30")
                            if file['name'].startswith(str(lab_number)):
                                return True
            except Exception:
                pass
            
    return False

# ==========================================
# 3. READ DATA & PREPARE BULK UPDATES
# ==========================================
print("\nDownloading sheet data... (Counts as 1 API Request to Google)")
all_data = sheet.get_all_values()

# Grab the list of student GitHub URLs from Row 1, Column D onwards
student_urls = all_data[0][3:]

text_updates = []
color_updates = []

print(f"Checking GitHub for all students and labs across {len(all_data) - 5} rows...")

# Loop through the rows starting at Row 6 in the spreadsheet
for row_index in range(5, len(all_data)):
    row = all_data[row_index]
    
    lab_number = row[0].strip()  # Column A
    repo_name = row[2].strip()   # Column C
    
    if not lab_number or not repo_name:
        continue
    
    print(f"Checking Lab {lab_number:<2} ({repo_name})...")
        
    # Loop through every student column
    for col_offset in range(len(student_urls)):
        url = student_urls[col_offset]
        
        excel_row = row_index + 1      # Spreadsheets start at row 1
        excel_col = col_offset + 4     # Students start at Column D (Col 4)
        
        did_homework = check_github(url, repo_name, lab_number)
        
        if did_homework:
            cell_text = "Yes"
            cell_color = green_format
        else:
            cell_text = "No"
            cell_color = red_format
            
        # 1. Add Text Update to cart
        text_updates.append(gspread.Cell(excel_row, excel_col, cell_text))
        
        # 2. Add Color Update to cart
        cell_name = rowcol_to_a1(excel_row, excel_col)
        color_updates.append({
            "range": cell_name,
            "format": cell_color
        })

# ==========================================
# 4. PUSH ALL UPDATES AT ONCE (BULK BATCH)
# ==========================================
print("\nPushing all updates to Google Sheets in bulk...")

if text_updates:
    sheet.update_cells(text_updates)

if color_updates:
    sheet.batch_format(color_updates)

print("[SUCCESS] Bulk update and coloring complete! 🎉")