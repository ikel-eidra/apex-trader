# 🚀 APEX TRADER - Deployment Guide

Your Apex Trader bot has been upgraded with **Advanced Intelligence**, **Dynamic Risk Management**, and a **Cyberpunk Dashboard**. Follow these steps to deploy it.

## 1. Backend Deployment (Railway)

The backend runs the Trading Bot and the API Server.

1.  **Push to GitHub**:
    -   Commit all changes in `apex-trader` to your GitHub repository.
    ```bash
    git add .
    git commit -m "Upgrade: Async Engine + Cyberpunk Dashboard"
    git push origin main
    ```

2.  **Deploy on Railway**:
    -   Go to [Railway.app](https://railway.app).
    -   Create a **New Project** -> **Deploy from GitHub repo**.
    -   Select your `apex-trader` repository.
    -   **Variables**: Add the following environment variables in Railway:
        -   `BINANCE_API_KEY`: Your Binance API Key.
        -   `BINANCE_API_SECRET`: Your Binance Secret.
        -   `BINANCE_TESTNET`: `True` (for testing) or `False` (for real money).
        -   `DRY_RUN`: `True` (simulated trading) or `False` (real trading).
        -   `API_PORT`: `8000` (or let Railway assign `PORT`).
    -   **Start Command**: Railway should automatically detect `Procfile` or `python main.py`. If not, set the Start Command to:
        ```bash
        python main.py
        ```

3.  **Get Backend URL**:
    -   Once deployed, Railway will give you a public URL (e.g., `https://apex-trader-production.up.railway.app`).
    -   **Copy this URL**. You need it for the dashboard.

## 2. Frontend Deployment (cPanel / Stellar)

The dashboard is a static React app that connects to your Railway backend.

1.  **Configure API URL**:
    -   Open `dashboard/public/config.js`.
    -   Update `window.APEX_API_URL` to your **Railway Backend URL** (from step 1).
    ```javascript
    window.APEX_API_URL = "https://apex-trader-production.up.railway.app";
    ```
    *(Note: You can also edit this file directly on cPanel after uploading if you want to change it later without rebuilding).*

2.  **Build the Dashboard** (Already done locally, but if you changed config):
    ```bash
    cd dashboard
    npm run build
    ```
    -   This creates a `dist` folder.

3.  **Upload to cPanel**:
    -   Go to your **cPanel File Manager**.
    -   Navigate to `public_html` (or a subdomain folder like `apex.futoltech.com`).
    -   **Upload** the contents of the `dashboard/dist` folder.
    -   Ensure `index.html`, `assets/`, and `config.js` are in the root of your domain folder.

## 3. Verification

1.  **Open your Dashboard URL** (e.g., `apex.futoltech.com`).
2.  Check the **System Status** card. It should say **RUNNING**.
3.  Check the **Market Overview** chart. It should load data.
4.  **Test Control**: Click "Emergency Stop" to test API connectivity.

## ⚠️ Important Notes

-   **Dry Run Mode**: The bot is set to `DRY_RUN = True` by default in `config.py`. Change this to `False` in your Railway variables only when you are ready to lose real money.
-   **Risk Management**: The new bot uses **ATR-based stops**. This means stops are dynamic. Watch the logs to see where it places them.
-   **Async Speed**: The scanner is FAST. It scans 100 coins in ~2 seconds. Ensure your Binance API limits allow this (standard accounts are fine).

**Good luck, Mahal ko! 🚀💙**
