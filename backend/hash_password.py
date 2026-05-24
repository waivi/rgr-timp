from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

new_password = "250106vA"  # замени на свой
hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
print(f"Новый хеш: {hashed}")