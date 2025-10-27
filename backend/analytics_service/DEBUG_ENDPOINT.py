# 🔍 ADD THIS DEBUG ENDPOINT TO app_clean.py

# Add this import at the top:
import sys

# Add this endpoint before if __name__ == "__main__":

@app.route("/api/debug/status", methods=["GET"])
def debug_status():
    """
    Debug endpoint to check deployment status.
    Visit: https://your-deployment-url.com/api/debug/status
    """
    import os
    import openai
    
    # Check file existence with absolute paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    status = {
        "status": "Flask is running ✅",
        "working_directory": os.getcwd(),
        "script_directory": current_dir,
        
        "environment": {
            "openai_key_present": bool(os.getenv('OPENAI_API_KEY')),
            "openai_key_length": len(os.getenv('OPENAI_API_KEY', '')) if os.getenv('OPENAI_API_KEY') else 0,
            "openai_key_prefix": os.getenv('OPENAI_API_KEY', '')[:7] if os.getenv('OPENAI_API_KEY') else None,
            "mongodb_uri_present": bool(os.getenv('MONGODB_URI')),
        },
        
        "model_files": {
            "classifier_exists": os.path.exists(os.path.join(current_dir, 'analytics_type_classifier.pkl')),
            "vectorizer_exists": os.path.exists(os.path.join(current_dir, 'analytics_vectorizer.pkl')),
            "cache_db_exists": os.path.exists(os.path.join(current_dir, 'tanaw_mapping_cache.db')),
        },
        
        "files_in_current_dir": [f for f in os.listdir(current_dir) if f.endswith('.pkl') or f.endswith('.db') or f.endswith('.py')][:20],
        
        "python_info": {
            "version": sys.version,
            "platform": sys.platform,
        },
        
        "package_versions": {
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "flask": Flask.__version__ if hasattr(Flask, '__version__') else 'unknown',
            "openai": getattr(openai, '__version__', 'unknown'),
        },
        
        "components_initialized": {
            "tanaw_processor": "TANAWDataProcessor" in globals(),
            "gpt_mapper": "GPTColumnMapper" in globals(),
        }
    }
    
    return jsonify(status), 200


@app.route("/api/debug/test-openai", methods=["GET"])
def test_openai():
    """
    Test if OpenAI connection works.
    Visit: https://your-deployment-url.com/api/debug/test-openai
    """
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return jsonify({
            "success": False,
            "error": "OPENAI_API_KEY environment variable not set",
            "checked_vars": ["OPENAI_API_KEY", "OPENAI_KEY", "OPENAI_API", "OPENAI_TOKEN"],
            "help": "Add OPENAI_API_KEY to your deployment environment variables"
        }), 500
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        
        return jsonify({
            "success": True,
            "message": "OpenAI connection working!",
            "api_key_prefix": api_key[:10] + "...",
            "response": response.choices[0].message.content,
            "model_used": response.model
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "help": "Check if API key is valid and has credits"
        }), 500


# Copy these two endpoints into your app_clean.py file
# Place them before the line: if __name__ == "__main__":

