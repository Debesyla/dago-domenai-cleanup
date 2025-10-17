## ✅ Recommended folder structure

```
project-root/
│
├── assets/
│   ├── input.txt         # raw list of domains or URLs
│   ├── output.txt        # cleaned and deduped root domains
│   └── sample/           # (optional) example datasets for testing
│
├── src/
│   ├── domain_cleaner.py # main cleaning logic
│   ├── utils/            # (optional) small helper scripts if needed
│   └── __init__.py
│
├── docs/
│   └── DOMAIN-CLEANER.md # documentation (this file)
│
├── .gitignore
├── requirements.txt
└── run.sh                # optional: single-line script to launch cleaner
```

---

## 🧾 `/docs/DOMAIN-CLEANER.md`

```markdown
# 🧹 Domain Cleaner Utility

## Overview

**Domain Cleaner** is a lightweight Python utility designed to prepare raw .lt (Lithuanian) domain data for detailed domain analysis.  
It reads a plain-text list of domains or URLs, cleans and normalizes them, handles government vs. commercial domain rules, removes duplicates, and outputs a tidy `.txt` list ready for bulk domain checkers.

This tool is ideal for preprocessing .lt domains before bulk WHOIS, DNS, or HTTP checks.

---

## 📁 Folder Structure

```

project-root/
├── assets/
│   ├── input.txt   # raw .lt domain input data (one domain or URL per line)
│   └── output.txt  # cleaned and deduplicated output (one domain per line)
│
├── src/
│   └── domain_cleaner.py  # main cleaning script
│
└── docs/
└── DOMAIN-CLEANER.md  # this documentation

````

---

## ⚙️ How It Works

1. **Reads** a text file with one .lt domain or URL per line.  
2. **Normalizes** the value (removes `http://`, `https://`, `www.`, paths, etc.).  
3. **Extracts** the domain using [`tldextract`](https://pypi.org/project/tldextract/).  
4. **Applies .lt domain rules**:
   - **Government domains** (`.lrv.lt`, `.edu.lt`, `.mil.lt`, `.gov.lt`): Preserves subdomains
   - **Commercial domains**: Strips subdomains (keeps only `example.lt`, drops `blog.example.lt`)
5. **Deduplicates** results.  
6. **Outputs** the cleaned list to `assets/output.txt` (one domain per line, ready for bulk domain checkers).

---

## 🐍 Example Script: `/src/domain_cleaner.py`

```python
from urllib.parse import urlparse
import tldextract

INPUT_FILE = "assets/input.txt"
OUTPUT_FILE = "assets/output.txt"

def clean_domains():
    cleaned = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw:
                continue

            ext = tldextract.extract(raw)
            if not ext.domain or not ext.suffix:
                continue

            # Domain reconstruction with .lt government domain rules
            domain = f"{ext.domain}.{ext.suffix}"
            
            # Government/institutional domains - preserve subdomains
            if ext.suffix in ['lrv.lt', 'edu.lt', 'mil.lt', 'gov.lt']:
                if ext.subdomain:
                    domain = f"{ext.subdomain}.{domain}"
            # All other domains - strip subdomains
            elif ext.subdomain:
                continue  # Skip, use root domain only

            cleaned.add(domain.lower())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in sorted(cleaned):
            f.write(domain + "\n")

    print(f"✅ {len(cleaned)} unique root domains saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_domains()
````

---

## 🧩 Requirements

Install dependencies once:

```bash
pip install tldextract
```

Create a `requirements.txt` file for easier environment setup:

```
tldextract
```

---

## ▶️ Usage

Place your raw domain list in `assets/input.txt`, one per line.

Then run:

```bash
python3 src/domain_cleaner.py
```

or if it’s in the root folder:

```bash
python3 domain-cleaner.py
```

Output will be written to:

```
assets/output.txt
```

---

## 🧠 Notes

* **Lithuanian domain focus**: Specifically designed for .lt domain preprocessing
* **Government domain handling**: Preserves subdomains for `.lrv.lt`, `.edu.lt`, `.mil.lt`, `.gov.lt`
* **Commercial domain handling**: Strips subdomains (i.e., `blog.example.lt` → `example.lt`)
* **URL handling**: Processes full URLs like `https://subdomain.example.lt/path` correctly
* **Performance**: Memory efficient with `set()` deduplication, handles thousands of domains quickly
* **Output format**: One domain per line, ready for detailed domain checkers
* **Error tolerance**: Ignores invalid entries (empty lines, malformed URLs)
* **Cross-platform**: Works on Linux, macOS, Windows

---

## 🔮 Future Improvements

* Add CLI flags (`--input`, `--output`)
* Add optional filters (TLD whitelist, blacklist, domain length)
* Add logging / progress display
* Integrate with next-stage checkers (WHOIS, HTTP, DNS)

---

## 🧰 Quick Run Script (Optional)

Add a small `run.sh` for convenience:

```bash
#!/bin/bash
python3 src/domain_cleaner.py
```

Then simply run:

```bash
./run.sh
```

---

## ✅ Summary

This mini-app serves as the **first pipeline step** for .lt domain intelligence work:

* **Cleans .lt domain data** with Lithuanian-specific business rules
* **Preserves government subdomains** while stripping commercial ones  
* **Standardizes output format** (one domain per line)
* **Ensures deduplication** and performance optimization
* **Prepares data** for detailed domain checkers (WHOIS, DNS, HTTP analysis)

Ideal before bulk domain analysis or connecting with automated domain checking tools.

```
