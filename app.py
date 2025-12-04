from flask import Flask, request, render_template, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre-cle-secrete-changez-moi')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configuration CORS - À adapter selon vos besoins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://votredomaine.azurewebsites.net"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Décorateur pour vérifier l'authentification Azure
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_name = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
        user_id = request.headers.get("X-MS-CLIENT-PRINCIPAL-ID")
        
        if not user_name:
            if request.path.startswith('/api/'):
                return jsonify({"error": "Non authentifié"}), 401
            return render_template('error.html', 
                                 message="Vous devez être authentifié pour accéder à cette page",
                                 code=401), 401
        
        # Stocker les infos utilisateur dans g pour y accéder facilement
        from flask import g
        g.user_name = user_name
        g.user_id = user_id
        g.user_roles = request.headers.get("X-MS-CLIENT-PRINCIPAL-IDP", "").split(',')
        
        return f(*args, **kwargs)
    return decorated_function

# Fonction helper pour obtenir les infos utilisateur
def get_user_info():
    return {
        'name': request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME"),
        'id': request.headers.get("X-MS-CLIENT-PRINCIPAL-ID"),
        'email': request.headers.get("X-MS-CLIENT-PRINCIPAL-EMAIL"),
        'idp': request.headers.get("X-MS-CLIENT-PRINCIPAL-IDP"),
        'roles': request.headers.get("X-MS-CLIENT-PRINCIPAL-ROLES", "").split(',')
    }

# Routes Frontend
@app.route("/")
@limiter.limit("30 per minute")
@require_auth
def home():
    user_info = get_user_info()
    return render_template('index.html', user=user_info)

@app.route("/dashboard")
@limiter.limit("30 per minute")
@require_auth
def dashboard():
    user_info = get_user_info()
    # Ajoutez ici la logique pour récupérer les données du dashboard
    stats = {
        'connexions': 42,
        'derniere_visite': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'statut': 'Actif'
    }
    return render_template('dashboard.html', user=user_info, stats=stats)

@app.route("/profil")
@limiter.limit("30 per minute")
@require_auth
def profil():
    user_info = get_user_info()
    return render_template('profil.html', user=user_info)

# Routes API
@app.route("/api/user")
@limiter.limit("10 per minute")
@require_auth
def api_user():
    user_info = get_user_info()
    return jsonify(user_info)

@app.route("/api/health")
@limiter.limit("60 per minute")
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route("/api/data", methods=['GET', 'POST'])
@limiter.limit("20 per minute")
@require_auth
def api_data():
    if request.method == 'POST':
        data = request.get_json()
        # Validation basique
        if not data:
            return jsonify({"error": "Données invalides"}), 400
        
        # Traiter les données ici
        return jsonify({
            "message": "Données reçues avec succès",
            "data": data
        }), 201
    
    # GET
    return jsonify({
        "items": [
            {"id": 1, "nom": "Item 1"},
            {"id": 2, "nom": "Item 2"}
        ]
    })

# Gestion des erreurs
@app.errorhandler(429)
def ratelimit_handler(e):
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Trop de requêtes. Veuillez réessayer plus tard."
        }), 429
    return render_template('error.html', 
                         message="Trop de requêtes. Veuillez réessayer plus tard.",
                         code=429), 429

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Ressource non trouvée"}), 404
    return render_template('error.html', 
                         message="Page non trouvée",
                         code=404), 404

@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Erreur serveur"}), 500
    return render_template('error.html', 
                         message="Erreur serveur",
                         code=500), 500

if __name__ == "__main__":
    app.run(debug=False)