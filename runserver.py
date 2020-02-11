"""
This script runs the flaskwebapp application using a development server.
"""

from os import environ
from flaskwebapp import app

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=5000)
