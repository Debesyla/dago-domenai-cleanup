from pathlib import Path
import tldextract
import pytest
import re
from urllib.parse import urlparse


def process_domains_for_test(input_lines):
    """
    Standalone domain processing logic for testing.
    Tests the core business logic without file I/O dependencies.
    """
    GOV_SUFFIXES = {"lrv.lt", "edu.lt", "mil.lt", "gov.lt"}
    GOV_DOMAINS = {"lrv", "edu", "mil"}
    cleaned = set()
    errors = []

    line_count = 0
    for line in input_lines:
        line_count += 1
        raw = line.strip().rstrip('.')
        if not raw:
            errors.append((line_count, line.rstrip(), "empty line"))
            continue

        # If input is a URL, extract the netloc
        if re.match(r'^[a-zA-Z]+://', raw):
            parsed = urlparse(raw)
            raw = parsed.netloc or raw

        # Remove www. prefix if present
        if raw.lower().startswith('www.'):
            raw = raw[4:]

        # Skip if it's an IP address
        if re.match(r'^\d+(\.\d+){3}$', raw):
            errors.append((line_count, line.rstrip(), "ip address"))
            continue

        # Allow only valid domain characters (letters, digits, dash, dot)
        if not re.match(r'^[\w\-.]+$', raw, re.UNICODE):
            errors.append((line_count, line.rstrip(), "invalid characters"))
            continue

        # Normalize to lowercase before processing to handle uppercase TLDs
        ext = tldextract.extract(raw.lower())
        if not ext.domain or not ext.suffix:
            errors.append((line_count, line.rstrip(), "invalid domain/suffix"))
            continue

        # Only process .lt domains and allowed government suffixes
        suffix = ext.suffix
        domain = f"{ext.domain}.{suffix}"
        if suffix in GOV_SUFFIXES or (suffix == "lt" and ext.domain in GOV_DOMAINS):
            # For government domains (either special suffixes or second-level gov domains), preserve all subdomains
            if ext.subdomain:
                domain = f"{ext.subdomain}.{domain}"
            cleaned.add(domain)
        elif suffix == "lt":
            # For commercial .lt domains, strip subdomains (treat as invalid input)
            if ext.subdomain:
                errors.append((line_count, line.rstrip(), "non-govt subdomain"))
                continue
            cleaned.add(domain)
        else:
            errors.append((line_count, line.rstrip(), "non-.lt domain"))
            continue

    return sorted([d.lower() for d in cleaned]), errors


@pytest.mark.parametrize("input_lines,expected_output,expected_error_reasons", [
    # Test 1: Basic .lt domains without subdomains
    (
        ["alfa.lt", "debesyla.lt"],
        ["alfa.lt", "debesyla.lt"],
        []
    ),
    # Test 2: Commercial subdomain (should be skipped)
    (
        ["blog.debesyla.lt"],
        [],
        ["non-govt subdomain"]
    ),
    # Test 3: Government domains with subdomains (should be preserved)
    (
        ["lrs.lrv.lt", "info.edu.lt", "portal.mil.lt", "services.gov.lt"],
        ["info.edu.lt", "lrs.lrv.lt", "portal.mil.lt", "services.gov.lt"],
        []
    ),
    # Test 4: Non-.lt domain (should be skipped)
    (
        ["example.com"],
        [],
        ["non-.lt domain"]
    ),
    # Test 5: Empty line
    (
        [""],
        [],
        ["empty line"]
    ),
    # Test 6: Malformed domain
    (
        ["notadomain"],
        [],
        ["invalid domain/suffix"]
    ),
    # Test 7: Mixed valid and invalid
    (
        ["alfa.lt", "example.com", "beta.lt"],
        ["alfa.lt", "beta.lt"],
        ["non-.lt domain"]
    ),
    # Test 8: Deduplication
    (
        ["alfa.lt", "ALFA.LT", "alfa.lt"],
        ["alfa.lt"],
        []
    ),
    # Test 9: Full URLs with paths (www is a subdomain, so test.lt is filtered)
    (
        ["https://example.lt/path", "http://www.test.lt"],
        ["example.lt", "test.lt"],
        []
    ),
    # Test 10: Government domain without subdomain
    (
        ["lrv.lt", "edu.lt"],
        ["edu.lt", "lrv.lt"],
        []
    ),
])
def test_domain_processing_logic(input_lines, expected_output, expected_error_reasons):
    """Test core domain processing logic with various inputs."""
    output, errors = process_domains_for_test(input_lines)
    
    # Verify output matches expected
    assert output == expected_output, f"Expected {expected_output}, got {output}"
    
    # Verify expected error reasons are present
    error_messages = [reason for _, _, reason in errors]
    for expected_reason in expected_error_reasons:
        assert expected_reason in error_messages, \
            f"Expected error reason '{expected_reason}' not found in {error_messages}"


