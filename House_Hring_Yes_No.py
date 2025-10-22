import re
import pandas as pd
import pdfplumber
from openpyxl import load_workbook

def extract_and_append_missing_personnel(pdf_path, personnel_excel):
    try:
        # Load personnel Excel file
        df = pd.read_excel(personnel_excel)

        # Ensure required columns exist
        for column in ['Personnel', 'Name', 'Designation', 'Basic Pay', 'House Rent Allowance', 'Hiring Amount']:
            if column not in df.columns:
                df[column] = None

        # Clean personnel numbers in Excel
        personnel_list = df['Personnel'].dropna().astype(str).tolist()
        personnel_list = [
            str(int(float(num))) for num in personnel_list if num.strip() and num.strip() != "0"
        ]

        # For tracking personnel found with HRA and Hiring Amount
        found_allowance = set()
        hiring_amounts = {}

        missing_data = []

        # Open and read PDF pages
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                # Find all personnel numbers on this page
                personnel_matches = re.findall(r'Personnel Number:\s*(\d+)', text)

                # Check if page contains HRA or Hiring
                has_allowance = "House Rent Allowance 45%" in text

                # Find hiring amount pattern (e.g., "Hiring Amount 25,000.00")
                hiring_match = re.search(r'Hiring Amount\s*([\d,]+\.\d{2})', text)
                hiring_value = hiring_match.group(1) if hiring_match else None

                for personnel in personnel_matches:
                    if has_allowance:
                        found_allowance.add(personnel)
                    if hiring_value:
                        hiring_amounts[personnel] = hiring_value

                    # Add missing personnel if not in Excel
                    if personnel not in personnel_list:
                        print(f"Missing Personnel Found: {personnel}")

                        # Extract Name
                        name_match = re.search(r'Name:\s*([A-Za-z\s]+)', text)
                        name = name_match.group(1).strip() if name_match else "Unknown"

                        # Extract Basic Pay
                        pay_match = re.search(r'Basic Pay\s+([\d,]+\.\d{2})', text)
                        basic_pay = pay_match.group(1) if pay_match else "Not In Pay Roll"

                        # Extract Designation
                        desig_match = re.search(r'Designation\s*:\s*([A-Za-z\s]+)', text)
                        designation = desig_match.group(1).strip() if desig_match else "Unknown"

                        hra_status = "Yes" if has_allowance else "No"
                        hiring_amt = hiring_value if hiring_value else "Not Mentioned"

                        missing_data.append([
                            personnel, name, designation, basic_pay, hra_status, hiring_amt
                        ])

        # Update existing Excel rows
        df['Personnel'] = df['Personnel'].astype(str)

        df['House Rent Allowance'] = df['Personnel'].apply(
            lambda x: "Yes" if x in found_allowance else "No"
        )

        df['Hiring Amount'] = df['Personnel'].apply(
            lambda x: hiring_amounts.get(x, "Not Mentioned")
        )

        # Append missing data (if any)
        if missing_data:
            df_missing = pd.DataFrame(
                missing_data,
                columns=['Personnel', 'Name', 'Designation', 'Basic Pay', 'House Rent Allowance', 'Hiring Amount']
            )
            df = pd.concat([df, df_missing], ignore_index=True)
            print("Missing personnel details appended to Excel.")
        else:
            print("No missing personnel found.")

        # Save updated Excel file
        df.to_excel(personnel_excel, index=False)
        print("✅ Excel updated successfully with House Rent Allowance and Hiring Amount status.")

    except Exception as e:
        print(f'❌ An error occurred: {str(e)}')


# Example usage
pdf_file_path = 'C:/Users/ACS/Music/Sept - 2025.pdf'
personnel_excel_path = 'C:/Users/ACS/Music/Sept - 2025.xlsx'

extract_and_append_missing_personnel(pdf_file_path, personnel_excel_path)
