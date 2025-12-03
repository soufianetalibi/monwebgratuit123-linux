from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    user_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    user_id   = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")

    if not user_name:
        return "Utilisateur non authentifié", 401

    return f"Bonjour {user_name} (ID: {user_id}) !"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
