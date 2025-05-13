from pdf2image import convert_from_path
import pytesseract
import pandas as pd

try:
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Your path may be different

    # Convert PDF to images (one per page)
    images = convert_from_path(
        'C:/Users/ACS/Downloads/hris_data.pdf',
        500,
        poppler_path=r'C:/poppler-24.08.0/Library/bin'
    )

    # Initialize an empty list to hold the rows of the table
    table_data = []

    # Process each page individually
    for page_num, img in enumerate(images, start=1):
        print(f"Extracting text from page {page_num}...")
        text = pytesseract.image_to_string(img)
        lines = text.split('\n')

        # Process each line from the extracted text
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespaces
            columns = line.split()  # Split by space to get columns

            # Check if the line has at least 5 columns (S#, Name, Father's Name, CNIC, Designation)
            if len(columns) >= 5:
                s_no = columns[0]
                name = columns[1] + " " + columns[2]  # Name can be in two parts
                father_name = columns[3]
                cnic = columns[4]
                designation = " ".join(columns[5:])  # Remaining part is Designation

                # Append the extracted data to the table_data list
                table_data.append([s_no, name, father_name, cnic, designation])

    # Convert the collected data into a pandas DataFrame (tabular form)
    df = pd.DataFrame(table_data, columns=['S#', 'Name', 'Father\'s Name', 'CNIC', 'Designation'])

    # Save the DataFrame to an Excel file
    df.to_excel('extracted_data.xlsx', index=False)

    print("✅ Data successfully extracted and saved to 'extracted_data.xlsx'.")

except Exception as e:
    print(f"❌ Error: {e}")
