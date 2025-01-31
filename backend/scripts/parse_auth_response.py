import sys
import json

def parse_auth_response():
    """Parse auth response from stdin and extract access token."""
    try:
        response = json.load(sys.stdin)
        return response.get('access_token', '')
    except json.JSONDecodeError:
        print("Error: Invalid JSON response", file=sys.stderr)
        return ''
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return ''

if __name__ == "__main__":
    token = parse_auth_response()
    print(token)
