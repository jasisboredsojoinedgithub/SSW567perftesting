# Requirement 1: 
# The system shall be able to scan the MRZ of a travel document using a hardware device scanner 
# and get the information in MRZ as two strings (line 1 and line 2). This is a placeholder for the software part.
def scanMRZ():
    pass

# Requirement 2: 
# The system shall be able to decode the two strings from specification #1 into their respective fields 
# and identify the respective check digits for the fields.
def decodeMRZ(line1, line2):
    decodedlinesdic = {
        "document-type": line1[0],
        "issuing-country": line1[2:5],
        "last-name": line1[5:].split("<<")[0].replace("<", " ").strip(),
        "first-name": line1[5:].split("<<")[1].replace("<", " ").strip() if "<<" in line1[5:] else "",
        "passport-number": line2[:9],
        "passport-check-digit": line2[9],
        "country-code": line2[10:13],
        "birth-date": line2[13:19],
        "birth-date-check-digit": line2[19],
        "sex": line2[20],
        "expiration-date": line2[21:27],
        "expiration-date-check-digit": line2[27],
        "personal-number": line2[28:42],
        "personal-number-check-digit": line2[42],
    }
    return decodedlinesdic

# Requirement 3:
# The system shall be able to encode travel document information fields queried from a database 
# into the two strings for the MRZ in a travel document. This is the opposite process compared to requirement #2.
def encodeMRZ(fields):
    line1 = f"P<{fields['issuing-country']}{fields['last-name']}<<{fields['first-name'].replace(' ', '<')}".ljust(44, "<")
    
    # Format personal number to ensure it's the correct length
    personal_number = fields['personal-number']
    if len(personal_number) > 14:  # Truncate if too long
        personal_number = personal_number[:14]
    elif len(personal_number) < 14:  # Pad if too short
        personal_number = personal_number.ljust(14, "<")
    
    line2 = (
        f"{fields['passport-number']}"
        f"{fields['passport-check-digit']}"
        f"{fields['country-code']}"
        f"{fields['birth-date']}"
        f"{fields['birth-date-check-digit']}"
        f"{fields['sex']}"
        f"{fields['expiration-date']}"
        f"{fields['expiration-date-check-digit']}"
        f"{personal_number}"
        f"{fields['personal-number-check-digit']}"
    )
    # Ensure line2 is exactly 44 characters without extra padding
    line2 = line2[:44]  # Truncate if longer than 44 characters
    
    return line1, line2

# Requirement 4:
# The system shall be able to report a mismatch between certain information fields and the check digit.
# The system shall report where the mismatch happened, i.e., which information field does not match its respective check digit.
def calculate_check_digit(field):
    weightingsequence = [7, 3, 1]
    total = 0
    
    for i in range(len(field)):
        char = field[i]
        if char.isalpha():
            value = ord(char.upper()) - 55  
        elif char.isdigit():
            value = int(char)
        else:
            value = 0  
        
        total += value * weightingsequence[i % 3]
    
    return total % 10

def mismatch(decodedlinesdic):
    mismatches = []
    
    fields_to_check = [
        ("passport-number", "passport-check-digit", "Passport Number"),
        ("birth-date", "birth-date-check-digit", "Birth Date"),
        ("expiration-date", "expiration-date-check-digit", "Expiration Date"),
        ("personal-number", "personal-number-check-digit", "Personal Number"),
    ]

    for field, check_digit_field, label in fields_to_check:
        if calculate_check_digit(decodedlinesdic[field]) != int(decodedlinesdic[check_digit_field]):
            mismatches.append(f"{label} there is a mismatch in the digit check")  
    
    return mismatches


if __name__ == "__main__":
    line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<"
    line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<1"

    fields = decodeMRZ(line1, line2)
    print("Decoded MRZ:", fields)

    mismatches = mismatch(fields)
    if mismatches:
        print("Mismatches Found:", mismatches)
    else:
        print("All check digits match.")
