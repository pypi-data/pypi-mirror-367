#!/usr/bin/env python3
"""
Test script to reproduce the Babel locale selector error.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing Flask-Babel imports...")
    from flask_babel import Babel
    print("✓ Flask-Babel import successful")
    
    print("\nTesting Flask app creation...")
    from url_analyzer.web.app import create_app
    
    print("Creating Flask app...")
    app = create_app()
    print("✓ Flask app created successfully")
    
    print("\nTesting app context...")
    with app.app_context():
        print("✓ App context works")
        
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()