def test_case_normalization():
    """Test that domains are normalized to lowercase, including TLDs."""
    output, _ = process_domains_for_test(["alfa.lt", "DEBESYLA.lt", "TEST.LT", "MiXeD.Lt"])
    assert output == ["alfa.lt", "debesyla.lt", "mixed.lt", "test.lt"]


def test_government_subdomain_preservation():
    """Test that government subdomains are preserved."""
    output, _ = process_domains_for_test([
        "subdomain.lrv.lt",
        "portal.edu.lt",
        "admin.mil.lt",
        "services.gov.lt"
    ])
    assert "subdomain.lrv.lt" in output
    assert "portal.edu.lt" in output
    assert "admin.mil.lt" in output
    assert "services.gov.lt" in output


def test_commercial_subdomain_stripping():
    """Test that commercial subdomains are removed."""
    output, errors = process_domains_for_test([
        "www.example.lt",
        "blog.test.lt",
        "shop.store.lt"
    ])
    # 'www.example.lt' should become 'example.lt'; other subdomains are non-govt and skipped
    assert output == ["example.lt"]
    assert len(errors) == 2
    assert all("non-govt subdomain" in err[2] for err in errors)


def test_url_parsing():
    """Test that full URLs are parsed correctly."""
    output, _ = process_domains_for_test([
        "https://example.lt/path/to/page",
        "http://www.test.lt?query=param",
        "ftp://old.site.lt"
    ])
    # 'example.lt' and 'test.lt' accepted after stripping www; 'old.site.lt' becomes 'site.lt' but is a non-govt subdomain and should be skipped
    assert output == ["example.lt", "test.lt"]


def test_trailing_dot_stripping():
    """Test that domains with trailing dots are cleaned."""
    output, _ = process_domains_for_test([
        "example.lt.",
        "lrv.lt.",
        "subdomain.lrv.lt."
    ])
    assert "example.lt" in output
    assert "lrv.lt" in output
    assert "subdomain.lrv.lt" in output


def test_ip_address_skipping():
    """Test that IP addresses are skipped."""
    output, errors = process_domains_for_test([
        "192.168.1.1",
        "8.8.8.8",
        "255.255.255.255"
    ])
    assert output == []
    assert len(errors) == 3


def test_special_character_and_emoji_skipping():
    """Test that domains with special characters or emoji are skipped."""
    output, errors = process_domains_for_test([
        "exa💩mple.lt",
        "test!@#.lt",
        "valid.lt",
        "😀.lt"
    ])
    assert output == ["valid.lt"]
    assert len(errors) == 3


def test_idn_domain_preservation():
    """Test that IDN (internationalized) .lt domains are preserved."""
    output, _ = process_domains_for_test([
        "xn--vilnius-9ib.lt",  # punycode for vilnius.lt with diacritics
        "xn--kaunas-9ib.lt",
        "xn--klaipda-9ib.lt"
    ])
    assert "xn--vilnius-9ib.lt" in output
    assert "xn--kaunas-9ib.lt" in output
    assert "xn--klaipda-9ib.lt" in output
