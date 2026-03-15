from app import create_app
from flask import url_for

app = create_app()

with app.app_context():
    with app.test_request_context():
        import routes_main
        import routes_auth
        
        print("Testing all routes:")
        for rule in app.url_map.iter_rules():
            print(f"Endpoint: {rule.endpoint}, Rule: {rule}")
            try:
                if 'static' in rule.endpoint:
                    print(f"  URL: {url_for(rule.endpoint, filename='test.js')}")
                elif '<int:device_id>' in str(rule):
                    print(f"  URL: {url_for(rule.endpoint, device_id=1)}")
                elif '<int:id>' in str(rule):
                    print(f"  URL: {url_for(rule.endpoint, id=1)}")
                elif '<path:filename>' in str(rule):
                    print(f"  URL: {url_for(rule.endpoint, filename='test.txt')}")
                elif not rule.arguments:
                    print(f"  URL: {url_for(rule.endpoint)}")
            except Exception as e:
                print(f"  Error: {e}")
