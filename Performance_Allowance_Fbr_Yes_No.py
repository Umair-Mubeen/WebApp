import re
import pandas as pd
import pdfplumber

def extract_and_append_missing_personnel(pdf_path, personnel_excel):
    try:
        # Load personnel Excel file
        df = pd.read_excel(personnel_excel)

        # Ensure required columns exist
        for column in ['Personnel', 'Name', 'Designation',  'Performance Allowance']:
            if column not in df.columns:
                df[column] = None

        # Clean personnel numbers
        personnel_list = df['Personnel'].dropna().astype(str).tolist()
        personnel_list = [
            str(int(float(num))) for num in personnel_list if num.strip() and num.strip() != "0"
        ]

        # Track found items
        found_perf_allow = set()
        missing_data = []

        # Read PDF pages
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                # Extract personnel numbers on this page
                personnel_matches = re.findall(r'Personnel Number:\s*(\d+)', text)

                # Check for Performance Allowance FBR
                has_performance_allowance = "Performance Allowance FBR" in text

                for personnel in personnel_matches:
                    if has_performance_allowance:
                        found_perf_allow.add(personnel)

                    # Handle missing personnel
                    if personnel not in personnel_list:
                        print(f"Missing Personnel Found: {personnel}")

                        # Extract Name
                        name_match = re.search(r'Name:\s*([A-Za-z\s]+)', text)
                        name = name_match.group(1).strip() if name_match else "Unknown"

                        # Extract Designation
                        desig_match = re.search(r'Designation\s*:\s*([A-Za-z\s]+)', text)
                        designation = desig_match.group(1).strip() if desig_match else "Unknown"


                        perf_status = "Yes" if has_performance_allowance else "No"


        # Update existing Excel data
        df['Personnel'] = df['Personnel'].astype(str)

        df['Performance Allowance'] = df['Personnel'].apply(
            lambda x: "Yes" if x in found_perf_allow else "No"
        )

        # Append missing personnel if any
        if missing_data:
            df_missing = pd.DataFrame(
                missing_data,
                columns=['Personnel', 'Name', 'Designation', 'Performance Allowance']
            )
            df = pd.concat([df, df_missing], ignore_index=True)
            print("Missing personnel details appended to Excel.")
        else:
            print("No missing personnel found.")

        # Save Excel
        df.to_excel(personnel_excel, index=False)
        print("✅ Excel updated successfully with Performance Allowance status.")

    except Exception as e:
        print(f'❌ An error occurred: {str(e)}')


# Example usage
pdf_file_path = 'C:/Users/ACS/Music/Sept - 2025.pdf'
personnel_excel_path = 'C:/Users/ACS/Music/Sept - 2025.xlsx'

extract_and_append_missing_personnel(pdf_file_path, personnel_excel_path)
