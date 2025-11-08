#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick setup verification script for Jetpo.
Run this to verify that the project is set up correctly.
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[FAIL] {description}: {filepath} - NOT FOUND")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        print(f"[OK] {description}: {dirpath}")
        return True
    else:
        print(f"[FAIL] {description}: {dirpath} - NOT FOUND")
        return False

def main():
    print("\n" + "="*60)
    print("Jetpo Setup Verification")
    print("="*60 + "\n")

    checks_passed = 0
    total_checks = 0

    # Check core files
    print("\nChecking Core Files...")
    total_checks += 1
    if check_file("manage.py", "Django manage.py"):
        checks_passed += 1

    total_checks += 1
    if check_file("requirements.txt", "Python requirements"):
        checks_passed += 1

    total_checks += 1
    if check_file("package.json", "Node package.json"):
        checks_passed += 1

    total_checks += 1
    if check_file(".env", "Environment file"):
        checks_passed += 1

    # Check configuration
    print("\nChecking Configuration...")
    total_checks += 1
    if check_directory("config", "Config directory"):
        checks_passed += 1

    total_checks += 1
    if check_file("config/settings.py", "Django settings"):
        checks_passed += 1

    total_checks += 1
    if check_file("config/urls.py", "URL configuration"):
        checks_passed += 1

    # Check apps
    print("\nChecking Apps...")
    apps = ["accounts", "core", "funds", "portfolios"]
    for app in apps:
        total_checks += 1
        if check_directory(app, f"{app.capitalize()} app"):
            checks_passed += 1

    # Check templates
    print("\nChecking Templates...")
    templates = [
        "templates/base.html",
        "templates/home.html",
        "templates/account/login.html",
        "templates/account/signup.html",
    ]
    for template in templates:
        total_checks += 1
        if check_file(template, template):
            checks_passed += 1

    # Check static files
    print("\nChecking Static Files...")
    total_checks += 1
    if check_file("static/css/input.css", "Tailwind input CSS"):
        checks_passed += 1

    total_checks += 1
    if check_file("tailwind.config.js", "Tailwind config"):
        checks_passed += 1

    # Check documentation
    print("\nChecking Documentation...")
    docs = ["README.md", "ARCHITECTURE.md", "SETUP.md", "PROJECT_STATUS.md"]
    for doc in docs:
        total_checks += 1
        if check_file(doc, doc):
            checks_passed += 1

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Checks passed: {checks_passed}/{total_checks}")

    if checks_passed == total_checks:
        print("\n[SUCCESS] All checks passed! Your setup is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install Node packages: npm install")
        print("3. Run migrations: python manage.py migrate")
        print("4. Create superuser: python manage.py createsuperuser")
        print("5. Build CSS: npm run tailwind:build")
        print("6. Start server: python manage.py runserver")
        print("\nSee SETUP.md for detailed instructions.\n")
        return 0
    else:
        print("\n[ERROR] Some checks failed. Please review the errors above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
