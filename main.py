import re
try:
    def extract_basic_pay(path, personnel):
        try:
            # Open the text file and read lines
            with open(path, 'r', encoding='utf-8', errors='replace') as file:
                lines = file.readlines()

            basic_pay = None
            found_pers = False
            pers_column = None  # To track which column the personnel number was found in

            # Iterate through the lines of the file
            for line in lines:
                # Check if the current line contains the exact "Pers #"
                # Check if the current line contains the exact "Pers #"
                left_column = line[:80].strip()
                right_column = line[80:].strip()

                if f"Pers #: {personnel}" in left_column:
                    print(f'Personnel record found in left column: {left_column}')
                    found_pers = True
                    pers_column = 'left'
                    continue  # Skip to the next line to find "Basic Pay"

                elif f"Pers #: {personnel}" in right_column:
                    print(f'Personnel record found in right column: {right_column}')
                    found_pers = True
                    pers_column = 'right'
                    continue  # Skip to the next line to find "Basic Pay"

                # If we found the personnel number, look for "Basic Pay"
                if found_pers and "0001-Basic Pay" in line:
                    # Debugging output for columns
                    print(f'Checking for Basic Pay in line: {line.strip()}')

                    # Use regex to find the basic pay
                    pay_pattern = r'0001-Basic Pay\s+([\d,]+\.\d{2})'
                    left_match = re.search(pay_pattern, left_column)
                    right_match = re.search(pay_pattern, right_column)

                    if left_match and pers_column == 'left':
                        basic_pay = left_match.group(1)
                        print(f'Basic Pay found in left column: {basic_pay}')
                    elif right_match and pers_column == 'right':
                        basic_pay = right_match.group(1)
                        print(f'Basic Pay found in right column: {basic_pay}')

                    # Stop searching once basic pay is found
                    if basic_pay:
                        break

            # Output result
            if basic_pay:
                print(f'Basic Pay for Pers # {pers_number}: {basic_pay}')
            else:
                print(f'Basic Pay not found for Pers # {pers_number}')

        except Exception as e:
            print(f'An error occurred: {str(e)}')


    # Example usage
    file_path = 'C:/Users/umair/Downloads/AUG-24.txt'
    pers_number = '50564658'  # Example personnel number
    extract_basic_pay(file_path, pers_number)


except Exception as e:
    print(str(e))
