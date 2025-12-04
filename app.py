from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    user_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    user_id   = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")

    # Affiche tous les headers X-MS-*
    headers = {k:v for k,v in request.headers.items() if k.startswith("X-MS-")}

    return f"""
    <h1>Headers reçus :</h1>
    <pre>{headers}</pre>
    <p>Nom utilisateur : {user_name}</p>
    <p>ID utilisateur : {user_id}</p>
    <p><a href="/.auth/logout?post_logout_redirect_uri=/">Se déconnecter</a></p>
    """
