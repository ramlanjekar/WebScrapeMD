# Documentation Web Crawler

A fast, asynchronous web crawler specifically designed for documentation websites. The crawler can extract content while preserving code blocks and formatting, generating a single combined Markdown file.

## Features

- 🚀 Asynchronous crawling for better performance
- 💾 Memory usage monitoring
- ⏱️ Execution time tracking
- 📘 Automatic Table of Contents generation
- 🔗 Smart URL extraction and processing
- 🎨 Code block preservation
- 📊 Detailed crawling statistics

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc_agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the crawler:
```bash
python crawl4AI_fast.py
```

2. When prompted, enter the documentation website URL you want to crawl.

3. The crawler will:
   - Extract all relevant documentation links
   - Crawl each page asynchronously
   - Generate a combined Markdown file in the `output` directory
   - Show progress, memory usage, and timing information

## Configuration

Key parameters that can be adjusted in `crawl4AI_fast.py`:

- `max_concurrent`: Number of concurrent crawling tasks (default: 10)
- `CrawlerRunConfig`: Content filtering eg: prettify , excluded_selector etc.
- `BrowserConfig`: Configs the browser enviroment

## Output

The crawler generates a combined Markdown file in the `output` directory with:
- Automatic table of contents
- Preserved code blocks and formatting
- Source URL references
- Clear content separation
- Links of the content(you can remove it if you want)

## Performance Metrics

The crawler provides:
- Memory usage tracking
- Total execution time
- Per-batch timing
- Success/failure statistics

## Project Structure

```
doc_agent/
├── crawl4AI_fast.py        # Main crawler implementation
├── anchorl_url_generator.py # URL extraction utilities
├── output/                 # Generated documentation
└── README.md              # This file
```

## Limitations

- Requires proper permissions to access documentation sites
- Some JavaScript-heavy sites might not render completely
- Rate limiting might be required for some websites

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
