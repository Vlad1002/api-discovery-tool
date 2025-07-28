#!/usr/bin/env python3
"""
API Documentation Extractor

This script extracts raw content from API documentation websites using Firecrawl.
It can crawl recursively through related pages and save the content in structured formats.
"""

import os
import json
import yaml
import argparse
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
from dotenv import load_dotenv

try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("Error: firecrawl-py package not found. Please install it with: pip install firecrawl-py")
    exit(1)

# Load environment variables
load_dotenv()

def test_firecrawl_connection():
    """Test connection to Firecrawl API."""
    try:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            print("❌ FIRECRAWL_API_KEY not found in environment variables")
            return False

        app = FirecrawlApp(api_key=api_key)
        
        # Test with a simple URL
        test_url = "https://httpbin.org/json"
        print(f"[*] Testing connection with: {test_url}")
        
        response = app.scrape_url(test_url, formats=["markdown"])
        
        if response:
            print("✅ Connection to Firecrawl successful!")
            return True
        else:
            print("❌ Unexpected response from Firecrawl")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Firecrawl: {e}")
        return False

def clean_url(url: str) -> str:
    """Clean and normalize URL."""
    # Remove markdown link syntax
    url = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\2', url)
    
    # Remove fragments and clean parameters
    parsed = urlparse(url)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Remove trailing slash if present
    if clean_url.endswith('/') and len(clean_url) > 8:
        clean_url = clean_url[:-1]
    
    return clean_url

def is_api_related_link(url: str, base_url: str) -> bool:
    """Check if a link is related to API documentation."""
    # Must be from the same domain
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    
    if base_domain not in url_domain and url_domain not in base_domain:
        return False
    
    url_lower = url.lower()
    
    # Positive keywords
    api_keywords = [
        'api', 'endpoint', 'swagger', 'openapi', 'spec', 'docs', 'documentation',
        'reference', 'guide', 'tutorial', 'integration', 'developer', 'dev',
        'rest', 'graphql', 'webhook', 'auth', 'authentication', 'oauth',
        'sandbox', 'postman', 'curl', 'json', 'xml', 'response', 'request',
        'psd2', 'aisp', 'pisp', 'cbpii', 'berlin-group', 'stet', 'open-banking'
    ]
    
    # Negative keywords to exclude
    negative_keywords = [
        'login', 'logout', 'register', 'signup', 'signin', 'privacy', 'terms',
        'cookie', 'gdpr', 'legal', 'contact', 'about', 'news', 'blog',
        'career', 'job', 'press', 'media', 'investor', 'support-ticket',
        'forum', 'community', 'social', 'facebook', 'twitter', 'linkedin'
    ]
    
    # Check for negative keywords first
    for keyword in negative_keywords:
        if keyword in url_lower:
            return False
    
    # Check for positive keywords
    for keyword in api_keywords:
        if keyword in url_lower:
            return True
    
    return False

def try_common_openapi_endpoints(base_url: str, app) -> list:
    """Try to access common OpenAPI specification endpoints."""
    common_paths = [
        '/openapi.json', '/openapi.yaml', '/openapi.yml',
        '/swagger.json', '/swagger.yaml', '/swagger.yml',
        '/api-docs', '/api-docs.json', '/api-docs.yaml',
        '/v1/openapi.json', '/v2/openapi.json', '/v3/openapi.json',
        '/docs/openapi.json', '/documentation/openapi.json'
    ]
    
    specs = []
    for path in common_paths:
        try:
            spec_url = base_url + path
            print(f"[*] Trying common endpoint: {spec_url}")
            
            spec_data = app.scrape_url(
                url=spec_url,
                formats=["markdown", "html"]
            )
            
            if spec_data and (getattr(spec_data, 'markdown', None) or getattr(spec_data, 'html', None)):
                specs.append({
                    'url': spec_url,
                    'content': {
                        'markdown': getattr(spec_data, 'markdown', None),
                        'html': getattr(spec_data, 'html', None)
                    }
                })
                print(f"[+] Found OpenAPI spec at: {spec_url}")
                
        except Exception as e:
            print(f"[!] Error accessing {spec_url}: {e}")
            continue
    
    return specs

