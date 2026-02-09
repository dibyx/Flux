#!/usr/bin/env python3
"""
Pre-release verification script for flux GPU
Run this before pushing to GitHub to ensure everything is ready
"""

import os
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"{Colors.GREEN}✓{Colors.END} {description}: {filepath}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {description} MISSING: {filepath}")
        return False

def check_file_contains(filepath, text, description):
    """Check if a file contains specific text"""
    if not os.path.exists(filepath):
        print(f"{Colors.RED}✗{Colors.END} File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if text in content:
            print(f"{Colors.GREEN}✓{Colors.END} {description}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} {description} - text not found")
            return False

def main():
    print("="*70)
    print(f"{Colors.BLUE}flux GPU - Pre-Release Verification{Colors.END}")
    print("="*70)
    print()
    
    passed = 0
    failed = 0
    
    # Check essential files
    print(f"{Colors.BLUE}1. Checking Essential Files...{Colors.END}")
    essential_files = [
        ("README.md", "README"),
        ("LICENSE", "License"),
        ("CONTRIBUTING.md", "Contributing guidelines"),
        ("CODE_OF_CONDUCT.md", "Code of conduct"),
        (".gitignore", "Git ignore"),
        (".gitattributes", "Git attributes"),
        ("SECURITY.md", "Security policy"),
    ]
    
    for filepath, desc in essential_files:
        if check_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Check GitHub-specific files
    print(f"{Colors.BLUE}2. Checking GitHub Files...{Colors.END}")
    github_files = [
        (".github/workflows/ci.yml", "GitHub Actions CI"),
        (".github/ISSUE_TEMPLATE/bug_report.md", "Bug report template"),
        (".github/ISSUE_TEMPLATE/feature_request.md", "Feature request template"),
        (".github/PULL_REQUEST_TEMPLATE.md", "Pull request template"),
    ]
    
    for filepath, desc in github_files:
        if check_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Check documentation
    print(f"{Colors.BLUE}3. Checking Documentation...{Colors.END}")
    doc_files = [
        ("PROJECT_SUMMARY.md", "Project summary"),
        ("FINAL_REPORT.md", "Final report"),
        ("docs/GETTING_STARTED.md", "Getting started guide"),
        ("docs/DEMOCRATIZATION.md", "Democratization manifesto"),
        ("docs/VISUAL_GALLERY.md", "Visual gallery"),
        ("docs/CONTACT.md", "Contact information"),
    ]
    
    for filepath, desc in doc_files:
        if check_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Check for placeholders
    print(f"{Colors.BLUE}4. Checking for Placeholders...{Colors.END}")
    placeholder_checks = [
        ("README.md", "[OWNER]", "No [OWNER] placeholder"),
        ("README.md", "[MAINTAINER", "No [MAINTAINER] placeholder"),
        ("CONTRIBUTING.md", "dibyx", "GitHub username updated"),
        ("CONTRIBUTING.md", "concealment960@gmail.com", "Email updated"),
    ]
    
    for filepath, text, desc in placeholder_checks:
        if filepath.endswith(".md") and "[" in text:
            # Checking that placeholder does NOT exist
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    if text not in f.read():
                        print(f"{Colors.GREEN}✓{Colors.END} {desc}")
                        passed += 1
                    else:
                        print(f"{Colors.RED}✗{Colors.END} Found placeholder: {text} in {filepath}")
                        failed += 1
        else:
            # Checking that text DOES exist
            if check_file_contains(filepath, text, desc):
                passed += 1
            else:
                failed += 1
    print()
    
    #  Check images
    print(f"{Colors.BLUE}5. Checking Images...{Colors.END}")
    if os.path.exists("docs/images"):
        images = list(Path("docs/images").glob("*.png")) + list(Path("docs/images").glob("*.jpg"))
        if len(images) >= 11:
            print(f"{Colors.GREEN}✓{Colors.END} Found {len(images)} images")
            passed += 1
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} Only {len(images)} images found (expected 12+)")
            failed += 1
    else:
        print(f"{Colors.RED}✗{Colors.END} docs/images directory not found")
        failed += 1
    print()
    
    # Check examples
    print(f"{Colors.BLUE}6. Checking Examples...{Colors.END}")
    example_files = [
        ("examples/math_demo.py", "Math demo"),
        ("examples/visual_demo.py", "Visual demo"),
        ("sw-toolchain/examples/vecadd.s", "Vector add example"),
    ]
    
    for filepath, desc in example_files:
        if check_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Summary
    print("="*70)
    total = passed + failed
    percentage = (passed / total * 100) if total > 0 else 0
    
    if failed == 0:
        print(f"{Colors.GREEN}✓ ALL CHECKS PASSED! ({passed}/{total}){Colors.END}")
        print(f"{Colors.GREEN}Repository is ready for GitHub release!{Colors.END}")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠ {passed}/{total} checks passed ({percentage:.1f}%){Colors.END}")
        print(f"{Colors.RED}Please fix {failed} issues before releasing{Colors.END}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print()
    print("Next steps:")
    print("  1. Fix any issues above")
    print("  2. Run: git init")
    print("  3. Run: git add .")
    print("  4. Run: git commit -m \"Initial release: flux GPU v2.0\"")
    print("  5. Create GitHub repo and push")
    print()
    print("See RELEASE_CHECKLIST.md for full instructions")
    sys.exit(exit_code)
