from flask import Flask, redirect, request, jsonify, render_template, Response
from pymongo import MongoClient
import os
from functools import wraps

app = Flask(__name__)

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

def check_auth(username, password):
    return username in admins and admins[username] == password

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ----- MongoDB Setup -----
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise Exception("MONGO_URI environment variable not set")
client = MongoClient(mongo_uri)

# Use DB_NAME environment variable if provided, otherwise default to 'telegram_redirector'
db_name = os.getenv('DB_NAME', 'telegram_redirector')
db = client[db_name]
collection = db['bots']

@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to add a new bot (JSON-based)
# (When using this API, include an "owner" field.)
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

# Updated Redirect Route for Bots with Fallback
@app.route('/<owner>/<bot_name>')
def redirect_to_bot(owner, bot_name):
    bot = collection.find_one({'bot_name': bot_name, 'owner': owner})
    if not bot:
        return render_template('404.html'), 404

    bot_username = bot['bot_username']
    
    # Construct the Telegram URL using tg:// scheme (for mobile devices with Telegram installed)
    tg_url = f"tg://resolve?domain={bot_username}"
    
    # Preserve any query parameters (e.g., start=...)
    query = request.query_string.decode('utf-8')
    if query:
        tg_url = f"{tg_url}&{query}"
    
    # Construct fallback web URL (for desktops or when tg:// fails)
    web_url = f"https://t.me/{bot_username}"
    if query:
        web_url = f"{web_url}?{query}"
    
    # Render a minimal redirect page that attempts the tg:// scheme then falls back
    return render_template('redirect.html', tg_url=tg_url, web_url=web_url)

# Admin Interface (view, add, edit, delete) - scoped to logged-in admin
@app.route('/admin', methods=['GET', 'POST'])
@requires_auth
def admin_panel():
    auth = request.authorization
    admin_username = auth.username

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

# Endpoint to delete a bot (scoped to the logged-in admin)
@app.route('/admin/delete/<bot_name>', methods=['POST'])
@requires_auth
def delete_bot(bot_name):
    auth = request.authorization
    admin_username = auth.username
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

# Endpoint to edit an existing bot (scoped to the logged-in admin)
@app.route('/admin/edit/<bot_name>', methods=['GET', 'POST'])
@requires_auth
def edit_bot(bot_name):
    auth = request.authorization
    admin_username = auth.username
    bot = collection.find_one({'bot_name': bot_name, 'owner': admin_username})
    if not bot:
        return render_template('404.html'), 404

    if request.method == 'POST':
        new_bot_username = request.form.get('bot_username')
        if not new_bot_username:
            error = "Bot username cannot be empty."
            return render_template('edit.html', bot=bot, error=error)
        collection.update_one({'bot_name': bot_name, 'owner': admin_username}, {'$set': {'bot_username': new_bot_username}})
        return redirect('/admin')
    return render_template('edit.html', bot=bot)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
