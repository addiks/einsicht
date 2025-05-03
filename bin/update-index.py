
import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    sys.argv
    
    try:
        print("Lorem ipsum")
        
    except Exception:
        sys.exit(0)