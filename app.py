"""
Application Web Flask moderne avec authentification Azure AD
Python 3.12+

Installation des dépendances:
pip install flask msal python-dotenv flask-session

Configuration requise:
1. Créer un fichier .env avec:
   AZURE_CLIENT_ID=votre_client_id
   AZURE_CLIENT_SECRET=votre_client_secret
   AZURE_TENANT_ID=votre_tenant_id
   SECRET_KEY=votre_secret_key_flask
   REDIRECT_URI=http://localhost:5000/getAToken

2. Configurer l'app Azure AD:
   - Créer une application dans Azure Portal
   - Ajouter l'URI de redirection
   - Générer un secret client
"""

from flask import Flask, render_template_string, redirect, request, session, url_for
from flask_session import Session
import msal
import os
from dotenv import load_dotenv
from functools import wraps

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configuration Azure AD
AZURE_CONFIG = {
    'client_id': os.getenv('AZURE_CLIENT_ID'),
    'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
    'authority': f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}",
    'redirect_uri': os.getenv('REDIRECT_URI', 'https://monwebgratuit123-linux.azurewebsites.net/getAToken'),
    'scope': ['User.Read']
}

def get_msal_app():
    """Initialise l'application MSAL"""
    return msal.ConfidentialClientApplication(
        AZURE_CONFIG['client_id'],
        authority=AZURE_CONFIG['authority'],
        client_credential=AZURE_CONFIG['client_secret']
    )

def login_required(f):
    """Décorateur pour protéger les routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Templates HTML
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - Application Azure AD</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .card {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        
        .card p {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .feature-item {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .feature-item h4 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .feature-item p {
            color: #666;
            font-size: 0.9rem;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>👋 Bienvenue</h2>
        <p>Connectez-vous avec votre compte Microsoft Azure AD pour accéder à l'application.</p>
        
        <div class="feature-grid">
            <div class="feature-item">
                <h4>🔒 Sécurisé</h4>
                <p>Authentification via Azure AD</p>
            </div>
            <div class="feature-item">
                <h4>⚡ Moderne</h4>
                <p>Interface responsive</p>
            </div>
            <div class="feature-item">
                <h4>🚀 Rapide</h4>
                <p>Connexion en un clic</p>
            </div>
        </div>
        
        <div style="margin-top: 2rem;">
            <a href="{{ auth_url }}" class="btn">Se connecter avec Microsoft</a>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tableau de bord</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar h1 {
            color: #667eea;
            font-size: 1.5rem;
        }
        
        .navbar .user-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .navbar .user-name {
            color: #333;
            font-weight: 500;
        }
        
        .container {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .card {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 700px;
            width: 100%;
            text-align: center;
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        
        .card p {
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
            margin-left: 1rem;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }
        
        .user-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
        }
        
        .user-card h3 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .user-details {
            text-align: left;
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .user-details p {
            margin: 0.5rem 0;
            color: white;
        }
        
        .user-details strong {
            color: rgba(255, 255, 255, 0.8);
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .feature-item {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .feature-item h4 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .feature-item p {
            color: #666;
            font-size: 0.9rem;
            margin: 0;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>🔐 Mon Application</h1>
        <div class="user-info">
            <span class="user-name">{{ user.name }}</span>
            <a href="{{ logout_url }}" class="btn btn-secondary">Déconnexion</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="card">
            <div class="user-card">
                <h3>👤 Profil utilisateur</h3>
                <div class="user-details">
                    <p><strong>Nom :</strong> {{ user.name }}</p>
                    <p><strong>Email :</strong> {{ user.preferred_username }}</p>
                    {% if user.get('job_title') %}
                    <p><strong>Poste :</strong> {{ user.job_title }}</p>
                    {% endif %}
                </div>
            </div>
            
            <h2>✨ Tableau de bord</h2>
            <p>Vous êtes connecté avec succès ! Cette application démontre l'intégration d'Azure AD avec Flask.</p>
            
            <div class="feature-grid">
                <div class="feature-item">
                    <h4>📊 Analyses</h4>
                    <p>Accédez aux statistiques</p>
                </div>
                <div class="feature-item">
                    <h4>📁 Documents</h4>
                    <p>Gérez vos fichiers</p>
                </div>
                <div class="feature-item">
                    <h4>⚙️ Paramètres</h4>
                    <p>Configurez l'application</p>
                </div>
                <div class="feature-item">
                    <h4>👥 Équipe</h4>
                    <p>Collaborez efficacement</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Page d'accueil - redirige selon l'état de connexion"""
    if session.get('user'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Page de connexion"""
    if session.get('user'):
        return redirect(url_for('dashboard'))
    
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        AZURE_CONFIG['scope'],
        redirect_uri=AZURE_CONFIG['redirect_uri']
    )
    
    return render_template_string(LOGIN_PAGE, auth_url=auth_url)

@app.route('/getAToken')
def get_token():
    """Callback Azure AD - récupère le token"""
    code = request.args.get('code')
    if not code:
        return redirect(url_for('login'))
    
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=AZURE_CONFIG['scope'],
        redirect_uri=AZURE_CONFIG['redirect_uri']
    )
    
    if 'error' in result:
        return f"Erreur d'authentification: {result.get('error_description')}"
    
    session['user'] = result.get('id_token_claims')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    return render_template_string(
        DASHBOARD_PAGE, 
        user=session.get('user'),
        logout_url=url_for('logout')
    )

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    logout_url = f"{AZURE_CONFIG['authority']}/oauth2/v2.0/logout?post_logout_redirect_uri={request.host_url}"
    return redirect(logout_url)

if __name__ == '__main__':
    # Vérifier la configuration
    if not all([AZURE_CONFIG['client_id'], AZURE_CONFIG['client_secret'], os.getenv('AZURE_TENANT_ID')]):
        print("⚠️  ATTENTION: Configurez les variables d'environnement dans un fichier .env")
        print("Variables requises: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
    
    print("🚀 Application démarrée")
    # Utiliser le port fourni par Azure ou 8000 par défaut
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)