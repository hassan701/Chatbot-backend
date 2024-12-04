# main.py
from api_handler import app

if __name__ == '__main__':
    # Run the Flask application on port 5000
    app.run(port=80)
