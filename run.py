from flask import Flask

app = Flask(__name__)
    
from app.routes import main
app.register_blueprint(main)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
