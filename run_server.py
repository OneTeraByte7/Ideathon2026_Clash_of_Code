"""
Simple server runner that properly configures Python path
"""
import sys
import os

# Add the server directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now run the server
if __name__ == "__main__":
    import uvicorn
    # Change to server directory to ensure relative imports work
    os.chdir(current_dir)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)