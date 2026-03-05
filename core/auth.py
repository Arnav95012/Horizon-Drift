import requests
import minecraft_launcher_lib
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import threading
import webbrowser

def authenticate_elyby(username, password):
    url = "https://authserver.ely.by/auth/authenticate"
    payload = {
        "agent": {"name": "Minecraft", "version": 1},
        "username": username,
        "password": password,
        "requestUser": True
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        return {
            "type": "elyby",
            "username": data["selectedProfile"]["name"],
            "uuid": data["selectedProfile"]["id"],
            "token": data["accessToken"]
        }
    else:
        raise Exception(resp.json().get("errorMessage", "Authentication failed"))

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h2>Authentication successful! You can close this window.</h2><script>window.close();</script></body></html>")
        
        # Extract code
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        if 'code' in query:
            self.server.auth_code = query['code'][0]
        
    def log_message(self, format, *args):
        pass # Suppress logging

def authenticate_microsoft():
    CLIENT_ID = "00000000402b5328" # Common Minecraft Launcher Client ID
    REDIRECT_URI = "http://localhost:8080/callback"
    
    login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URI)
    
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server.auth_code = None
    
    webbrowser.open(login_url)
    
    # Wait for one request
    server.handle_request()
    
    if not server.auth_code:
        raise Exception("Failed to get authorization code")
        
    auth_data = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URI, server.auth_code, code_verifier)
    
    return {
        "type": "microsoft",
        "username": auth_data["name"],
        "uuid": auth_data["id"],
        "token": auth_data["access_token"],
        "refresh_token": auth_data.get("refresh_token", "")
    }

