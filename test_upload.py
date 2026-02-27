
import os
import requests

# Test settings
BASE_URL = "http://localhost:8000/api/"
EMAIL = "manager@example.com"  # Replace with a valid manager email
PASSWORD = "password123"      # Replace with a valid password

def test_upload():
    # 1. Login to get token
    login_res = requests.post(f"{BASE_URL}accounts/login/", json={"email": EMAIL, "password": PASSWORD})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    
    token = login_res.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    print(f"Logged in. Token: {token[:10]}...")

    # 2. Upload a dummy image
    image_path = "test_image.png"
    with open(image_path, "wb") as f:
        f.write(os.urandom(1024)) # Dummy 1KB file
    
    with open(image_path, "rb") as f:
        files = {"profile_picture": (image_path, f, "image/png")}
        upload_res = requests.put(f"{BASE_URL}accounts/profile/update/", headers=headers, files=files)
        
    if upload_res.status_code == 200:
        print("Upload successful!")
        print(f"New Profile URL: {upload_res.json()['user'].get('profile_picture_url')}")
    else:
        print(f"Upload failed: {upload_res.status_code}")
        print(upload_res.text)
    
    if os.path.exists(image_path):
        os.remove(image_path)

if __name__ == "__main__":
    test_upload()
