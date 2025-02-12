
---

### 4. redirector.py

```python
from flask import Flask, redirect, request, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise Exception("MONGO_URI environment variable not set")
client = MongoClient(mongo_uri)
db = client['telegram_redirector']
collection = db['bots']

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to add a new bot (JSON-based)
@app.route('/add', methods=['POST'])
def add_bot():
    data = request.get_json()
    bot_name = data.get('bot_name')
    bot_username = data.get('bot_username')

    if not bot_name or not bot_username:
        return jsonify({'error': 'Missing bot_name or bot_username'}), 400

    if collection.find_one({'bot_name': bot_name}):
        return jsonify({'error': 'Bot name already exists'}), 400

    collection.insert_one({
        'bot_name': bot_name,
        'bot_username': bot_username
    })

    custom_domain = os.getenv('CUSTOM_DOMAIN')
    if custom_domain:
        base_url = custom_domain.rstrip('/')
    else:
        base_url = request.host_url.rstrip('/')

    bot_link = f'{base_url}/{bot_name}'
    return jsonify({'message': 'Bot added successfully', 'bot_link': bot_link}), 201

# Redirect route for bots
@app.route('/<bot_name>')
def redirect_to_bot(bot_name):
    bot = collection.find_one({'bot_name': bot_name})
    if not bot:
        return render_template('404.html'), 404

    bot_username = bot['bot_username']
    telegram_url = f"https://t.me/{bot_username}"
    return render_template('redirect.html', bot_username=bot_username, telegram_url=telegram_url)

# Admin Interface to view and add bots via a web form
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        bot_name = request.form.get('bot_name')
        bot_username = request.form.get('bot_username')
        if not bot_name or not bot_username:
            error = "Missing bot name or bot username."
            bots = list(collection.find({}, {'_id': 0}))
            return render_template('admin.html', bots=bots, error=error)
        if collection.find_one({'bot_name': bot_name}):
            error = "Bot name already exists."
            bots = list(collection.find({}, {'_id': 0}))
            return render_template('admin.html', bots=bots, error=error)
        collection.insert_one({'bot_name': bot_name, 'bot_username': bot_username})
        success = "Bot added successfully!"
        bots = list(collection.find({}, {'_id': 0}))
        return render_template('admin.html', bots=bots, success=success)
    else:
        bots = list(collection.find({}, {'_id': 0}))
        return render_template('admin.html', bots=bots)

# Endpoint to delete a bot via the admin interface
@app.route('/admin/delete/<bot_name>', methods=['POST'])
def delete_bot(bot_name):
    result = collection.delete_one({'bot_name': bot_name})
    if result.deleted_count:
        success = f"Bot '{bot_name}' deleted successfully."
    else:
        success = f"Bot '{bot_name}' not found."
    bots = list(collection.find({}, {'_id': 0}))
    return render_template('admin.html', bots=bots, success=success)

# New endpoint to edit an existing bot
@app.route('/admin/edit/<bot_name>', methods=['GET', 'POST'])
def edit_bot(bot_name):
    bot = collection.find_one({'bot_name': bot_name})
    if not bot:
        return render_template('404.html'), 404

    if request.method == 'POST':
        new_bot_username = request.form.get('bot_username')
        if not new_bot_username:
            error = "Bot username cannot be empty."
            return render_template('edit.html', bot=bot, error=error)
        # Update the bot's username in MongoDB
        collection.update_one({'bot_name': bot_name}, {'$set': {'bot_username': new_bot_username}})
        return redirect('/admin')
    return render_template('edit.html', bot=bot)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
