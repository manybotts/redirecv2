
---

### 4. redirector.py

```python
from flask import Flask, redirect, request, jsonify, render_template, session, url_for, flash
from pymongo import MongoClient
import os
from functools import wraps

app = Flask(__name__)

# Set secret key for session management (use a secure value in production)
app.secret_key = os.getenv('SECRET_KEY', 'defaultsecretkey')

# ----- Multi-Admin Setup -----
# Expected format for ADMINS env var: "alice:secret1,bob:secret2"
admins_env = os.getenv('ADMINS', '')
admins = {}
if admins_env:
    for pair in admins_env.split(','):
        parts = pair.split(':')
        if len(parts) == 2:
            username, password = parts[0].strip(), parts[1].strip()
            admins[username] = password

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash("Please log in to access the admin panel.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----- MongoDB Setup -----
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise Exception("MONGO_URI environment variable not set")
client = MongoClient(mongo_uri)
db = client['telegram_redirector']
collection = db['bots']

@app.route('/')
def index():
    return render_template('index.html')

# ----- Custom Login & Logout Routes -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in admins and admins[username] == password:
            session['admin'] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for('admin_panel'))
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

# ----- API Endpoint for Adding Bots (JSON-based) -----
@app.route('/add', methods=['POST'])
def add_bot():
    data = request.get_json()
    bot_name = data.get('bot_name')
    bot_username = data.get('bot_username')
    owner = data.get('owner')
    if not bot_name or not bot_username or not owner:
        return jsonify({'error': 'Missing bot_name, bot_username, or owner'}), 400

    # Check uniqueness per owner
    if collection.find_one({'bot_name': bot_name, 'owner': owner}):
        return jsonify({'error': 'Bot name already exists for this owner'}), 400

    collection.insert_one({
        'bot_name': bot_name,
        'bot_username': bot_username,
        'owner': owner
    })

    custom_domain = os.getenv('CUSTOM_DOMAIN')
    if custom_domain:
        base_url = custom_domain.rstrip('/')
    else:
        base_url = request.host_url.rstrip('/')

    bot_link = f'{base_url}/{owner}/{bot_name}'
    return jsonify({'message': 'Bot added successfully', 'bot_link': bot_link}), 201

# ----- Redirect Route for Bots (includes owner) -----
@app.route('/<owner>/<bot_name>')
def redirect_to_bot(owner, bot_name):
    bot = collection.find_one({'bot_name': bot_name, 'owner': owner})
    if not bot:
        return render_template('404.html'), 404

    bot_username = bot['bot_username']
    # Construct the Telegram URL
    telegram_url = f"https://t.me/{bot_username}"
    query = request.query_string.decode('utf-8')
    if query:
        telegram_url = f"{telegram_url}?{query}"
    return render_template('redirect.html', bot_username=bot_username, telegram_url=telegram_url)

# ----- Admin Interface (view, add, edit, delete) -----
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    admin_username = session['admin']
    custom_domain = os.getenv('CUSTOM_DOMAIN')
    if custom_domain:
        base_url = custom_domain.rstrip('/')
    else:
        base_url = request.host_url.rstrip('/')

    if request.method == 'POST':
        bot_name = request.form.get('bot_name')
        bot_username = request.form.get('bot_username')
        if not bot_name or not bot_username:
            error = "Missing bot name or bot username."
            bots = list(collection.find({'owner': admin_username}, {'_id': 0}))
            return render_template('admin.html', bots=bots, error=error, base_url=base_url, admin_username=admin_username)
        if collection.find_one({'bot_name': bot_name, 'owner': admin_username}):
            error = "Bot name already exists for your account."
            bots = list(collection.find({'owner': admin_username}, {'_id': 0}))
            return render_template('admin.html', bots=bots, error=error, base_url=base_url, admin_username=admin_username)
        collection.insert_one({'bot_name': bot_name, 'bot_username': bot_username, 'owner': admin_username})
        success = "Bot added successfully!"
        bots = list(collection.find({'owner': admin_username}, {'_id': 0}))
        return render_template('admin.html', bots=bots, success=success, base_url=base_url, admin_username=admin_username)
    else:
        bots = list(collection.find({'owner': admin_username}, {'_id': 0}))
        return render_template('admin.html', bots=bots, base_url=base_url, admin_username=admin_username)

@app.route('/admin/delete/<bot_name>', methods=['POST'])
@login_required
def delete_bot(bot_name):
    admin_username = session['admin']
    result = collection.delete_one({'bot_name': bot_name, 'owner': admin_username})
    if result.deleted_count:
        success = f"Bot '{bot_name}' deleted successfully."
    else:
        success = f"Bot '{bot_name}' not found."
    custom_domain = os.getenv('CUSTOM_DOMAIN')
    if custom_domain:
        base_url = custom_domain.rstrip('/')
    else:
        base_url = request.host_url.rstrip('/')
    bots = list(collection.find({'owner': admin_username}, {'_id': 0}))
    return render_template('admin.html', bots=bots, success=success, base_url=base_url, admin_username=admin_username)

@app.route('/admin/edit/<bot_name>', methods=['GET', 'POST'])
@login_required
def edit_bot(bot_name):
    admin_username = session['admin']
    bot = collection.find_one({'bot_name': bot_name, 'owner': admin_username})
    if not bot:
        return render_template('404.html'), 404

    if request.method == 'POST':
        new_bot_username = request.form.get('bot_username')
        if not new_bot_username:
            error = "Bot username cannot be empty."
            return render_template('edit.html', bot=bot, error=error)
        collection.update_one({'bot_name': bot_name, 'owner': admin_username}, {'$set': {'bot_username': new_bot_username}})
        return redirect(url_for('admin_panel'))
    return render_template('edit.html', bot=bot)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
