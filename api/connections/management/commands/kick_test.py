import os
import webbrowser
from flask import Flask, request, redirect
from django.core.management.base import BaseCommand
import secrets
import base64
from urllib.parse import urlencode
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.chrome.options import Options





class Command(BaseCommand):
    def handle(self, *args, **options):
        # Kick API adatok

        client_id = "01JQY0E86HFNY7749PH9SXC2QF"
        redirect_uri = "http://localhost:8000"
        scope = "user:read"
        response_type = "code"

        # OAuth URL összeállítása
        auth_url = (
            f"https://kick.com/oauth/authorize?"
            f"response_type={response_type}&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}"
        )

        # Chrome driver elindítása
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get("https://kick.com")
        print(driver.title)
        driver.quit()

        print("Jelentkezz be, majd várj, amíg átirányít az auth kóddal...")

        # Várakozás amíg átirányít (állítható idő)
        while True:
            time.sleep(1)
            if redirect_uri in driver.current_url and "code=" in driver.current_url:
                break
        
        # Kód kinyerése az URL-ből
        parsed_url = urlparse(driver.current_url)
        code = parse_qs(parsed_url.query).get("code", [None])[0]
        driver.quit()

        if code:
            print(f"\nAuthorization Code: {code}")
        else:
            print("Nem sikerült lekérni a kódot.")



#        REDIRECT_URI = "http://127.0.0.1:5000/callback"
#        SCOPES = "chat:read chat:write"  # Itt adhatsz meg más jogosultságokat
#        app = Flask(__name__)
#        @app.route("/")
#        def home():
#            """Átirányít az engedélyezési oldalra."""
#            auth_url = (
#                f"https://kick.com/oauth/authorize"
#                f"?response_type=token"
#                f"&client_id={CLIENT_ID}"
#                f"&redirect_uri={REDIRECT_URI}"
#                f"&scope={SCOPES.replace(' ', '%20')}"
#            )
#            return redirect(auth_url)
#        @app.route("/callback")
#        def callback():
#            """Itt kapjuk meg az access tokent"""
#            return """
#            <script>
#                const hashParams = new URLSearchParams(window.location.hash.substring(1));
#                const accessToken = hashParams.get("access_token");
#                if (accessToken) {
#                    document.body.innerHTML = "<h2>Access Token:</h2><p>" + accessToken + "</p>";
#                    console.log("Access Token:", accessToken);
#                } else {
#                    document.body.innerHTML = "<h2>Hiba: Token nem található!</h2>";
#                }
#            </script>
#            """
#        if __name__ == "__main__":
#            # Megnyitja az engedélyezési URL-t a böngészőben
#            webbrowser.open("http://127.0.0.1:8000/")
#            app.run(port=5000, debug=True)
