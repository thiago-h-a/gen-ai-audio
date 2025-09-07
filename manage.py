#!/usr/bin/env python3
import os
import sys

# Entry point for Django administrative tasks (e.g., runserver, migrate).
# This remains slim by design: configuration lives in notetaker/settings.py.

def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notetaker.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
