import re
import pandas as pd
import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side, Font, Alignment


def extract_details_from_pdf(pdf_path, personnel_excel):
    try:
        # Read the personnel numbers from the provided Excel file
        df = pd.read_excel(personnel_excel)

        # Add new columns if they don't already exist
        if 'Basic Pay' not in df.columns:
            df['Basic Pay'] = None
        if 'CNIC' not in df.columns:
            df['CNIC'] = None
        if 'D.O.B' not in df.columns:
            df['D.O.B'] = None
        if 'Entry' not in df.columns:
            df['Entry'] = None

        # Clean the personnel list, ignoring empty and zero values
        personnel_list = df['Personnel'].dropna().astype(str).tolist()
        personnel_list = [
            str(int(float(num))) for num in personnel_list
            if num.strip() and num.strip() != "0"
        ]

        if not personnel_list:
            print("No valid personnel found.")
            return

        # Open the PDF and read its content
        with pdfplumber.open(pdf_path) as pdf:
            pdf_text = ''
            for page in pdf.pages:
                pdf_text += page.extract_text()

        for idx, personnel in enumerate(personnel_list):
            personnel = personnel.strip()
            basic_pay = None
            cnic = None
            dob = None
            entry_date = None
            found_pers = False

            print(f"\nSearching for Personnel # {personnel}")

            # Search for the personnel number in the PDF text
            if f"Personnel Number: {personnel}" in pdf_text:
                found_pers = True

            if found_pers:
                # Extract the basic pay, CNIC, date of birth, and entry into govt service
                pay_pattern = rf'Personnel Number: {personnel}.*?Basic Pay\s+([\d,]+\.\d{{2}})'
                cnic_pattern = rf'Personnel Number: {personnel}.*?CNIC:\s+([\d-]+)'
                # Handle both date formats: DD.MM.YYYY, DD/MM/YYYY, or DD-MM-YYYY
                dob_pattern = rf'Personnel Number: {personnel}.*?Date of Birth:\s+(\d{{2}}[./-]\d{{2}}[./-]\d{{4}})'

                # Handle variations in "Entry into Govt. Service" labeling
                entry_pattern = rf'Personnel Number: {personnel}.*?Entry into Govt[ .]*Service:\s+(\d{{2}}[./-]\d{{2}}[./-]\d{{4}})'

                pay_match = re.search(pay_pattern, pdf_text, re.DOTALL)
                cnic_match = re.search(cnic_pattern, pdf_text, re.DOTALL)
                dob_match = re.search(dob_pattern, pdf_text, re.DOTALL)
                entry_match = re.search(entry_pattern, pdf_text, re.DOTALL)

                if pay_match:
                    basic_pay = pay_match.group(1)
                if cnic_match:
                    cnic = cnic_match.group(1)
                if dob_match:
                    dob = dob_match.group(1)
                if entry_match:
                    entry_date = entry_match.group(1)

            # Update the Excel dataframe with the extracted details
            df.at[idx, 'Basic Pay'] = basic_pay if basic_pay else 'Not In Pay Roll'
            df.at[idx, 'CNIC'] = cnic if cnic else 'Not Found'
            df.at[idx, 'D.O.B'] = dob if dob else 'Not Found'
            df.at[idx, 'Entry'] = entry_date if entry_date else 'Not Found'

            print(f'Personnel #{personnel}: Basic Pay={basic_pay}, CNIC={cnic}, DOB={dob}, Entry={entry_date}')

        # Save the updated Excel file
        df.to_excel(personnel_excel, index=False)

    except Exception as e:
        print(f'An error occurred: {str(e)}')


# Example usage
pdf_path = 'C:/Users/umair/Downloads/SEPT-24.pdf'
personnel_excel_path = 'C:/Users/umair/Downloads/EmployeePayRoll.xlsx'
extract_details_from_pdf(pdf_path, personnel_excel_path)
