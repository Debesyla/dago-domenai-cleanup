# Copilot Instructions - Domain Cleaner

## Project Overview
This is a lightweight Python utility for preprocessing .lt (Lithuanian) domain data. It transforms raw domain/URL lists into clean, deduplicated domains suitable for detailed domain analysis.

**Core Flow**: `assets/input.txt` → domain cleaning logic → `assets/output.txt` (one domain per line)

## Architecture & Key Components

### Single-Purpose Script Design
- **`src/domain_cleaner.py`**: Main logic using `tldextract` library
- **Data Flow**: Read raw domains → extract root domains → filter subdomains → deduplicate → output sorted list
- **No database**: Simple file-to-file transformation

### Critical Domain Processing Logic
```python
# Key pattern: Extract domains, with special handling for .lt government domains
ext = tldextract.extract(raw)
domain = f"{ext.domain}.{ext.suffix}"

# Government/institutional domains - preserve subdomains
if ext.suffix in ['lrv.lt', 'edu.lt', 'mil.lt', 'gov.lt']:  # Add other govt TLDs as needed
    if ext.subdomain:
        domain = f"{ext.subdomain}.{domain}"
# All other domains - strip subdomains (blog.example.lt → example.lt)
elif ext.subdomain:
    continue  # Skip, use root domain only
```

### File Structure Convention
- **`assets/input.txt`**: Raw .lt domains/URLs (one per line, any format)
- **`assets/output.txt`**: Clean domains (gitignored, generated, one per line)
- **`docs/DOMAIN-CLEANER.md`**: Complete usage documentation

### Performance Characteristics
- **Memory efficient**: Uses `set()` for deduplication, processes line-by-line
- **Speed**: Handles thousands of domains in seconds with `tldextract` caching
- **Output ready**: Sorted one-domain-per-line format for bulk domain checkers

## Development Workflows

### Running the Tool
```bash
# Primary method
python3 src/domain_cleaner.py

# Alternative via convenience script
./run.sh
```

### Testing with Sample Data
The `assets/input.txt` shows expected .lt domain input format:
```
debesyla.lt
debes.debesyla.lt  # Will be filtered out (non-govt subdomain)
alfa.lt
lrs.lrv.lt  # Will be kept (government subdomain)
```

### Dependencies
- **Single dependency**: `tldextract>=5.1.2` for robust domain parsing
- **Install**: `pip install -r requirements.txt`

## Project-Specific Patterns

### Error Handling Philosophy
- **Graceful skipping**: Invalid domains are ignored, not errored
- **Minimal validation**: Trust `tldextract` to handle edge cases
- **Simple feedback**: Print count of processed domains

### Data Conventions
- **Case normalization**: All output domains are lowercase
- **Sorting**: Output is alphabetically sorted for consistency
- **Encoding**: UTF-8 for international domains

### Git Workflow
- **Track**: Source code, requirements, documentation, sample input
- **Ignore**: Generated output files (`assets/output.txt`)
- **Clean state**: Output directory structure exists but files are generated

## Integration Points

### Input Expectations
- One .lt domain/URL per line in `assets/input.txt`
- Handles full URLs: `https://blog.example.lt/path` → `example.lt`
- Preserves government subdomains: `subdomain.lrv.lt` → `subdomain.lrv.lt`
- Skips empty lines and malformed entries silently

### Output Format
- Plain text, one domain per line (exactly as needed for detailed domain checker)
- Ready for bulk processing tools (WHOIS, DNS checkers)
- Designed as "first pipeline step" for domain intelligence workflows

## Future Extension Points
The documentation in `docs/DOMAIN-CLEANER.md` outlines planned enhancements:
- CLI argument support (`--input`, `--output`)
- Domain filtering options (TLD whitelist/blacklist)
- Progress logging for large datasets
- Integration hooks for downstream analysis tools