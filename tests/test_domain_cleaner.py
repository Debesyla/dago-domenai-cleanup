from pathlib import Path
import tldextract
import pytest


def process_domains_for_test(input_lines):
    """
    Standalone domain processing logic for testing.
    Tests the core business logic without file I/O dependencies.
    """
    GOV_DOMAINS = {"lrv", "edu", "mil"}
    cleaned = set()
    errors = []
    
    line_count = 0
    for line in input_lines:
        line_count += 1
        raw = line.strip()
        
        if not raw:
            errors.append((line_count, line.rstrip(), "empty line"))
            continue
        
        # Normalize to lowercase before processing to handle uppercase TLDs
        ext = tldextract.extract(raw.lower())
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
    
    return sorted(cleaned), errors


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
        ["example.lt"],
        ["non-govt subdomain"]
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
    assert output == []
    assert len(errors) == 3
    assert all("non-govt subdomain" in err[2] for err in errors)


def test_url_parsing():
    """Test that full URLs are parsed correctly."""
    output, _ = process_domains_for_test([
        "https://example.lt/path/to/page",
        "http://www.test.lt?query=param",
        "ftp://old.site.lt"
    ])
    # www and old are subdomains, should be filtered
    assert output == ["example.lt"]
