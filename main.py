import datetime
import argparse
import re
import scrubadub
import scrubadub_spacy
from scrubadub.detectors import Detector
from scrubadub.filth import Filth

def find_candidate_surname(data: str) -> str:
    """
    Find the candidate's surname in the data.

    Examples:
    **Surname:** Smith
    return "Smith"

    Surname         Smith
    return "Smith"
    """
    pattern = r'Surname[:\s]*([A-Za-z]+)'
    match = re.search(pattern, data)
    if match:
        return match.group(1)
    raise ValueError("No surname found")

# Custom Filth class for phone numbers
class PhoneNumberFilth(Filth):
    type = 'phone_number'

# Custom Detector for phone numbers
class PhoneNumberDetector(Detector):
    name = 'phone_number'

    def iter_filth(self, text, document_name=None):
        phone_regex = re.compile(
            r'(\+44\s?\d{4}|\(?0\d{4}\)?\s?)\s?\d{3,4}\s?\d{3,4}'  # Matches +44 7478 121959, (07478) 121959, 07478 121959
        )
        for match in phone_regex.finditer(text):
            yield PhoneNumberFilth(beg=match.start(), end=match.end(), text=match.group(), document_name=document_name)

# Custom Filth class for postcodes
class PostcodeFilth(Filth):
    type = 'postcode'

# Custom Detector for UK postcodes
class PostcodeDetector(Detector):
    name = 'postcode'

    def iter_filth(self, text, document_name=None):
        postcode_regex = re.compile(r'\b[A-Z]{1,2}\d{1,2}\s*\d[A-Z]{2}\b')  # Basic regex for UK postcodes
        for match in postcode_regex.finditer(text):
            yield PostcodeFilth(beg=match.start(), end=match.end(), text=match.group(), document_name=document_name)

# Custom Filth class for addresses
class AddressFilth(Filth):
    type = 'address'

# Custom Detector for UK street types
class AddressDetector(Detector):
    name = 'address'

    def iter_filth(self, text, document_name=None):
        # Common UK street types
        street_types = [
            r"Street", r"St", r"Road", r"Rd", r"Avenue", r"Ave", r"Lane", r"Ln", r"Drive", r"Dr", r"Close", r"Court", r"Ct",
            r"Terrace", r"Place", r"Gardens", r"Way", r"Crescent", r"Square", r"Row", r"Park", r"View", r"Walk"
        ]

        # Regex to match any address that ends with a street type
        address_regex = re.compile(
            r'\b[\w\s.,/-]*\b(?:' + '|'.join(street_types) + r')\b', re.IGNORECASE
        )

        for match in address_regex.finditer(text):
            yield AddressFilth(beg=match.start(), end=match.end(), text=match.group(), document_name=document_name)

def replace_brand_names(data: str) -> str:
        # case insensitive replacement of 'github' with 'GHGHGH'
    data = re.sub(r'github', 'GHGHGH', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'gitlab' with 'GLGLGL'
    data = re.sub(r'gitlab', 'GLGLGL', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'bitbucket' with 'BBBBBB'
    data = re.sub(r'bitbucket', 'BBBBBB', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'aws' with 'AWSAWSAWS'
    data = re.sub(r'aws', 'AWSAWSAWS', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'azure' with 'AZUREAZUREAZURE'
    data = re.sub(r'azure', 'AZUREAZUREAZURE', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'gcp' with 'GCPGCPGCP'
    data = re.sub(r'gcp', 'GCPGCPGCP', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'oracle' with 'ORCORC'
    data = re.sub(r'oracle', 'ORCORC', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'microsoft' with 'MCSMCS'
    data = re.sub(r'microsoft', 'MCSMCS', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'google' with 'GGLGGLGGL'
    data = re.sub(r'google', 'GGLGGLGGL', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'ibm' with 'IBMIBMIBM'
    data = re.sub(r'ibm', 'IBMIBMIBM', data, flags=re.IGNORECASE)
    return data

def restore_brand_names(data: str) -> str:
    # case insensitive replacement of 'GHGHGH' with 'github'
    data = re.sub(r'GHGHGH', 'GitHub', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'GLGLGL' with 'gitlab'
    data = re.sub(r'GLGLGL', 'GitLab', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'BBBBBB' with 'bitbucket'
    data = re.sub(r'BBBBBB', 'BitBucket', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'AWSAWSAWS' with 'aws'
    data = re.sub(r'AWSAWSAWS', 'AWS', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'AZUREAZUREAZURE' with 'azure'
    data = re.sub(r'AZUREAZUREAZURE', 'Azure', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'GCPGCPGCP' with 'gcp'
    data = re.sub(r'GCPGCPGCP', 'GCP', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'ORCORC' with 'oracle'
    data = re.sub(r'ORCORC', 'Oracle', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'MCSMCS' with 'microsoft'
    data = re.sub(r'MCSMCS', 'Microsoft', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'GGLGGLGGL' with 'google'
    data = re.sub(r'GGLGGLGGL', 'Google', data, flags=re.IGNORECASE)
    # case insensitive replacement of 'IBMIBMIBM' with 'ibm'
    data = re.sub(r'IBMIBMIBM', 'IBM', data, flags=re.IGNORECASE)
    return data

def main(file_path: str):
    with open(file_path, "r") as f:
        data = f.read()
    candidate_surname = find_candidate_surname(data)
    surname_pattern = re.compile(re.escape(candidate_surname), re.IGNORECASE)
    data = surname_pattern.sub("*****", data)
    data = replace_brand_names(data)
    scrubber = scrubadub.Scrubber()
    scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector)
    scrubber.add_detector(PhoneNumberDetector())
    scrubber.add_detector(PostcodeDetector())
    scrubber.add_detector(AddressDetector())
    cleaned_data = scrubber.clean(data)
    cleaned_data = restore_brand_names(cleaned_data)
    print(cleaned_data)

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--file-path", type=str, required=True, help="The path to the text file to anonymise")
    args = argp.parse_args()
    main(args.file_path)
