# 🔐 LP-LoginParser

**LP-LoginParser** is a powerful command-line tool that extracts and submits login forms from web pages. It uses intelligent detection and fallback logic to identify login forms, even when they're non-standard or split across different HTML containers.

Designed for pentesters, bug bounty hunters, and automation workflows — LP-LoginParser detects fields, submits credentials, and saves session cookies and headers for later authenticated use.

---

## 🚀 Features

- ✅ Detects standard and non-standard login forms
- ✅ Parses form action and all input fields (username, password, CSRF, hidden)
- ✅ Supports custom headers and cookies
- ✅ Prints structured payload and status info
- ✅ Saves authenticated session to `session.json`
- ✅ Clean output with colorized status messages
- ✅ Installable via `pip` or `pipx`

---

## 📦 Installation

### Using pipx (Recommended for CLI tools)

```bash
pipx install lp-loginparser
````

### Using pip

```bash
pip install lp-loginparser
```

---

## ⚙️ Usage

```bash
lp-loginparser -u https://example.com/login
```

### With Verbose Output

```bash
lp-loginparser -u https://example.com/login -v
```

### Custom Headers and Cookies

```bash
lp-loginparser \
  -u https://example.com/login \
  -hd "X-Forwarded-For: 127.0.0.1" \
  -ck sessionid=abc123
```

---

## 🧪 Output Example

```
LP-LoginParser

[*] Container #1: <form action='/login' method='POST'>
<input type='text' name='username' value=''>
<input type='password' name='password' value=''>
<input type='submit' name='submit' value='Login'>

[+] Detected login form action URL: [https://example.com/login]

[+] Detected login fields: {'username': 'admin', 'password': 'admin', 'csrf_token': 'abc123'}

[+] Detected login form structure: <form>

Login status: 200 OK
[+] Login Successful

Session saved to: [session.json]
```

---

## 🧰 CLI Options

| Option                 | Description                                                      |
| ---------------------- | ---------------------------------------------------------------- |
| `-u`, `--url`          | URL of the login page (required)                                 |
| `-un`, `--username`    | Username to submit (default: `admin`)                            |
| `-pw`, `--password`    | Password to submit (default: `admin`)                            |
| `-v`, `--verbose`      | Enable verbose mode for HTML inspection                          |
| `-ck`, `--cookie`      | Cookies in `key=value` format                                    |
| `-hd`, `--header`      | Custom headers in `Key: Value` format                            |
| `-s`, `--session-file` | Output JSON file to store session info (default: `session.json`) |

---

## 📂 Project Structure

```
lp-loginparser/
├── lp_loginparser/
│   ├── __init__.py
│   └── cli.py
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Author

Made with passion for security automation by [Your Name](https://github.com/yourusername)

```

---

Let me know if you want a badge section (PyPI version, license, downloads), or if you'd like me to auto-generate the PyPI description from this ✅
```
