from app import create_app
from flask import url_for

app = create_app()

with app.app_context():
    with app.test_request_context():
        print(f"URL for main.dashboard: {url_for('main.dashboard')}")
        print(f"URL for auth.login: {url_for('auth.login')}")
        try:
            print(f"URL for main.report_problem (id=1): {url_for('main.report_problem', device_id=1)}")
        except Exception as e:
            print(f"Error for main.report_problem: {e}")
