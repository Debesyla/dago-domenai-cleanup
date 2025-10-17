
import tldextract
from pathlib import Path

INPUT_FILE = Path("assets/input.txt")
OUTPUT_FILE = Path("assets/output.txt")

GOV_DOMAINS = {"lrv", "edu", "mil"}  # Lithuanian government/institutional domains

def clean_domains():
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    cleaned = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        line_count = 0
        for line in f:
            line_count += 1
            if line_count % 1000 == 0:
                print(f"...processed {line_count} lines...")

            raw = line.strip()
            if not raw:
                continue

            ext = tldextract.extract(raw)
            if not ext.domain or not ext.suffix:
                continue

            # Only process .lt domains (including .gov.lt)
            if ext.suffix == "gov.lt":
                # .gov.lt is a special suffix recognized by tldextract
                domain = f"{ext.domain}.{ext.suffix}"
                if ext.subdomain:
                    domain = f"{ext.subdomain}.{domain}"
                cleaned.add(domain.lower())
            elif ext.suffix == "lt":
                if ext.domain in GOV_DOMAINS:
                    # Lithuanian government domains (lrv.lt, edu.lt, mil.lt)
                    domain = f"{ext.domain}.{ext.suffix}"
                    if ext.subdomain:
                        domain = f"{ext.subdomain}.{domain}"
                    cleaned.add(domain.lower())
                else:
                    # Commercial .lt domains: strip subdomains
                    if ext.subdomain:
                        continue
                    domain = f"{ext.domain}.{ext.suffix}"
                    cleaned.add(domain.lower())
            else:
                # Skip non-.lt domains entirely
                continue

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in sorted(cleaned):
            f.write(domain + "\n")

    print(f"✅ Cleaned {len(cleaned)} unique .lt domains saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_domains()
