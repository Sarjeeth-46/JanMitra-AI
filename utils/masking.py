import re

def mask_aadhaar(aadhaar: str) -> str:
    """ Masks Aadhaar number, revealing only the last 4 digits. """
    if not aadhaar:
        return aadhaar
    
    # Remove all formatting characters first
    clean_aadhaar = re.sub(r'[\s\-]', '', str(aadhaar))
    
    if len(clean_aadhaar) < 4:
        return "****"
        
    return "XXXX XXXX " + clean_aadhaar[-4:]

def mask_phone(phone: str) -> str:
    """ Masks Indian phone numbers, keeping the first 2 and last 2 digits. """
    if not phone:
        return phone
        
    clean_phone = re.sub(r'\D', '', str(phone))
    
    if len(clean_phone) != 10:
        return "****"
        
    return f"{clean_phone[:2]}******{clean_phone[-2:]}"

def mask_income(income: int | str) -> str:
    """ Masks specific financial figures into broad categories. """
    try:
        val = int(income)
        if val <= 50000:
            return "Below 50k"
        elif val <= 250000:
            return "50k - 2.5L"
        elif val <= 500000:
            return "2.5L - 5L"
        elif val <= 800000:
            return "5L - 8L"
        else:
            return "Above 8L"
    except (ValueError, TypeError):
        return "Unknown"

def mask_dob(dob: str) -> str:
    """ Masks Date of Birth, revealing only the year (e.g. XX/XX/1990). """
    if not dob:
        return dob
    
    # Very naive regex extraction for a 4 digit year at the end
    match = re.search(r'(\d{4})', str(dob))
    if match:
        return f"XX/XX/{match.group(1)}"
    return "XX/XX/XXXX"

def mask_dict_pii(data: dict) -> dict:
    """
    Recursively scans a dictionary and masks PII fields like 'aadhaar', 'phone', 'income', 'dob'.
    Leaves non-PII fields untouched. Safe for deeply nested payloads.
    """
    if not isinstance(data, dict):
        return data

    masked_data = {}
    for key, value in data.items():
        lower_key = str(key).lower()
        
        if isinstance(value, dict):
            masked_data[key] = mask_dict_pii(value)
        elif isinstance(value, list):
            masked_data[key] = [mask_dict_pii(item) if isinstance(item, dict) else item for item in value]
        elif 'aadhaar' in lower_key:
            masked_data[key] = mask_aadhaar(str(value))
        elif 'phone' in lower_key or 'mobile' in lower_key:
            masked_data[key] = mask_phone(str(value))
        elif 'income' in lower_key:
            masked_data[key] = mask_income(value)
        elif 'dob' in lower_key or 'birth' in lower_key:
            masked_data[key] = mask_dob(str(value))
        else:
            masked_data[key] = value

    return masked_data
