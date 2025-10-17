
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
    errors = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        line_count = 0
        for line in f:
            line_count += 1
            if line_count % 1000 == 0:
                print(f"...processed {line_count} lines...")

            raw = line.strip()
            if not raw:
                errors.append((line_count, line.rstrip(), "empty line"))
                continue

            ext = tldextract.extract(raw)
            if not ext.domain or not ext.suffix:
                errors.append((line_count, line.rstrip(), "invalid domain/suffix"))
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
                        errors.append((line_count, line.rstrip(), "non-govt subdomain"))
                        continue
                    domain = f"{ext.domain}.{ext.suffix}"
                    cleaned.add(domain.lower())
            else:
                # Skip non-.lt domains entirely
                errors.append((line_count, line.rstrip(), "non-.lt domain"))
                continue


    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for domain in sorted(cleaned):
            f.write(domain + "\n")

    # Write errors to assets/errors.txt
    errors_file = Path("assets/errors.txt")
    with open(errors_file, "w", encoding="utf-8") as ef:
        for line_num, line_val, reason in errors:
            ef.write(f"Line {line_num}: {reason} | {line_val}\n")

    print(f"✅ Cleaned {len(cleaned)} unique .lt domains saved to {OUTPUT_FILE}")
    print(f"⚠️ {len(errors)} lines skipped. See {errors_file} for details.")

if __name__ == "__main__":
    clean_domains()
