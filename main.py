import json
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        if "/user" in self.path:
            try:
                username = self.path.split("=")[1]
                
                url_id = f"https://users.roblox.com/v1/users/search?keyword={username}&limit=10"
                req = urllib.request.Request(url_id, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    if not data["data"]:
                        self.wfile.write(json.dumps({"error": "NotFound"}).encode())
                        return
                    user_id = data["data"][0]["id"]
                    display_name = data["data"][0]["displayName"]
                    real_name = data["data"][0]["name"]

                followers_url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
                with urllib.request.urlopen(urllib.request.Request(followers_url, headers={'User-Agent': 'Mozilla/5.0'})) as f_res:
                    followers_count = json.loads(f_res.read().decode()).get("count", 0)

                friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
                with urllib.request.urlopen(urllib.request.Request(friends_url, headers={'User-Agent': 'Mozilla/5.0'})) as fr_res:
                    friends_count = json.loads(fr_res.read().decode()).get("count", 0)

                details_url = f"https://users.roblox.com/v1/users/{user_id}"
                with urllib.request.urlopen(urllib.request.Request(details_url, headers={'User-Agent': 'Mozilla/5.0'})) as d_res:
                    d_data = json.loads(d_res.read().decode())
                    created_at = d_data.get("created", "")
                    bio = d_data.get("description", "No bio available.")

                result = {
                    "success": True,
                    "userId": user_id,
                    "username": real_name,
                    "displayName": display_name,
                    "followers": followers_count,
                    "friends": friends_count,
                    "created": created_at[:10],
                    "bio": bio if bio != "" else "Empty bio."
                }
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.wfile.write(json.dumps({"error": "Invalid endpoint"}).encode())
