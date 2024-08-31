# import re
# import pandas as pd
#
# # Step 1: Read the content of the text file
# with open('C:/Users/umair/Downloads/July-24.txt', 'r') as file:
#     content = file.read()
#
# # Step 2: Define patterns for extracting data, including the new allowances
# patterns = {
#     "Pers_No": r"Pers #: (\d+)",
#     "Name": r"Name:\s+([A-Z\s]+)",
#     "CNIC_No": r"CNIC No\.(\d+)",
#     "Basic_Pay": r"0001-Basic Pay\s+([\d,]+\.\d{2})",
#     "Qualification_Pay": r"0010-Qualification Pay\s+([\d,]+\.\d{2})",
#     "Entertainment_Allowance": r"1518-Entertainment Allowance\s+([\d,]+\.\d{2})",
#     "Orderly_Allowance": r"1540-Orderly Allowance\s+([\d,]+\.\d{2})",
#     "Medical_Allowance": r"1947-Medical Allow\s+([\d,]+\.\d{2})",
#     "Performance_Allowance": r"2114-Performance Allowance FBR\s+([\d,]+\.\d{2})",
#     "Fixed_FBR_Incentive": r"2215-Fixed FBR Incentive\s+([\d,]+\.\d{2})",
#     "Adhoc_Rel_Al_15_22_PS17": r"2347-Adhoc Rel Al 15% 22\(PS17\)\s+([\d,]+\.\d{2})",
#     "Adhoc_Relief_2023_35": r"2378-Adhoc Relief All 2023 35%\s+([\d,]+\.\d{2})",
#     "Adhoc_Relief_2024_25": r"2393-Adhoc Relief All 2024 25%\s+([\d,]+\.\d{2})",
#     "GPF_Balance": r"GPF Balance\s+([\d,]+\.\d{2})",
#     "Total_Deductions": r"Total Deductions\s+([\d,]+\.\d{2})",
#     "Net_Amount": r"(\d{3},\d{3}\.\d{2})",
#     "DOB": r"D\.O\.B\s+(\d{2}\.\d{2}\.\d{4})",
# }
#
# # Step 3: Split content into individual records
# records = content.split('Karachi-Sub Off')
#
# # Step 4: Extract data for each record
# extracted_data = []
# for record in records[1:]:  # Skipping the first split part which might be empty
#     data = {key: re.search(pattern, record).group(1) if re.search(pattern, record) else None
#             for key, pattern in patterns.items()}
#     extracted_data.append(data)
#
# # Step 5: Convert the list of dictionaries to a DataFrame
# df = pd.DataFrame(extracted_data)
#
# # Step 6: Display or save the DataFrame
# print(df)
# df.to_csv('C:/Users/umair/Downloads/extracted_data.csv', index=False)
#
#

