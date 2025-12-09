from flask import Flask, render_template_string, redirect, request, session, url_for
from flask_session import Session
import msal
import os
from functools import wraps

# -----------------------------------------------------------------------------
# FLASK CONFIGURATION
# -----------------------------------------------------------------------------
app = Flask(__name__)

# Clé secrète (obligatoire en production)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuration session pour Azure HTTPS
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
Session(app)

# -----------------------------------------------------------------------------
# AZURE AD CONFIGURATION
# -----------------------------------------------------------------------------
AZURE_CONFIG = {
    'client_id': os.getenv('AZURE_CLIENT_ID'),
    'client_secret': os.getenv('AZURE_CLIENT_SECRET'),
    'authority': f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}",
    'redirect_uri': os.getenv('REDIRECT_URI'),
    'scope': ['User.Read']
}

# -----------------------------------------------------------------------------
# MSAL CLIENT
# -----------------------------------------------------------------------------
def get_msal_app():
    return msal.ConfidentialClientApplication(
        AZURE_CONFIG['client_id'],
        authority=AZURE_CONFIG['authority'],
        client_credential=AZURE_CONFIG['client_secret']
    )

# -----------------------------------------------------------------------------
# LOGIN DECORATOR
# -----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------------------------------------------------------
# HTML TEMPLATES
# -----------------------------------------------------------------------------
LOGIN_PAGE = """..."""
DASHBOARD_PAGE = """..."""
# ⚠️ IMPORTANT
# gardez exactement vos templates actuels ici (je ne les enlève pas, juste raccourcis l'affichage)

# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('dashboard' if session.get('user') else 'login'))

@app.route('/login')
def login():
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=AZURE_CONFIG['scope'],
        redirect_uri=AZURE_CONFIG['redirect_uri']
    )
    return render_template_string(LOGIN_PAGE, auth_url=auth_url)

@app.route('/getAToken')
def get_token():
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
        return f"Erreur Azure AD: {result.get('error_description')}"

    session['user'] = result.get('id_token_claims')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(
        DASHBOARD_PAGE,
        user=session.get('user'),
        logout_url=url_for('logout')
    )

@app.route('/logout')
def logout():
    session.clear()
    logout_url = f"{AZURE_CONFIG['authority']}/oauth2/v2.0/logout"
    return redirect(logout_url)

# -----------------------------------------------------------------------------
# APPLICATION STARTUP
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    required = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'REDIRECT_URI', 'SECRET_KEY']
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        print("❌ VARIABLES MANQUANTES :", missing)
    else:
        print("✅ Configuration Azure AD OK")

    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
