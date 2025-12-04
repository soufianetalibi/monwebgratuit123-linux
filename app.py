from flask import Flask, request, render_template_string

app = Flask(__name__)

# Template HTML simple
TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentification Entra ID</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        .icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        .user-info {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }
        .user-name {
            font-size: 1.5rem;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .user-id {
            font-size: 0.9rem;
            color: #666;
            font-family: monospace;
            word-break: break-all;
        }
        .message {
            color: #666;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            margin-top: 1.5rem;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            transition: transform 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="card">
        {% if user_name %}
            <div class="icon">👤</div>
            <h1>Bienvenue !</h1>
            <div class="user-info">
                <div class="user-name">{{ user_name }}</div>
                {% if user_id %}
                <div class="user-id">ID: {{ user_id }}</div>
                {% endif %}
            </div>
            <p class="message">Vous êtes connecté avec succès via Entra ID</p>
            <a href="/.auth/logout" class="btn">Se déconnecter</a>
        {% else %}
            <div class="icon">🔐</div>
            <h1>Authentification requise</h1>
            <p class="message">Merci de vous authentifier pour accéder à l'application</p>
            <a href="/.auth/login/aad" class="btn">Se connecter avec Microsoft</a>
        {% endif %}
        <div class="footer">
            Application sécurisée avec Entra ID
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    # Récupérer les informations de l'utilisateur depuis les headers Azure
    user_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    user_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
    
    return render_template_string(TEMPLATE, user_name=user_name, user_id=user_id)

if __name__ == "__main__":
    app.run(debug=False)