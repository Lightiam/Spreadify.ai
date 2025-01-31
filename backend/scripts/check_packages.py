import pkg_resources
import sys
import os

def check_environment():
    """Check Python environment and installed packages."""
    print("=== Environment Check ===")
    
    print("\nInstalled packages:")
    for dist in pkg_resources.working_set:
        print(f"{dist.key} {dist.version}")
    
    print("\nPython path:")
    for path in sys.path:
        print(path)
    
    print("\nCurrent working directory:")
    print(os.getcwd())
    
    print("\nRelevant environment variables:")
    for key, value in os.environ.items():
        if any(term in key for term in ["PYTHON", "DATABASE", "TEST"]):
            print(f"{key}={value}")

if __name__ == "__main__":
    check_environment()
