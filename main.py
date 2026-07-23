from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # CORS ve Header ayarları
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            # Parametreyi al
            if "?" in self.path:
                query = self.path.split("?")[1]
                username = query.split("=")[1]
            else:
                username = "lillviqa"

            # 1. Kullanıcı ID bulma
            url_id = f"https://users.roblox.com/v1/users/search?keyword={username}&limit=1"
            req = urllib.request.Request(url_id, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if not data.get("data"):
                    self.wfile.write(json.dumps({"error": "NotFound"}).encode())
                    return
                user_id = data["data"][0]["id"]
                display_name = data["data"][0]["displayName"]
                real_name = data["data"][0]["name"]

            # 2. Takipçi Sayısı
            followers_url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
            with urllib.request.urlopen(urllib.request.Request(followers_url, headers={'User-Agent': 'Mozilla/5.0'})) as f_res:
                followers_count = json.loads(f_res.read().decode()).get("count", 0)

            # 3. Arkadaş Sayısı
            friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
            with urllib.request.urlopen(urllib.request.Request(friends_url, headers={'User-Agent': 'Mozilla/5.0'})) as fr_res:
                friends_count = json.loads(fr_res.read().decode()).get("count", 0)

            # 4. Profil Detayları
            details_url = f"https://users.roblox.com/v1/users/{user_id}"
            with urllib.request.urlopen(urllib.request.Request(details_url, headers={'User-Agent': 'Mozilla/5.0'})) as d_res:
                d_data = json.loads(d_res.read().decode())
                created_at = d_data.get("created", "")
                bio = d_data.get("description", "No bio.")

            result = {
                "success": True,
                "userId": user_id,
                "username": real_name,
                "displayName": display_name,
                "followers": followers_count,
                "friends": friends_count,
                "created": created_at[:10],
                "bio": bio
            }
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_data = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_data).encode())
