try:
    import flask
    import flask_login
    import flask_sqlalchemy
    import flask_mail
    import authlib
    import waitress
    import dotenv
    import requests
    import psycopg2
    print("All external dependencies found.")
except ImportError as e:
    print(f"External dependency missing: {e}")
    exit(1)

try:
    from app import create_app
    print("Local import 'from app import create_app' successful.")
except ImportError as e:
    print(f"Local import failed: {e}")
    # Print sys.path to help debug
    import sys
    print("sys.path:", sys.path)
    exit(1)
except Exception as e:
    print(f"Error during import of app: {e}")
    exit(1)
