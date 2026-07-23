from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            username = ""
            if "?" in self.path:
                parts = self.path.split("?")
                for part in parts:
                    if part.startswith("username="):
                        username = part.split("=")[1].strip()

            if not username:
                self.wfile.write(json.dumps({"success": False, "error": "Kullanıcı adı belirtilmedi"}).encode())
                return

            # 1. Klasik ve stabil V1 Arama Endpoint'i
            url_id = f"https://users.roblox.com/v1/users/search?keyword={username}&limit=1"
            req = urllib.request.Request(url_id, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if not data.get("data") or len(data["data"]) == 0:
                    self.wfile.write(json.dumps({"success": False, "error": "Kullanıcı bulunamadı"}).encode())
                    return
                
                user_id = data["data"][0]["id"]
                real_name = data["data"][0]["name"]
                display_name = data["data"][0]["displayName"]

            # 2. Takipçi Sayısı
            followers_count = 0
            try:
                followers_url = f"https://friends.roblox.com/v1/users/{user_id}/followers/count"
                with urllib.request.urlopen(urllib.request.Request(followers_url, headers={'User-Agent': 'Mozilla/5.0'})) as f_res:
                    followers_count = json.loads(f_res.read().decode()).get("count", 0)
            except:
                pass

            # 3. Arkadaş Sayısı
            friends_count = 0
            try:
                friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends/count"
                with urllib.request.urlopen(urllib.request.Request(friends_url, headers={'User-Agent': 'Mozilla/5.0'})) as fr_res:
                    friends_count = json.loads(fr_res.read().decode()).get("count", 0)
            except:
                pass

            # 4. Profil Detayları
            created_at = ""
            bio = "No bio."
            try:
                details_url = f"https://users.roblox.com/v1/users/{user_id}"
                with urllib.request.urlopen(urllib.request.Request(details_url, headers={'User-Agent': 'Mozilla/5.0'})) as d_res:
                    d_data = json.loads(d_res.read().decode())
                    created_at = d_data.get("created", "")
                    bio = d_data.get("description", "No bio.")
            except:
                pass

            result = {
                "success": True,
                "userId": user_id,
                "username": real_name,
                "displayName": display_name,
                "followers": followers_count,
                "friends": friends_count,
                "created": created_at[:10] if created_at else "",
                "bio": bio if bio else "Empty bio."
            }
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_data = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_data).encode())
