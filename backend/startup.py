#!/usr/bin/env python3
"""
Startup script to sanitize environment variables before loading the main application.
This addresses the issue where DATABASE_URL is set with a 'psql ' prefix in production.
"""

import os
import sys
from urllib.parse import urlparse


def sanitize_database_url():
    """Sanitize the DATABASE_URL environment variable if it has malformed format."""
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        original_url = db_url
        # Clean up the URL by removing 'psql ' prefix and surrounding quotes
        cleaned_url = db_url.strip()
        
        # Handle the specific case: 'psql postgresql://...' (with quotes)
        if cleaned_url.startswith("'psql postgresql://") and cleaned_url.endswith("'"):
            start_pos = len("'psql ")
            end_pos = len(cleaned_url) - 1
            cleaned_url = cleaned_url[start_pos:end_pos].strip()
        elif cleaned_url.startswith("psql postgresql://"):
            # Handle case without outer quotes: psql postgresql://...
            start_pos = len("psql ")
            cleaned_url = cleaned_url[start_pos:].strip()
        elif cleaned_url.startswith("'psql ") and "postgresql://" in cleaned_url:
            # Handle case: 'psql postgresql://...' (with leading quote but maybe trailing quote)
            start_pos = len("'psql ")
            cleaned_url = cleaned_url[start_pos:].strip()
            if cleaned_url.endswith("'"):
                cleaned_url = cleaned_url[:-1].strip()
        
        # Remove any surrounding quotes
        cleaned_url = cleaned_url.strip("'\"")
        
        # If the URL was changed, update the environment variable
        if cleaned_url != original_url:
            print(f"INFO: Sanitized DATABASE_URL from: '{original_url}' to: '{cleaned_url}'", file=sys.stderr)
            os.environ['DATABASE_URL'] = cleaned_url
        else:
            print(f"INFO: DATABASE_URL format is valid: '{cleaned_url}'", file=sys.stderr)


def main():
    """Main entry point that sanitizes environment and then imports the application."""
    sanitize_database_url()
    
    # Now import and run the main application
    try:
        from app.main import socket_app as app
        import uvicorn
        
        # Run the application
        uvicorn.run(
            app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload=os.getenv("RELOAD", "false").lower() == "true"
        )
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
