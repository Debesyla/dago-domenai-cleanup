# Domain Cleaner for .lt Domains

A lightweight Python utility for cleaning and deduplicating Lithuanian (.lt) domain lists. Designed for preprocessing before bulk domain analysis (WHOIS, DNS, HTTP checks).

## Features
- **Strict .lt filtering:** Only outputs .lt domains
- **Government domain logic:** Preserves subdomains for `.gov.lt`, `.lrv.lt`, `.edu.lt`, `.mil.lt`
- **Commercial domain logic:** Strips subdomains for all other .lt domains
- **Deduplication & sorting:** Output is unique, lowercase, and alphabetically sorted
- **Ready for bulk checkers:** Output is one domain per line

## Usage

1. Place your raw .lt domain list (one domain or URL per line) in `assets/input.txt`.
2. Run the cleaner:
   ```bash
   python3 src/domain_cleaner.py
   # or
   ./run.sh
   ```
3. Find cleaned domains in `assets/output.txt`.

## Example
**Input (`assets/input.txt`):**
```
debesyla.lt
blog.debesyla.lt
lrs.lrv.lt
info.edu.lt
portal.mil.lt
services.gov.lt
alfa.lt
example.com
```

**Output (`assets/output.txt`):**
```
alfa.lt
debesyla.lt
info.edu.lt
lrs.lrv.lt
portal.mil.lt
services.gov.lt
```

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```

## How It Works
- Reads each line from `assets/input.txt`
- Extracts domain parts using `tldextract`
- Applies Lithuanian government/commercial domain rules
- Deduplicates and sorts output
- Skips non-.lt domains, empty lines, and malformed entries

## Performance
- Memory efficient: processes line-by-line, uses `set()` for deduplication
- Fast: handles thousands of domains in seconds

## Documentation
See [`docs/DOMAIN-CLEANER.md`](docs/DOMAIN-CLEANER.md) for full details, architecture, and extension points.

## License
MIT
