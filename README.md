# Telegram Bot Redirector

A simple, high‑performance web application that dynamically redirects users to multiple Telegram bots.  
Designed for easy deployment on [Heroku](https://heroku.com), [Railway](https://railway.app), and [Koyeb](https://koyeb.com) – with an option to use your own custom domain.

## Features

- **High‑Performance Redirects:** Capable of handling 100–200 redirects per minute.
- **Multi‑Bot Support:** Each admin can add and manage their own bots independently.
- **Custom Domain Option:** Set `CUSTOM_DOMAIN` (e.g., `https://www.yourcustomdomain.com`) to override the default host.
- **Multi‑Admin Security:** Admin access is protected via HTTP Basic Authentication. Configure multiple admins using the `ADMINS` environment variable.
- **User-Friendly Admin Interface:** Easily add, edit, and delete bots; each bot displays its generated link with an easy "Copy" button.
- **Flexible Deployment:** Deploy effortlessly on Heroku, Railway, Koyeb, or any container‑based platform.

## One‑Click Deploy

- **Heroku:**  
  [![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/manybotts/redirecv2)
- **Railway:**  
  [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template?referralCode=YOUR_RAILWAY_REFERRAL_CODE)
- **Koyeb:**  
  [![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=redirecv2&repository=manybotts%2Fredirecv2&branch=main&builder=dockerfile&instance_type=free&env%5BDB_NAME%5D=hybrid&env%5BMONGO_URI%5D=mongodb%2Bsrv%3A%2F%2Fibox%3A1111%40cluster0.hpl8s.mongodb.net%2F%3FretryWrites%3Dtrue%26w%3Dmajority%26appName%3DCluster0&env%5BPORT%5D=8080&ports=5000%3Bhttp%3B%2F&hc_protocol%5B5000%5D=tcp&hc_grace_period%5B5000%5D=5&hc_interval%5B5000%5D=30&hc_restart_limit%5B5000%5D=3&hc_timeout%5B5000%5D=5&hc_path%5B5000%5D=%2F&hc_method%5B5000%5D=get)

> **Note:** Replace any environment values (such as `MONGO_URI` or `YOUR_RAILWAY_REFERRAL_CODE`) as needed.

## Project Structure

## Environment Variables

Before deploying, set the following:

- **MONGO_URI**: Your MongoDB connection string.
- **DB_NAME** (optional): Your database name (defaults to `telegram_redirector` if not set).
- **CUSTOM_DOMAIN** (optional): Your custom domain (e.g., `https://www.yourcustomdomain.com`).  
  If not set, the app uses the incoming request’s host.
- **ADMINS**: A comma‑separated list of admin credentials in the format `username:password` (e.g., `alice:secret1,bob:secret2`).

## Getting Started Locally

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/manybotts/redirecv2.git
   cd redirecv2
