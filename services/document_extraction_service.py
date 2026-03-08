import re
import logging
import boto3
from typing import Dict, Any
from models.config import Settings

logger = logging.getLogger(__name__)

class TextractService:
    def __init__(self):
        self.settings = Settings()
        client_kwargs = {
            "region_name": self.settings.aws_region
        }
        if getattr(self.settings, "aws_access_key_id", None) and getattr(self.settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = self.settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = self.settings.aws_secret_access_key
            
        self.textract = boto3.client(
            service_name='textract',
            **client_kwargs
        )

    def extract_document_data(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts structured fields from document bytes using Amazon Textract analyze_document.
        Falls back to regex heuristics over raw text if structured detection fails.
        """
        try:
            # Upgrade from detect_document_text to analyze_document for precise Form detection
            response = self.textract.analyze_document(
                Document={'Bytes': file_bytes},
                FeatureTypes=["FORMS", "TABLES"]
            )
            
            blocks = response.get("Blocks", [])
            extracted_text = ""
            key_map = {}
            value_map = {}
            block_map = {}

            # Build block map and extract raw text for regex fallbacks
            for item in blocks:
                block_map[item['Id']] = item
                if item["BlockType"] == "LINE":
                    extracted_text += item["Text"] + "\n"
                elif item["BlockType"] == "KEY_VALUE_SET":
                    if 'KEY' in item.get('EntityTypes', []):
                        key_map[item['Id']] = item
                    elif 'VALUE' in item.get('EntityTypes', []):
                        value_map[item['Id']] = item

            def get_text_from_block(block):
                text = ""
                if 'Relationships' in block:
                    for relationship in block['Relationships']:
                        if relationship['Type'] == 'CHILD':
                            for child_id in relationship['Ids']:
                                word = block_map[child_id]
                                if word['BlockType'] == 'WORD':
                                    text += word['Text'] + " "
                                elif word['BlockType'] == 'SELECTION_ELEMENT':
                                    if word['SelectionStatus'] == 'SELECTED':
                                        text += "X "
                return text.strip()

            # Link Keys to Values
            kvs = {}
            for block_id, key_block in key_map.items():
                if 'Relationships' in key_block:
                    for relationship in key_block['Relationships']:
                        if relationship['Type'] == 'VALUE':
                            for val_id in relationship['Ids']:
                                value_block = value_map[val_id]
                                key = get_text_from_block(key_block)
                                val = get_text_from_block(value_block)
                                kvs[key.lower()] = val
            
            logger.info("Textract OCR successful", extra={"event": "textract_success", "fields_detected": len(kvs)})
            
            # --- Field Extraction Logic ---
            name_val = None
            aadhaar_val = None
            age_val = None

            # 1. Search Structured KVS first
            for k, v in kvs.items():
                if "name" in k or "father" not in k and "name" in k:
                    name_val = v
                if "dob" in k or "date of birth" in k or "yob" in k or "year of birth" in k:
                    try:
                        import datetime
                        # naive extraction if it's just a year "1995" or "04/05/1995"
                        year_match = re.search(r"(19[0-9]{2}|20[0-9]{2})", v)
                        if year_match:
                            age_val = datetime.datetime.now().year - int(year_match.group(1))
                        dob_val = v
                    except:
                        pass
                if "aadhaar" in k or "id" in k:
                     aadhaar_match = re.search(r"(\d{4}[\s-]?\d{4}[\s-]?\d{4})", v)
                     if aadhaar_match:
                         aadhaar_val = aadhaar_match.group(1)
                if "income" in k or "salary" in k or "earnings" in k:
                    income_match = re.search(r"(\d+)", v.replace(',', ''))
                    if income_match:
                        income_val = income_match.group(1)

            # 2. Fallback to raw LINE regex if KVS missed them (common in poorly scanned IDs)
            if not aadhaar_val:
                aadhaar_match = re.search(r"(\d{4}[\s-]?\d{4}[\s-]?\d{4})", extracted_text)
                if aadhaar_match:
                    aadhaar_val = aadhaar_match.group(1).replace('-', ' ')
                    
            if not name_val:
                name_match = re.search(r"(?:Name|NAME|ame)[\s:;\-]+([A-Za-z\s]+?)(?=\n|\r|$|[0-9])", extracted_text, re.IGNORECASE)
                if name_match:
                    name_val = name_match.group(1).strip()
            
            if not dob_val if 'dob_val' in locals() else True:
                dob_match = re.search(r"(?:DOB|Date of Birth|Birth)[\s:;\-]+(\d{2}/\d{2}/\d{4})", extracted_text, re.IGNORECASE)
                if dob_match:
                    dob_val = dob_match.group(1)
                    
            if not age_val:
                yob = re.search(r"(?:YOB|Year of Birth)[\s:;\-]+(19[0-9]{2}|20[0-9]{2})", extracted_text, re.IGNORECASE)
                if yob:
                    try:
                        import datetime
                        age_val = datetime.datetime.now().year - int(yob.group(1))
                    except:
                        pass

            return {
                "raw_text": extracted_text,
                "structured_forms": kvs,
                "extracted_fields": {
                    "aadhaar": aadhaar_val,
                    "name": name_val,
                    "dob": dob_val if 'dob_val' in locals() else None,
                    "income": income_val if 'income_val' in locals() else None
                }
            }
            
        except Exception as e:
            logger.error("Textract processing failed", extra={"event": "textract_error", "error": str(e)})
            raise

    def extract_income_data(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extract script specifically for Income Certificate using Regex patterns.
        """
        try:
            response = self.textract.detect_document_text(
                Document={'Bytes': file_bytes}
            )
            blocks = response.get("Blocks", [])
            extracted_text = "\n".join([item["Text"] for item in blocks if item["BlockType"] == "LINE"])
            
            # Keyword validation
            keywords = ["income certificate", "annual income", "revenue department"]
            if not any(kw in extracted_text.lower() for kw in keywords):
                raise ValueError("Income certificate keywords not found")

            # Extract Annual Income
            income_pattern = r"(?:Annual Income|Income).*?(\d{1,3},?\d{3,6})"
            income_match = re.search(income_pattern, extracted_text, re.IGNORECASE)
            annual_income = income_match.group(1).replace(',', '') if income_match else None
            if not annual_income:
                # Fallback to general number extraction next to 'Rs'
                rs_match = re.search(r"(?:Rs\.?|Rupees|INR)[\s]*([\d,]+)", extracted_text, re.IGNORECASE)
                if rs_match:
                    annual_income = rs_match.group(1).replace(',', '')

            # Extract Name
            name_pattern = r"(?:Shri|Smt|Kumari|Sri|Mrs\.|Mr\.)\s+([A-Za-z\s]+?)(?=\s+(?:S/o|D/o|W/o|,|\n))"
            name_match = re.search(name_pattern, extracted_text, re.IGNORECASE)
            name_val = name_match.group(1).strip() if name_match else None
            if not name_val:
                name_match_alt = re.search(r"(?:Name|NAME|ame)[\s:;\-]+([A-Za-z\s]+?)(?=\n|\r|$|[0-9])", extracted_text, re.IGNORECASE)
                if name_match_alt:
                    name_val = name_match_alt.group(1).strip()
            
            # Extract Issuing Authority
            authority_pattern = r"(?:Issuing Authority|Issued by)[\s:;\-]+([A-Za-z\s]+?)(?=\n|\r|$)"
            authority_match = re.search(authority_pattern, extracted_text, re.IGNORECASE)
            authority_val = authority_match.group(1).strip() if authority_match else "Tahsildar"
            
            # Certificate Number
            cert_pattern = r"(?:Certificate No|Application No|Ref No)[\.\s:;\-]+([A-Z0-9\/\-]+)"
            cert_match = re.search(cert_pattern, extracted_text, re.IGNORECASE)
            cert_val = cert_match.group(1).strip() if cert_match else None

            logger.info("Income Certificate OCR successful", extra={"event": "income_ocr_success"})
            
            return {
                "raw_text": extracted_text,
                "extracted_data": {
                    "name": name_val,
                    "annual_income": annual_income,
                    "issuing_authority": authority_val,
                    "certificate_number": cert_val
                }
            }
        except Exception as e:
            logger.error("Textract processing failed for income cert", extra={"event": "textract_income_error", "error": str(e)})
            raise
