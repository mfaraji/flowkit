# Personal Utility Tools SDK

A comprehensive Python SDK containing various utility tools for personal productivity and automation.

## Features

- **File Operations**: File manipulation, organization, and batch processing
- **Text Processing**: String utilities, text analysis, and formatting tools
- **Data Utilities**: Data validation, conversion, and manipulation helpers
- **System Tools**: System information, process management, and automation
- **Network Utilities**: HTTP helpers, API clients, and network diagnostics
- **Time & Date**: Date/time manipulation and scheduling utilities
- **Crypto & Security**: Encryption, hashing, and security utilities
- **Configuration**: Settings management and configuration helpers

## Installation

```bash
pip install personal-utils-sdk
```

## Quick Start

```python
from personal_utils import FileUtils, TextUtils, DateUtils

# File operations
FileUtils.organize_downloads()

# Text processing
cleaned_text = TextUtils.clean_whitespace("  messy   text  ")

# Date utilities
formatted_date = DateUtils.format_timestamp()
```

## Documentation

See the [docs](./docs/) directory for detailed documentation and examples.

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](./LICENSE) for details. 