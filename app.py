from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    user_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    user_id   = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")

    if not user_name:
        return "Utilisateur non authentifié", 401

    return f"Bonjour {user_name} (ID: {user_id}) !"
