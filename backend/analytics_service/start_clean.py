#!/usr/bin/env python3
"""
Start TANAW Clean Architecture Server
Pure OpenAI + TANAW implementation
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Import and run the clean app
from app_clean import app

if __name__ == "__main__":
    print("🚀 Starting TANAW Clean Architecture Server")
    print("📡 Server will be available at: http://localhost:5002")
    print("🔄 Auto-reload enabled for development")
    print("=" * 60)
    print("✨ Clean Architecture: OpenAI → Column Mapping → TANAW Processing → Charts")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5002)
