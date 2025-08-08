# PyxTxt

[![PyPI version](https://img.shields.io/pypi/v/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyxtxt.svg)](https://pypi.org/project/pyxtxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PyxTxt** is a simple and powerful Python library to extract text from various file formats.  
It supports PDF, DOCX, XLSX, PPTX, ODT, HTML, XML, TXT, legacy Office files, and more.

**NEW in v0.1.24+**: Enhanced support for web content, byte streams, and requests integration!

---

## ✨ Features

- **Multiple input types**: File paths, `io.BytesIO` buffers, raw `bytes` objects, and `requests.Response` objects
- **Wide format support**: PDF, DOCX, PPTX, XLSX, ODT, HTML, XML, TXT, legacy Office files (.xls, .ppt, .doc)
- **Automatic MIME detection**: Uses `python-magic` for intelligent file type recognition
- **Web-ready**: Direct support for downloading and extracting text from URLs
- **Memory efficient**: Process files without saving to disk
- **Modern Python**: Full type hints and clean API design

---

## 📦 Installation 

The library is modular so you can install all modules:

```bash
pip install pyxtxt[all]
```
or just the modules you need:
```bash
pip install pyxtxt[pdf,odf,docx,presentation,spreadsheet,html]
```
Because needed libraries are common, installing the html module will also enable SVG and XML support.
The architecture is designed to grow with new modules for additional formats.
## ⚠️ Note: You must have libmagic installed on your system (required by python-magic).
The pyproject.toml file should select the correct version for your system. But if you have any problem you can install it manually.

**On Ubuntu/Debian:**

```bash
sudo apt install libmagic1
```

**On Mac (Homebrew):**

```bash
brew install libmagic
```
**On Windows:**

Use python-magic-bin instead of python-magic for easier installation.

## 🛠️ Dependencies
- PyMuPDF (fitz)

- beautifulsoup4

- python-docx

- python-pptx

- odfpy

- openpyxl

- lxml

- xlrd (<2.0.0)

- python-magic

Dependencies are automatically installed from pyproject.toml.

## 📚 Usage Examples

### Basic Usage
```python
from pyxtxt import xtxt

# Extract from file path
text = xtxt("document.pdf")
print(text)

# Extract from BytesIO buffer
import io
with open("document.docx", "rb") as f:
    buffer = io.BytesIO(f.read())
text = xtxt(buffer)
print(text)
```

### NEW: Web Content Support
```python
import requests
from pyxtxt import xtxt, xtxt_from_url

# Method 1: Direct from bytes
response = requests.get("https://example.com/document.pdf")
text = xtxt(response.content)

# Method 2: Direct from Response object  
text = xtxt(response)

# Method 3: URL helper function
text = xtxt_from_url("https://example.com/document.pdf")
```

### Show Available Formats
```python
from pyxtxt import extxt_available_formats

# List supported MIME types
formats = extxt_available_formats()
print(formats)

# Pretty format names
formats = extxt_available_formats(pretty=True)
print(formats)
```
## 🌐 Common Web Use Cases

```python
# API responses
api_response = requests.post("https://api.example.com/generate-pdf")
text = xtxt(api_response.content)

# File uploads (Flask/Django)
uploaded_bytes = request.files['document'].read()
text = xtxt(uploaded_bytes)

# Email attachments
attachment_bytes = email_msg.get_payload(decode=True)
text = xtxt(attachment_bytes)
```

## ⚠️ Known Limitations

- **Legacy file detection**: When using raw streams without filenames, legacy files (.doc, .xls, .ppt) may not be correctly detected due to identical file signatures in libmagic
- **Filename hints recommended**: When available, providing original filenames improves detection accuracy
- **MSWrite .doc files**: Require `antiword` installation:
  ```bash
  sudo apt-get update && sudo apt-get install antiword
  ```

## 📖 Full Examples

See [examples.py](https://github.com/dede-amdp/pyxtxt/blob/main/examples.py) for comprehensive usage examples including:
- Local file processing
- Memory buffer handling  
- Web content extraction
- Error handling patterns
- All supported formats demonstration

## 🔒 License

Distributed under the MIT License. See LICENSE file for details.

The software is provided "as is" without any warranty of any kind.

## 🤝 Contributing

Pull requests, issues, and feedback are warmly welcome! 🚀

- **Bug reports**: Please include file samples and error details
- **Feature requests**: Describe your use case and expected behavior
- **Code contributions**: Follow existing patterns and add tests

## 📊 Changelog

### v0.1.24+
- ✅ Added support for `bytes` objects
- ✅ Added support for `requests.Response` objects  
- ✅ Added `xtxt_from_url()` helper function
- ✅ Improved type hints and error handling
- ✅ Enhanced web content processing capabilities
