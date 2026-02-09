# Security Policy

## Supported Versions

flux GPU is currently in its initial release. We will provide security updates for:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

---

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in flux GPU, please report it responsibly.

### How to Report

**Do NOT** create a public GitHub issue for security vulnerabilities.

Instead, please email:
- **Email**: concealment960@gmail.com
- **Subject**: [SECURITY] Brief description of issue

### What to Include

Please provide:
1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** (what an attacker could do)
4. **Suggested fix** (if you have one)
5. **Your contact information** for follow-up

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix timeline**: Depending on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release

### Disclosure Policy

- We will work with you to understand and fix the issue
- We will credit you in the fix (unless you prefer to remain anonymous)
- We ask that you do not publicly disclose until we've released a fix
- We will coordinate disclosure timing with you

---

## Security Considerations for Users

### Hardware Designs (RTL)

**IMPORTANT**: flux GPU is an **educational platform**. If you plan to use it in production:

1. **Conduct thorough security review**
   - RTL code review
   - Formal verification
   - Penetration testing

2. **Known limitations**:
   - No hardware security features (TEE, secure boot, etc.)
   - No side-channel attack mitigations
   - Designed for learning, not production security

3. **Add security layers** if needed:
   - Memory protection units
   - Access control
   - Encryption
   - Secure boot

### Software Toolchain

1. **Assembler/Simulator**:
   - Input validation exists but may not be exhaustive
   - Do not run untrusted assembly programs
   - Sandbox if running user code

2. **Firmware**:
   - No authentication/authorization
   - Add security layers for production use

### FPGA/ASIC Builds

1. **Supply chain security**:
   - Verify tool downloads (checksums)
   - Use official PDKs
   - Review all scripts before running

2. **Fabrication**:
   - Use trusted fabrication sources
   - Understand shuttle risks
   - Review all GDSII carefully

---

## Security Best Practices

### For Contributors

1. **Code review**:
   - Review all changes carefully
   - Watch for injection vulnerabilities
   - Validate all inputs

2. **Dependencies**:
   - Keep Python packages updated
   - Review dependency changes
   - Use virtual environments

3. **Secrets**:
   - Never commit credentials
   - No API keys in code
   - Use environment variables

### For Users

1. **Updates**:
   - Watch for security releases
   - Update promptly
   - Read release notes

2. **Isolation**:
   - Run simulations in containers
   - Don't run untrusted HDL
   - Sandbox FPGA programming

3. **Verification**:
   - Verify signatures (when available)
   - Check file hashes
   - Use official sources only

---

## Scope

### In Scope

Security issues in:
- ✅ RTL code (potential hardware vulnerabilities)
- ✅ Python toolchain (code injection, etc.)
- ✅ Documentation (misleading security info)
- ✅ Build scripts (malicious code execution)

### Out of Scope

- ❌ Issues in third-party tools (Yosys, Verilator, etc.)
  - Report to those projects directly
- ❌ Physical security of manufactured chips
- ❌ Side-channel attacks (known limitation)
- ❌ Issues requiring physical access to FPGA

---

## Security Features (Current)

### What We Have

1. **Input validation**:
   - Assembly syntax checking
   - Instruction validation
   - Register bounds checking

2. **Safe defaults**:
   - No network access
   - Local-only operation
   - Sandboxed simulation

3. **Open source**:
   - Code is reviewable
   - Community can audit
   - Transparent development

### What We Don't Have (Yet)

1. **Signed releases**
   - Coming in future versions

2. **Automated security scanning**
   - Planned for CI/CD

3. **Formal verification**
   - Educational project scope

---

## Hall of Fame

We will recognize security researchers who responsibly disclose vulnerabilities:

*No vulnerabilities reported yet!*

---

## Questions?

For security-related questions:
- Email: concealment960@gmail.com
- GitHub Discussions: https://github.com/dibyx/flux/discussions

For general questions, use GitHub Issues.

---

**Thank you for helping keep flux GPU secure!** 🔒
