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

def main(file_path: str):
    with open(file_path, "r") as f:
        data = f.read()
    candidate_surname = find_candidate_surname(data)
    surname_pattern = re.compile(re.escape(candidate_surname), re.IGNORECASE)
    data = surname_pattern.sub("*****", data)
    scrubber = scrubadub.Scrubber()
    scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector)
    scrubber.add_detector(PhoneNumberDetector())
    scrubber.add_detector(PostcodeDetector())
    scrubber.add_detector(AddressDetector())
    cleaned_data = scrubber.clean(data)
    print(cleaned_data)

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--file-path", type=str, default="", help="The path to the text file to anonymise")
    args = argp.parse_args()
    main(args.file_path)
