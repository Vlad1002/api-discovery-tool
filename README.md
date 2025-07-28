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

### Basic Usage

Extract API documentation from a single URL:

```bash
python extract_api.py "https://developer.bank.com/api-docs" \
  --country ro \
  --service-type aisp \
  --bank example_bank
```

### Advanced Usage

Recursive crawling with custom depth:

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

### PDF Documentation

The tool automatically detects and optimizes for PDF files:

```bash
python extract_api.py "https://bank.com/api-guide.pdf" \
  --country nl \
  --service-type cbpii \
  --bank ing
```

## 📊 Command Line Options

| Option | Short | Description | Required | Default |
|--------|-------|-------------|----------|---------|
| `url` | - | URL of API documentation to extract | ✅ | - |
| `--country` | `-c` | Country code (e.g., ro, de, fr) | ✅ | - |
| `--service-type` | `-s` | Service type: aisp, pisp, cbpii, all | ✅ | - |
| `--bank` | `-b` | Bank name/identifier | ✅ | - |
| `--output` | `-o` | Custom output file path | ❌ | auto-generated |
| `--format` | `-f` | Output format: json, yaml | ❌ | json |
| `--recursive` | `-r` | Enable recursive crawling | ❌ | false |
| `--max-depth` | `-d` | Maximum crawl depth | ❌ | 3 |
| `--verbose` | `-v` | Enable verbose output | ❌ | false |

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

## 🚨 Error Handling

The tool includes comprehensive error handling for:

- **Network timeouts**: Automatic retry with reduced parameters
- **Rate limiting**: Built-in delays between requests
- **Invalid URLs**: Graceful error messages
- **PDF processing**: Optimized parameters and fallback options
- **Missing API keys**: Clear setup instructions

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

## 🐛 Troubleshooting

### Common Issues

1. **"FIRECRAWL_API_KEY not found"**
   - Ensure `.env` file exists with valid API key
   - Check environment variable is loaded correctly

2. **"Payment Required" error**
   - API key has exceeded free tier limits
   - Wait for rate limit reset or upgrade plan

3. **PDF timeout errors**
   - Tool automatically retries with reduced parameters
   - Large PDFs may require multiple attempts

4. **No content extracted**
   - Check if URL is accessible
   - Verify the site doesn't block automated access
   - Try with `--verbose` flag for detailed logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Vlad** - *Initial work and development*

## 🙏 Acknowledgments

- [Firecrawl](https://firecrawl.dev) for the web scraping API
- European Banking Authority for PSD2 guidelines
- Berlin Group for Open Banking standards

---

**Note**: This tool is designed for extracting publicly available API documentation. Always respect robots.txt and terms of service of target websites. 