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
            
            if "?" in self.path:
                query = self.path.split("?")[1]
                username = query.split("=")[1]
            else:
                username = ""
            if "?" in self.path:
                parts = self.path.split("?")
                if len(parts) > 1 and "=" in parts[1]:
                    username = parts[1].split("=")[1].strip()

            if not username:
                self.wfile.write(json.dumps({"success": False, "error": "Kullanıcı adı belirtilmedi"}).encode())
                return

            # Doğrudan kullanıcı adı ile ID bulma (POST isteği kullanan alternatif stabil yöntem yerine V1 API arama düzeltmesi)
            url_id = f"https://users.roblox.com/v1/usernames/users"
            payload = json.dumps({"usernames": [username], "excludeBannedUsers": True}).encode("utf-8")
            
            req = urllib.request.Request(
                url_id, 
                data=payload, 
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                },
                method='POST'
            )
            
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
