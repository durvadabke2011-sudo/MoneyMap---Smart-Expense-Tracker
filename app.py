from flask import Flask
from config import SECRET_KEY
from models import create_tables
from auth import auth_bp
from routes import routes_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    print("🚀 Starting MoneyMap...")
    create_tables()
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True)
