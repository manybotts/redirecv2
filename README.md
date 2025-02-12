# redirecv2

# Telegram Bot Redirector

A simple, high‑performance web application that dynamically redirects users to multiple Telegram bots.  
Designed for easy deployment on [Heroku](https://heroku.com), [Railway](https://railway.app), and [Koyeb](https://koyeb.com) – with an option to use your own custom domain.

## Features

- **High‑Performance Redirects:** Capable of handling 100–200 redirects per minute.
- **Multi‑Bot Support:** Add and manage multiple Telegram bot redirects.
- **Custom Domain Option:** Set `CUSTOM_DOMAIN` (e.g., `https://www.yourcustomdomain.com`) to override the default host.
- **User-Friendly Admin Interface:** Manage bots (view, add, edit, delete) directly via your browser.
- **Flexible Deployment:** Deploy effortlessly on Heroku, Railway, or any container‑based platform like Koyeb.

## One‑Click Deploy

Deploy with just a click on your preferred platform:

- [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/manybotts/redirecv2)
- [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template?repository=https://github.com/manybotts/redirecv2&referralCode=YOUR_RAILWAY_REFERRAL_CODE)
- [![Deploy on Koyeb](https://www.koyeb.com/static/images/deploy-on-koyeb.svg)](https://app.koyeb.com/new?repository=https://github.com/manybotts/redirecv2)

> **Note:** Replace `YOUR_RAILWAY_REFERRAL_CODE` with your actual referral code if applicable.

## Project Structure




. ├── Procfile ├── Dockerfile ├── README.md ├── redirector.py ├── requirements.txt ├── runtime.txt └── templates ├── index.html ├── admin.html ├── edit.html ├── redirect.html └── 404.html


## Environment Variables

Before deploying, make sure to set the following:

- **MONGO_URI**: Your MongoDB connection string.
- **CUSTOM_DOMAIN** (optional): Your custom domain (e.g., `https://www.yourcustomdomain.com`).  
  If not set, the app will use the incoming request’s host.

## Getting Started Locally

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
Create a Virtual Environment & Install Dependencies:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
Set Environment Variables:

You can create a .env file or set variables in your shell:

bash
Copy
export MONGO_URI="your_mongodb_connection_string"
export CUSTOM_DOMAIN="https://www.yourcustomdomain.com"  # Optional
Run the Application:

bash
Copy
python redirector.py
The app will run at http://localhost:5000.

Deployment Instructions
Deploy on Heroku
Create & Configure Your Heroku App:
  heroku create your-app-name
heroku config:set MONGO_URI="your_mongodb_connection_string"
heroku config:set CUSTOM_DOMAIN="https://www.yourcustomdomain.com"  # Optional
git push heroku main

Add Your Custom Domain (Optional):

Log in to your Heroku dashboard.
Go to your app’s Settings.
Under the Domains and certificates section, click "Add domain".
Enter your custom domain (e.g., www.yourcustomdomain.com) and save it.
Heroku will provide you with a DNS target (e.g., your-app-name.herokuapp.com or a custom endpoint).
Configure DNS on spaceship.com:

Log in to your spaceship.com account and access your DNS management.
Create a CNAME record for the subdomain (e.g., www) pointing to the Heroku DNS target.
If using an apex domain (like yourcustomdomain.com), consider using an ALIAS/ANAME record if supported or use a service with CNAME flattening (e.g., Cloudflare).
SSL/TLS:
Heroku automatically manages SSL certificates (with Automated Certificate Management on paid plans).

Deploy on Railway
Deploy on Railway:

Click the "Deploy on Railway" button above.
Connect your GitHub repository.
Set the environment variables (MONGO_URI and optionally CUSTOM_DOMAIN) in the Railway dashboard.
Deploy the project.
Add Your Custom Domain (Optional):

In the Railway dashboard, navigate to the Domains section.
Click "Add Domain" and enter your custom domain (e.g., www.yourcustomdomain.com).
Railway will provide the required DNS records (either CNAME or A records).
Configure DNS on spaceship.com:

In your spaceship.com DNS panel, add the provided DNS records.
For a CNAME record, point your subdomain (e.g., www) to the Railway target.
Adjust TTL settings as needed for quick propagation.
SSL/TLS:
Railway typically provisions SSL certificates automatically for custom domains.

Deploy on Koyeb
Deploy on Koyeb:

Click the "Deploy on Koyeb" button above.
Connect your GitHub account and select the repository.
Set the environment variables (MONGO_URI and optionally CUSTOM_DOMAIN) in the Koyeb dashboard.
Deploy the project.
Add Your Custom Domain (Optional):

Log in to your Koyeb dashboard.
Go to your project settings and select the Domains tab.
Click "Add Domain" and enter your custom domain (e.g., www.yourcustomdomain.com).
Koyeb will display the required DNS records, usually a CNAME record pointing to a Koyeb endpoint.
Configure DNS on spaceship.com:

In your spaceship.com DNS management, create a CNAME record for your subdomain (e.g., www) that points to the provided Koyeb endpoint.
For apex domains, use ALIAS/ANAME records or a service that supports CNAME flattening.
SSL/TLS:
Koyeb automatically provisions SSL certificates for added custom domains.

Custom Domain Integration Summary
In your application, the environment variable CUSTOM_DOMAIN determines the base URL used when generating bot links. Make sure to:

Set CUSTOM_DOMAIN to your custom domain URL (e.g., https://www.yourcustomdomain.com) in your deployment platform’s environment settings.
Follow the DNS configuration instructions on spaceship.com to point your custom domain (or subdomain) to your deployment target.
Allow time for DNS propagation (this can range from a few minutes to several hours).
Admin Interface
For a user-friendly way to add and manage bots, an admin interface is provided.
Visit https://www.yourcustomdomain.com/admin (or http://localhost:5000/admin when running locally) to:

View the list of existing bots.
Add a new bot using a simple form.
Edit an existing bot to update its username.
Delete bots with a click of a button.
No additional configuration is required. All bot data is stored in your MongoDB database.

API Endpoints
Add a New Bot (API)
Alternatively, you can add a new bot by sending a POST request to /add with a JSON payload:

json
Copy
{
  "bot_name": "your_bot_name",
  "bot_username": "your_bot_username"
}
Response:

json
Copy
{
  "message": "Bot added successfully",
  "bot_link": "https://www.yourcustomdomain.com/your_bot_name"
}
Redirect to a Bot
Visit https://www.yourcustomdomain.com/your_bot_name in your browser.
The app will redirect you (after a brief pause) to the corresponding Telegram bot at https://t.me/your_bot_username.
