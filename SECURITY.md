# Security Policy

## Overview

This document outlines security practices and policies for the Cannabis Analytics Dashboard project.

## Supported Versions

This project is currently in development (v0.1.0). Security updates will be applied to the main branch.

| Version | Supported          | Status      |
| ------- | ------------------ | ----------- |
| 0.1.x   | :white_check_mark: | Development |
| < 0.1   | :x:                | Deprecated  |

## Security Best Practices

### 1. Environment Variables and API Keys

**CRITICAL**: Never commit sensitive information to version control.

#### Protected Files
The following files contain or may contain sensitive information and are protected by `.gitignore`:
- `.env` - Environment variables including API keys
- `.streamlit/secrets.toml` - Streamlit secrets
- `*.key`, `*.pem` - Private keys and certificates

#### API Key Handling
- Store API keys in `.env` file (see `.env.example` for template)
- Use the `Config` class from `app/config/env.py` to access environment variables
- Never hardcode API keys in source files
- Validate API keys before use with `Config.get_api_key()`

Example:
```python
from config.env import Config

api_key = Config.get_api_key()
if not api_key:
    st.error("API key not configured. Please set OPENAI_API_KEY in .env file.")
    st.stop()
```

### 2. Data Validation

All data files are validated on load to prevent security issues:

#### File Validation
- File existence checks before loading
- Required column validation
- Data type validation
- Empty file warnings

#### Input Sanitization
- User inputs (if any) should be sanitized before processing
- File paths are constructed using `os.path.join()` to prevent path traversal
- No direct user input is used in file operations

### 3. Dependency Management

#### Package Security
- Dependencies managed via Poetry with locked versions (`poetry.lock`)
- Regular security audits recommended via `poetry show --outdated`
- Use `pip-audit` or similar tools to check for known vulnerabilities

#### Update Strategy
```bash
# Check for outdated packages
poetry show --outdated

# Update specific package
poetry update package-name

# Update all packages (test thoroughly after)
poetry update
```

### 4. Data Privacy

#### Sensitive Data
This application processes cannabis retail and social media sentiment data. Consider:
- **Personal Information**: Ensure no PII (Personally Identifiable Information) is in data files
- **Business Sensitive**: Retailer data may be business-sensitive; limit access appropriately
- **Compliance**: Ensure data handling complies with relevant regulations (CCPA, etc.)

#### Data Storage
- Data files stored in `data/` directory (not in .gitignore by default)
- If data becomes sensitive, add to .gitignore and provide data loading instructions
- Consider encryption for sensitive data at rest

### 5. Streamlit Security

#### Secrets Management
Streamlit secrets should be stored in `.streamlit/secrets.toml` (ignored by git):
```toml
# .streamlit/secrets.toml
[database]
# connection string here

[api]
openai_key = "your-key-here"
```

Access via:
```python
import streamlit as st
api_key = st.secrets["api"]["openai_key"]
```

#### Deployment Security
When deploying:
- Set secrets via Streamlit Cloud UI or deployment platform
- Use environment variables for sensitive configuration
- Enable authentication if required
- Use HTTPS for all deployments

### 6. Code Security

#### File Operations
- All file operations use absolute paths via `get_data_dir()`
- No user input used in file path construction
- Try-except blocks prevent information disclosure via error messages

#### Error Handling
- User-friendly error messages via Streamlit UI
- Technical details logged but not exposed to users
- Use `st.error()` and `st.warning()` appropriately

### 7. Pre-commit Hooks (Recommended)

Install pre-commit hooks to prevent accidental commits of sensitive data:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: check-yaml
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install hooks
pre-commit install
```

### 8. Testing Security

Security-related tests should verify:
- API keys are not hardcoded (grep for patterns)
- Sensitive files are in .gitignore
- Error messages don't leak sensitive information
- Data validation prevents malformed input

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability in this project:

1. **DO NOT** create a public GitHub issue
2. Email the maintainer directly with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Timeline**: Critical issues within 2 weeks, others within 4 weeks
- **Disclosure**: Coordinated disclosure after fix is released

### Scope

The following are **IN SCOPE** for security reports:
- API key exposure or insecure handling
- Path traversal vulnerabilities
- SQL injection (if database added)
- XSS vulnerabilities (if user input added)
- Dependency vulnerabilities (critical/high severity)

The following are **OUT OF SCOPE**:
- Issues in third-party dependencies (report to maintainers)
- Social engineering attacks
- Physical security issues
- Denial of service attacks against the application

## Security Checklist for Developers

Before committing code:
- [ ] No API keys or passwords in code
- [ ] All sensitive config in .env file
- [ ] .env file in .gitignore
- [ ] User input sanitized (if applicable)
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies up to date
- [ ] File operations use safe path handling
- [ ] Data validation in place

Before deploying:
- [ ] Environment variables set in deployment platform
- [ ] Streamlit secrets configured
- [ ] HTTPS enabled
- [ ] Authentication enabled (if required)
- [ ] Data files reviewed for sensitive information
- [ ] Access logs configured (if applicable)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://snyk.io/blog/python-security-best-practices-cheat-sheet/)
- [Streamlit Security](https://docs.streamlit.io/library/advanced-features/security-reminders)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Contact

For security concerns, contact the project maintainer through GitHub or the email specified in the repository.

---
**Last Updated**: November 2025
**Version**: 1.0
