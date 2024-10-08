import os
import json
import argparse
import re
import scrubadub
import scrubadub_spacy
from scrubadub.detectors import Detector
from scrubadub.filth import Filth
import scrubadub.post_processors
import hashlib
import math
from collections import defaultdict
from scrubadub import utils

brand_name_mapping = {
    "GitHub": "GHGHGH",
    "GitLab": "GLGLGL",
    "BitBucket": "BBBBBB",
    "AWS": "AWESAWESAWES",
    "Azure": "AZREAZREAZRE",
    "GCP": "GCPGCPGCP",
    "Oracle": "ORCORC",
    "Microsoft": "MCSMCS",
    "Google": "GGLGGLGGL",
    "IBM": "IBEMIBEMIBEM",
    "MySQL": "MyQLMyQLMyQL",
    "PostgreSQL": "PQLPQLPQL",
    "Postgres": "PGRPGRPGR",
    "SQL": "SQSQSQSQ",
    'Agile': 'AGAGAGAGAG',
    'SuperTest': 'STSTSTSTST',
    'Netlify': 'NLNLNLNL',
    'Software Development': 'SDSDSDSDSD',
    'NIST': 'NSTNSTNST',
    'OWASP': 'OWASWOWASOWAS',
    'Enterprise': 'ENTENTENTE',
    'Sonarqube': 'SONASONASONA',
    'Software Engineer': 'SWEWESWESW',
    'Software': 'SWSWSWSW',
    'Scrum': 'SCRSCRSCR',
}
class MappingFilthReplacer(scrubadub.post_processors.FilthReplacer):
    def __init__(self, include_hash=True, hash_salt=None, hash_length=5, replacement_map=None):
        super().__init__(include_hash=include_hash, hash_salt=hash_salt, hash_length=hash_length)
        if replacement_map is None:
            self.replacement_map = {}
        else:
            self.replacement_map = replacement_map

    def process_filth(self, filth_list):
        """Processes the filth to replace the original text and stores the mapping."""
        for filth_item in filth_list:
            # Generate the replacement label
            replacement_label = self.filth_label(filth=filth_item)

            # Extract the hash from the replacement label if it exists
            if self.include_hash:
                hash_key = replacement_label
                # Store the mapping of hash -> original text
                self.replacement_map[hash_key] = filth_item.text

            # Set the replacement string for this filth
            filth_item.replacement_string = replacement_label

        return filth_list

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
            r"Terrace", r"Place", r"Gardens", r"Way", r"Crescent", r"Square", r"Row", r"Park", r"View", r"Walk", r"Place",

        ]

        # Regex to match any text with a street type
        address_regex = re.compile(
            r'\b(?:' + '|'.join(street_types) + r')\b', re.IGNORECASE
        )

        for match in address_regex.finditer(text):
            yield AddressFilth(beg=match.start(), end=match.end(), text=match.group(), document_name=document_name)

# Custom Filth class for ad-hoc local names and misc items
class LocalMiscFilth(Filth):
    type = 'localmisc'

# Custom Detector for ad-hoc local names and misc items
class LocalMiscDetector(Detector):
    name = 'localmisc'
    local_regex = r''

    def iter_filth(self, text, document_name=None):
        misc_regex = re.compile(self.local_regex, re.IGNORECASE)
        for match in misc_regex.finditer(text):
            yield LocalMiscFilth(beg=match.start(), end=match.end(), text=match.group(), document_name=document_name)

def replace_brand_names(data: str) -> str:
    for brand, replacement in brand_name_mapping.items():
        replacement = 'REDACTED' + replacement + 'REDACTED'
        data = re.sub(brand, replacement, data, flags=re.IGNORECASE)
    return data

def restore_brand_names(data: str) -> str:
    # use the replacement map in reverse
    for brand, replacement in brand_name_mapping.items():
        replacement = 'REDACTED' + replacement + 'REDACTED'
        data = re.sub(replacement, brand, data, flags=re.IGNORECASE)
    return data

def main(file_path: str, output_file: str|None = None, local_words: list[str] = []):
    with open(file_path, "r") as f:
        data = f.read()
    candidate_surname = find_candidate_surname(data)
    surname_pattern = re.compile(re.escape(candidate_surname), re.IGNORECASE)
    data = surname_pattern.sub("SURNAME-9a9a9a", data)
    data = replace_brand_names(data)
    replacement_map = {}
    # Initialize the scrubber with the custom MappingFilthReplacer
    scrubber = scrubadub.Scrubber(post_processor_list=[
        MappingFilthReplacer(include_hash=True, hash_salt='blah-de-blah', hash_length=5, replacement_map=replacement_map),
        scrubadub.post_processors.PrefixSuffixReplacer(prefix='', suffix=''),
    ])
    scrubber.add_detector(PhoneNumberDetector())
    scrubber.add_detector(PostcodeDetector())
    scrubber.add_detector(AddressDetector())
    scrubber.add_detector(scrubadub_spacy.detectors.SpacyEntityDetector)
    if local_words:
        local_regex = r'(' + '|'.join(local_words) + r')'
        misc_detector = LocalMiscDetector()
        misc_detector.local_regex = local_regex
        scrubber.add_detector(misc_detector)
    cleaned_data = ""
    for line in data.splitlines():
        print(f"line: {line}")
        cleaned = scrubber.clean(line)
        print(f"cleaned: {cleaned}")
        cleaned_data += cleaned + "\n"
    replacement_map['SURNAME-9a9a9a'] = candidate_surname

    print(f"Replacement map: {replacement_map}")
    cleaned_data = restore_brand_names(cleaned_data)
    if output_file:
        with open(output_file, "w") as f:
            f.write(cleaned_data)
        with open(f"{output_file}_mapping.json", "w") as f:
            json.dump(replacement_map, f, indent=4)
    else:
        print(cleaned_data)

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    # mutually exclusive group for file-path and file-dir
    group = argp.add_mutually_exclusive_group(required=True)
    group.add_argument("--file-path", type=str, help="The path to the text file to anonymise. Will output to stdout.")
    group.add_argument("--file-dir", type=str, help="The path to the directory with multiple text files to anonymise. Will write the anonymised files to the same directory prefixed anon_")
    args = argp.parse_args()
    if os.path.exists('local_words.txt'):
        with open('local_words.txt', 'r') as f:
            local_words = [line.strip() for line in f.read().splitlines() if line.strip()]
    else:
        local_words = []
    if args.file_path:
        main(args.file_path, local_words=local_words)
    elif args.file_dir:
        for file in os.listdir(args.file_dir):
            main(os.path.join(args.file_dir, file), output_file=os.path.join(args.file_dir, f"anon_{file}"), local_words=local_words)
