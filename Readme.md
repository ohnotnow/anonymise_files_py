# Anonymization Script

This Python script anonymizes sensitive information from text files, including surnames, phone numbers, postcodes, and addresses, primarily designed to work with UK-based data. The script leverages the `scrubadub` library along with custom detectors for postcodes, phone numbers, and addresses.

## Features
- Detects and anonymizes surnames found in text.
- Anonymizes phone numbers, postcodes, and addresses using custom detectors.
- Removes named entities like organizations and locations using `scrubadub` and `spaCy`.

## Requirements

Ensure you have Python installed and `git` available on your system. You will also need to have `scrubadub` and `spaCy` installed, along with some additional dependencies.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ohnotnow/anonymise_files_py
   cd anonymise_files_py
   ```

2. **Set up a virtual environment:**

   On MacOS and Ubuntu:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Additional steps:**

   Some users may need to run the following additional commands to ensure compatibility with the latest version of `scrubadub` and its dependencies:

   ```bash
   pip install -U pydantic pydantic_core
   python -m spacy download en_core_web_sm
   ```

## Usage

To run the anonymization script on a singletext file, use the following command:

```bash
python main.py --file-path <path-to-your-text-file>
```

Replace `<path-to-your-text-file>` with the path to the text file you wish to anonymize.

### Example

```bash
python main.py --file-path sample.txt
```

The script will process the text file, detect and anonymize sensitive information, and print the cleaned data.  If you are getting some debug errors from scrubadub, but the anonymisation is working as expected, you can run :

```bash
python main.py --file-path sample.txt 2>/dev/null
```

If you have a directory of files, you can use the following command:

```bash
python main.py --file-dir /path/to/your/directory
```

This will process all the files in the specified directory and write the anonymised files to the same directory prefixed `anon_`.

## License

This project is licensed under the MIT License.
