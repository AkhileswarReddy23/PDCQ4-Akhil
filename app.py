from flask import Flask, redirect, url_for, session, render_template, request
from datetime import datetime
from authlib.integrations.flask_client import OAuth
import pytz

app = Flask(__name__)
app.secret_key = 'abcdefgh123456'
app.config['GOOGLE_CLIENT_ID'] = '716598335852-0ahk2u4ret2sbr8017teegf60v0tn2m0.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['GOOGLE_DISCOVERY_URL'] = 'https://accounts.google.com/.well-known/openid-configuration'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid email profile',
    }
)

@app.route('/')
def index():
    if 'user' in session:
        user_data = session['user']
        name = user_data['name']
        email = user_data['email']
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        return render_template('welcome.html', name=name, email=email, current_time=current_time)
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def authorize_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        session['user'] = {
            'name': user_info['name'],
            'email': user_info['email']
        }
    else:
        # Fallback: fetch user info from Google API
        user_info = google.get('userinfo').json()
        session['user'] = {
            'name': user_info.get('name'),
            'email': user_info.get('email')
        }
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

def generate_design_pattern(n):
    """
    Generate a recursive design pattern based on the number of lines.
    Pattern: recursively breaks down the word "FORMULATIONS" by showing
    the word, then a connector line, then continuing recursively with the middle.
    """
    word = "FORMULAQSOLUTIONS"
    lines = []
    
    def recursive_pattern(text):
        """Recursively generate the pattern"""
        if len(lines) >= n or not text:
            return
        
        # Base case: single character
        if len(text) == 1:
            lines.append(text)
            return
        
        # Show the text
        lines.append(text)
        if len(lines) >= n:
            return
        
        # Show connector between first and last character
        first = text[0]
        last = text[-1]
        middle_length = len(text) - 2
        
        if middle_length >= 0:
            if middle_length == 0:
                connector = first + last
            else:
                connector = first + "-" * middle_length + last
            lines.append(connector)
            if len(lines) >= n:
                return
            
            # Extract middle and recurse
            middle = text[1:-1]
            if middle:
                recursive_pattern(middle)
    
    recursive_pattern(word)
    return '\n'.join(lines[:n])

@app.route('/generate-design', methods=['POST'])
def generate_design():
    try:
        data = request.get_json()
        lines = data.get('lines', 0)
        
        # Validate input
        if not isinstance(lines, int) or lines < 1 or lines > 100:
            return {'error': 'Invalid input. Lines must be between 1 and 100'}, 400
        
        design = generate_design_pattern(lines)
        return {'design': design}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