def extract_site_content(url: str, depth: int = 0, max_depth: int = 1, visited_urls: set = None) -> dict:
    """
    Extract content from a website, including relevant child pages.
    Tries multiple formats to capture JavaScript content as well.
    Includes improved support for PDFs.
    """
    if visited_urls is None:
        visited_urls = set()

    if depth > max_depth or url in visited_urls:
        return {}

    visited_urls.add(url)
    print(f"\n[*] Initializing extraction from: {url} (depth: {depth})")

    try:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables.")

        app = FirecrawlApp(api_key=api_key)

        # Delay between requests to avoid rate limiting
        if depth > 0:  # Don't wait for the first page
            wait_time = 31  # Firecrawl has a 30-second limit
            print(f"\n[*] Waiting {wait_time} seconds to avoid rate limiting...")
            for i in range(wait_time, 0, -1):
                print(f"\r[*] Waiting {i} more seconds...", end="", flush=True)
                time.sleep(1)
            print("\n")

        print("[*] Making request to Firecrawl...")
        
        # Detect if URL is a PDF
        is_pdf = url.lower().endswith('.pdf')
        
        # Configure parameters based on content type
        if is_pdf:
            print("[*] PDF detected - using optimized parameters...")
            scraped_data = app.scrape_url(
                url=url,
                formats=["markdown", "html"],
                timeout=120000,  # 2 minute timeout for PDFs
                wait_for=5000    # Wait 5 seconds for loading
            )
        else:
            # Try multiple formats to capture JavaScript content
            scraped_data = app.scrape_url(
                url=url,
                formats=["markdown", "links", "html", "screenshot"],
                wait_for=2000,  # Wait 2 seconds for JavaScript to load
                timeout=30000   # 30 second timeout
            )
        
        if not scraped_data:
            raise ValueError("No response received from Firecrawl")

        # Extract base_url for checks
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))

        # Initialize results dictionary
        results = {
            'url': url,
            'content': {
                'markdown': getattr(scraped_data, 'markdown', None),
                'html': getattr(scraped_data, 'html', None),
                'screenshot': getattr(scraped_data, 'screenshot', None) if not is_pdf else None
            },
            'links': [],
            'child_pages': []
        }

        # For PDFs, don't search for OpenAPI specs or links
        if is_pdf:
            print("[+] PDF processed successfully!")
            return results

        # Try to find and directly access OpenAPI specification
        openapi_urls = []
        if hasattr(scraped_data, 'html') and scraped_data.html:
            # Search for OpenAPI specification links in HTML
            openapi_patterns = [
                r'href=["\']([^"\']*openapi[^"\']*\.(?:json|yaml|yml))["\']',
                r'href=["\']([^"\']*swagger[^"\']*\.(?:json|yaml|yml))["\']',
                r'href=["\']([^"\']*spec[^"\']*\.(?:json|yaml|yml))["\']',
                r'href=["\']([^"\']*api[^"\']*\.(?:json|yaml|yml))["\']'
            ]
            
            for pattern in openapi_patterns:
                matches = re.findall(pattern, scraped_data.html, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/'):
                        openapi_url = urljoin(base_url, match)
                    elif match.startswith(('http://', 'https://')):
                        openapi_url = match
                    else:
                        continue
                    openapi_urls.append(openapi_url)

        # Try to access found OpenAPI specifications
        if openapi_urls:
            print(f"[*] Found {len(openapi_urls)} possible OpenAPI specifications...")
            for openapi_url in openapi_urls[:3]:  # Limit to first 3
                try:
                    print(f"[*] Trying to access specification: {openapi_url}")
                    time.sleep(2)  # Short delay
                    
                    spec_data = app.scrape_url(
                        url=openapi_url,
                        formats=["markdown", "html"]
                    )
                    
                    if spec_data and (getattr(spec_data, 'markdown', None) or getattr(spec_data, 'html', None)):
                        results['openapi_specs'] = results.get('openapi_specs', [])
                        results['openapi_specs'].append({
                            'url': openapi_url,
                            'content': {
                                'markdown': getattr(spec_data, 'markdown', None),
                                'html': getattr(spec_data, 'html', None)
                            }
                        })
                        print(f"[+] OpenAPI specification extracted successfully!")
                    
                except Exception as e:
                    print(f"[!] Error accessing specification {openapi_url}: {e}")
        
        # If no specs found in HTML, try common endpoints
        if not openapi_urls and depth == 0:  # Only for main page
            common_specs = try_common_openapi_endpoints(base_url, app)
            if common_specs:
                results['openapi_specs'] = results.get('openapi_specs', [])
                results['openapi_specs'].extend(common_specs)

        # Process links to find relevant pages
        if hasattr(scraped_data, 'links') and scraped_data.links:
            print(f"\n[*] Analyzing {len(scraped_data.links)} found links...")
            api_related_links = []
            
            for link in scraped_data.links:
                # Build full URL for relative links
                if link.startswith('/'):
                    full_url = urljoin(base_url, link)
                elif link.startswith(('http://', 'https://')):
                    full_url = link
                else:
                    continue
                
                # Clean URL
                full_url = clean_url(full_url)
                
                # Check if link seems relevant
                if is_api_related_link(full_url, base_url):
                    api_related_links.append(full_url)
            
            # Remove duplicates and sort
            api_related_links = list(set(api_related_links))
            results['links'] = api_related_links
            
            # Recursively explore relevant pages (limited to first 3)
            if depth < max_depth and api_related_links:
                relevant_links = [link for link in api_related_links if link != url][:3]
                
                if relevant_links:
                    print(f"[*] Exploring {len(relevant_links)} relevant pages found...")
                    
                    for i, child_url in enumerate(relevant_links, 1):
                        print(f"\n[*] Exploring page {i}/{len(relevant_links)}: {child_url}")
                        child_content = extract_site_content(child_url, depth + 1, max_depth, visited_urls)
                        
                        if child_content:
                            results['child_pages'].append(child_content)

        return results

    except Exception as e:
        print(f"[!] Error extracting content from {url}: {e}")
        
        # If it's a PDF and we have timeout, try again with reduced parameters
        if url.lower().endswith('.pdf') and ('timeout' in str(e).lower() or 'internal server error' in str(e).lower()):
            print("[*] Trying again with reduced parameters for PDF...")
            try:
                time.sleep(5)  # Wait a bit
                retry_data = app.scrape_url(
                    url=url,
                    formats=["markdown"],
                    timeout=60000,  # 1 minute timeout
                    wait_for=1000   # 1 second wait
                )
                
                if retry_data:
                    print("[+] PDF processed successfully on second attempt!")
                    return {
                        'url': url,
                        'content': {
                            'markdown': getattr(retry_data, 'markdown', None),
                            'html': getattr(retry_data, 'html', None),
                            'screenshot': None
                        },
                        'links': [],
                        'child_pages': []
                    }
            except Exception as retry_e:
                print(f"[!] Failed on second attempt too: {retry_e}")
        
        return {}

def generate_output_filename(country: str, service_type: str, bank: str, format_type: str) -> str:
    """Generate output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directory structure
    output_dir = os.path.join("outputs", country, service_type, bank)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    filename = f"raw_content_{timestamp}.{format_type}"
    return os.path.join(output_dir, filename)

def save_output(data: dict, filename: str, format_type: str):
    """Save extracted data to file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if format_type == 'json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format_type == 'yaml':
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"[+] Content saved to '{filename}'")
        
    except Exception as e:
        print(f"[!] Error saving file: {e}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract raw content from API documentation websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_api.py "https://developer.example.com" --country ro --service-type aisp --bank example
  python extract_api.py "https://api.docs.com" --country de --service-type pisp --bank testbank --recursive --max-depth 2
        """
    )
    
    parser.add_argument('url', help='URL of the API documentation to extract')
    parser.add_argument('--country', '-c', required=True, help='Country code (e.g., ro, de, fr)')
    parser.add_argument('--service-type', '-s', required=True, 
                       choices=['aisp', 'pisp', 'cbpii', 'all'],
                       help='Service type: aisp, pisp, cbpii, or all')
    parser.add_argument('--bank', '-b', required=True, help='Bank name/identifier')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--format', '-f', choices=['json', 'yaml'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Crawl related pages recursively')
    parser.add_argument('--max-depth', '-d', type=int, default=3,
                       help='Maximum crawl depth (default: 3)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_arguments()
    
    print("🚀 API Documentation Extractor")
    print("=" * 60)
    
    if args.verbose:
        print(f"\n[*] Configuration:")
        print(f"- URL: {args.url}")
        print(f"- Country: {args.country}")
        print(f"- Service: {args.service_type}")
        print(f"- Bank: {args.bank}")
        print(f"- Format: {args.format}")
        print(f"- Recursive: {args.recursive}")
        print(f"- Max depth: {args.max_depth}")
    
    # Test connection first
    if not test_firecrawl_connection():
        print("\n❌ Cannot connect to Firecrawl. Please check your API key.")
        return
    
    # Extract content
    max_depth = args.max_depth if args.recursive else 0
    extracted_data = extract_site_content(args.url, max_depth=max_depth)
    
    if not extracted_data:
        print("\n❌ No content could be extracted.")
        return
    
    print("\n✅ Extraction complete!")
    
    # Generate output filename
    if args.output:
        output_file = args.output
    else:
        output_file = generate_output_filename(
            args.country, 
            args.service_type, 
            args.bank, 
            args.format
        )
    
    # Save results
    save_output(extracted_data, output_file, args.format)
    
    # Summary
    print(f"\n[*] Extraction summary:")
    print(f"- Main URL: {extracted_data.get('url', 'N/A')}")
    print(f"- Links found: {len(extracted_data.get('links', []))}")
    print(f"- Child pages explored: {len(extracted_data.get('child_pages', []))}")
    
    if 'openapi_specs' in extracted_data:
        print(f"- OpenAPI specifications found: {len(extracted_data['openapi_specs'])}")

if __name__ == "__main__":
    main()