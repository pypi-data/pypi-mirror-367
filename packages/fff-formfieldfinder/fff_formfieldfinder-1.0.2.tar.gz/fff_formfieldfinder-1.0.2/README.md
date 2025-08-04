# FFF - FormFieldFinder

**FFF** is a CLI-based tool that automatically detects login form structures and extracts field names and action URLs from HTML — perfect for use with fuzzing and brute-force tools like [`ffuf`](https://github.com/ffuf/ffuf) and [`wfuzz`](https://github.com/xmendez/wfuzz).

FFF intelligently detects both traditional `<form>` tags and modern login layouts where fields may be split across `<div>`, `<section>`, or sibling containers. It supports cookies, headers, and verbose form dumps.

---

## 🚀 Features

- Auto-detects `<form>` elements with login fields
- Handles non-standard layouts (fallbacks for `<div>`, `<section>`, etc.)
- Extracts `action` URL (with full `urljoin` resolution)
- Prints fuzz-ready login payload as Python `dict`
- Accepts custom cookies and headers
- Verbose mode to inspect all login containers
- Installable via `pip` or `pipx`
- Compatible with ffuf, wfuzz, Burp Suite automation

---

## 📦 Installation

### ➤ Using pipx (Recommended)

```bash
pipx install fff-formfieldfinder
```

```bash
# to add to PATH and reset shell for using the fff command
pipx ensurepath && exec $SHELL   
```

### ➤ Using pip

```bash
pip install fff-formfieldfinder
```

---

## 🧪 Usage

### 🔍 Basic Scan

```bash
fff -u https://example.com/login
```

### 🔍 Custom Headers and Cookies

```bash
fff -u https://example.com/login \
     -hd "X-Forwarded-For: 127.0.0.1" \
     -ck sessionid=abcd1234
```

### 🔍 With Custom Credentials

```bash
fff -u https://example.com/login -un admin -pw admin
```

### 🔍 Verbose Mode

```bash
fff -u https://example.com/login -v
```

---

## 📤 Output Example

```bash
FFF - Form Field Finder


Detected login form action URL: [https://example.com/auth]

Detected login fields: {'username': 'admin', 'password': 'admin', 'csrf_token': 'abc123'}

Detected Login form structure: <form>
```

---

## ⚙️ Command-Line Options

|Option|Description|
|---|---|
|`-u` / `--url`|Target URL to scan (**required**)|
|`-un` / `--username`|Username to use in payload (default: `admin`)|
|`-pw` / `--password`|Password to use in payload (default: `admin`)|
|`-ck` / `--cookie`|Cookie header(s), format: `key=value`|
|`-hd` / `--header`|Custom headers, format: `Header: value`|
|`-v` / `--verbose`|Enable verbose form dump|

---

## 📂 Project Structure

```
FFF-FormFieldFinder/
├── fff/
│   ├── __init__.py
│   └── cli.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
```

---

## 📜 Author

[Ph4nt01](https://github.com/Ph4nt01)
