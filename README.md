# API Discovery Tool

A professional Python tool for extracting and analyzing API documentation from banking and financial services websites. Built specifically for PSD2 compliance and Open Banking initiatives.

## 🚀 Features

- **Automated Content Extraction**: Scrapes API documentation from websites using advanced web crawling
- **PDF Support**: Handles PDF documentation with optimized parameters and retry logic
- **OpenAPI Detection**: Automatically discovers and extracts OpenAPI/Swagger specifications
- **Recursive Crawling**: Intelligently follows relevant documentation links
- **Multi-format Output**: Supports JSON and YAML output formats
- **Organized Storage**: Hierarchical file organization by country/service-type/bank
- **Rate Limit Handling**: Built-in delays to respect API limits
- **PSD2 Optimized**: Specifically designed for banking API documentation

## 📋 Requirements

- Python 3.8+
- Firecrawl API key (get from [firecrawl.dev](https://firecrawl.dev))
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd api-discovery-tool
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your FIRECRAWL_API_KEY
   ```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
FIRECRAWL_API_KEY=your_api_key_here
```

## 📖 Usage

The tool supports multiple extraction modes depending on your needs. All commands follow the same basic structure but with different parameters for different scenarios.

### 🎯 Basic Usage - Single Page Extraction

Extract API documentation from a single URL without following links:

```bash
python extract_api.py "https://developer.bank.com/api-docs" \
  --country ro \
  --service-type aisp \
  --bank example_bank
```

**What happens:**
- ✅ Extracts content from the specified URL only
- ✅ Discovers OpenAPI/Swagger specifications if present
- ✅ Lists relevant links but doesn't follow them
- ✅ Fast execution (~30-60 seconds)
- ✅ Minimal API credit usage

**Best for:** Quick documentation overview, specific page analysis

### 🔄 Recursive Crawling - Complete Documentation Extraction

Automatically follows relevant links to build comprehensive documentation:

```bash
python extract_api.py "https://developer.bank.com" \
  --country de \
  --service-type pisp \
  --bank deutsche_bank \
  --recursive \
  --max-depth 2 \
  --format yaml \
  --verbose
```

**What happens:**
- ✅ Extracts main page content
- ✅ Intelligently identifies relevant API documentation links
- ✅ Follows up to 3 most relevant links per page
- ✅ Continues recursively up to specified depth
- ✅ Discovers OpenAPI specs across multiple pages
- ✅ 30-second delays between requests (rate limiting)

**Recursion Levels:**
- **Depth 1**: Main page + immediate child pages
- **Depth 2**: Main page + child pages + grandchild pages  
- **Depth 3**: Three levels deep (recommended maximum)

**Best for:** Complete documentation mapping, comprehensive analysis

### 📄 PDF Documentation - Automatic Optimization

The tool automatically detects PDF files and optimizes processing:

```bash
python extract_api.py "https://bank.com/api-guide.pdf" \
  --country nl \
  --service-type cbpii \
  --bank ing
```

**What happens:**
- ✅ Detects PDF format automatically (`url.endswith('.pdf')`)
- ✅ Uses extended timeout (2 minutes vs 30 seconds)
- ✅ Optimized wait time for PDF rendering
- ✅ Converts PDF content to markdown and HTML
- ✅ Automatic retry with reduced parameters if timeout
- ✅ Skips link crawling (not applicable to PDFs)

**Best for:** PDF documentation, user guides, technical specifications

### 🎛️ Advanced Configuration Examples

#### Multi-format Output with Verbose Logging
```bash
python extract_api.py "https://developer.commerzbank.com" \
  --country de \
  --service-type all \
  --bank commerzbank \
  --recursive \
  --max-depth 1 \
  --format yaml \
  --verbose
```

#### Custom Output Location
```bash
python extract_api.py "https://developers.brd.ro/psd2" \
  --country ro \
  --service-type aisp \
  --bank brd \
  --output "/custom/path/brd_documentation.json" \
  --verbose
```

#### Quick Scan Mode (Non-recursive)
```bash
python extract_api.py "https://developer.ing.com/openbanking" \
  --country nl \
  --service-type pisp \
  --bank ing
```

### 🚀 Command Execution Flow

1. **URL Analysis**: Detects content type (PDF vs web page)
2. **Parameter Optimization**: Adjusts timeouts and formats automatically  
3. **Content Extraction**: Scrapes main page with optimized settings
4. **Link Discovery**: Identifies relevant API documentation links
5. **Recursive Processing**: Follows links if `--recursive` enabled
6. **OpenAPI Detection**: Searches for API specifications
7. **Content Organization**: Saves in structured format
8. **Rate Limiting**: Respects API limits with automatic delays

## 📊 Command Line Options

| Option | Short | Description | Required | Default | Example |
|--------|-------|-------------|----------|---------|---------|
| `url` | - | URL of API documentation to extract | ✅ | - | `"https://developer.bank.com"` |
| `--country` | `-c` | Country code (ISO 3166-1 alpha-2) | ✅ | - | `ro`, `de`, `nl`, `fr`, `hu` |
| `--service-type` | `-s` | PSD2 service type | ✅ | - | `aisp`, `pisp`, `cbpii`, `all` |
| `--bank` | `-b` | Bank name/identifier (lowercase, underscore) | ✅ | - | `bnp_paribas`, `deutsche_bank` |
| `--output` | `-o` | Custom output file path | ❌ | auto-generated | `"/path/to/custom.json"` |
| `--format` | `-f` | Output format | ❌ | `json` | `json`, `yaml` |
| `--recursive` | `-r` | Enable recursive link crawling | ❌ | `false` | - |
| `--max-depth` | `-d` | Maximum recursion depth (1-5) | ❌ | `3` | `1`, `2`, `3` |
| `--verbose` | `-v` | Enable detailed logging | ❌ | `false` | - |

### 📋 Parameter Details

#### Service Types (`--service-type`)
- **`aisp`**: Account Information Service Provider - access to account data
- **`pisp`**: Payment Initiation Service Provider - payment processing
- **`cbpii`**: Card Based Payment Instrument Issuer - card payment confirmation
- **`all`**: All service types (use when documentation covers multiple services)

#### Country Codes (`--country`)
Common European banking markets:
- **`ro`**: Romania (BRD, BCR, Raiffeisen)
- **`de`**: Germany (Deutsche Bank, Commerzbank)
- **`nl`**: Netherlands (ING, ABN AMRO, KBC)
- **`fr`**: France (BNP Paribas, Société Générale)
- **`hu`**: Hungary (OTP Bank, K&H Bank)
- **`it`**: Italy (UniCredit, Intesa Sanpaolo)
- **`es`**: Spain (Santander, BBVA)

#### Recursion Depth (`--max-depth`)
- **`1`**: Main page + immediate child pages (recommended for quick scans)
- **`2`**: Two levels deep (balanced approach)
- **`3`**: Three levels deep (comprehensive, default)
- **`4-5`**: Very deep crawling (use with caution, high API usage)

## 📁 Output Structure

The tool organizes extracted content in a hierarchical structure:

```
outputs/
├── ro/
│   ├── aisp/
│   │   └── brd/
│   │       └── raw_content_20240125_143022.json
│   └── pisp/
│       └── bcr/
│           └── raw_content_20240125_143055.json
├── de/
│   └── aisp/
│       └── deutsche_bank/
│           └── raw_content_20240125_143128.json
└── nl/
    └── cbpii/
        └── ing/
            └── raw_content_20240125_143201.json
```

## 📄 Output Format

Each extracted file contains:

```json
{
  "url": "https://developer.bank.com/api-docs",
  "content": {
    "markdown": "# API Documentation\n...",
    "html": "<html>...</html>",
    "screenshot": "base64_image_data"
  },
  "links": [
    "https://developer.bank.com/authentication",
    "https://developer.bank.com/endpoints"
  ],
  "openapi_specs": [
    {
      "url": "https://developer.bank.com/openapi.json",
      "content": {
        "markdown": "openapi: 3.0.0\n...",
        "html": "<html>...</html>"
      }
    }
  ],
  "child_pages": [
    {
      "url": "https://developer.bank.com/authentication",
      "content": {...},
      "links": [...],
      "child_pages": []
    }
  ]
}
```

## 🏦 Supported Banks & Services

The tool has been tested with major European banks including:

- **Romania**: BRD, BCR, Raiffeisen
- **Germany**: Deutsche Bank, Commerzbank
- **Netherlands**: ING, ABN AMRO, KBC
- **France**: BNP Paribas, Société Générale
- **Hungary**: OTP Bank, K&H Bank

### Service Types

- **AISP** (Account Information Service Provider)
- **PISP** (Payment Initiation Service Provider)  
- **CBPII** (Card Based Payment Instrument Issuer)
- **ALL** (All service types)

## 🔍 Examples

### Example 1: Romanian Bank AISP

```bash
python extract_api.py "https://developers.brd.ro/psd2" \
  --country ro \
  --service-type aisp \
  --bank brd \
  --verbose
```

### Example 2: German Bank with Recursive Crawling

```bash
python extract_api.py "https://developer.commerzbank.com" \
  --country de \
  --service-type pisp \
  --bank commerzbank \
  --recursive \
  --max-depth 3 \
  --format yaml
```

### Example 3: PDF Documentation

```bash
python extract_api.py "https://developer.ing.com/api-guide.pdf" \
  --country nl \
  --service-type cbpii \
  --bank ing
```


## 📈 Performance

- **Processing Speed**: ~30-60 seconds per page (depending on content)
- **Rate Limits**: Respects Firecrawl's 30-second rate limit
- **Memory Usage**: Optimized for large documentation sites
- **Concurrent Processing**: Sequential processing to avoid rate limits

## 🔒 Security

- **API Key Protection**: Environment variable configuration
- **URL Validation**: Input sanitization and validation
- **Safe File Handling**: Secure file operations
- **No Sensitive Data Storage**: Only public documentation is extracted


