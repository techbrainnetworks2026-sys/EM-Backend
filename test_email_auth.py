import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api/accounts'

def test_email_login_flow():
    # 1. Register Employee with unique details
    print("1. Registering Employee...")
    email_user = "email_user_1@test.com"
    password = "password123"
    
    data = {
        'username': 'email_user_1',
        'password': password,
        'role': 'EMPLOYEE',
        'email': email_user,
        'department': 'Sales',
        'designation': 'Sales Person',
        'blood_group': 'B+',
        'mobile_number': '1112223334'
    }
    
    try:
        res = requests.post(f'{BASE_URL}/register/', json=data)
        print("Register Status:", res.status_code)
        if res.status_code != 201:
            print("Response:", res.text)
            # If default user exists from previous run, we might get error, but we want to test login anyway
    except Exception as e:
        print("Failed to connect:", e)
        return

    # 2. Login with EMAIL (not username) - Should Fail first (Not Approved)
    print("\n2. Logging in with EMAIL (Should Fail - Not Approved)...")
    login_data = {
        'email': email_user, 
        'password': password
    }
    res = requests.post(f'{BASE_URL}/login/', json=login_data)
    print("Login Status (Expect 403):", res.status_code)
    print("Response:", res.text)

    # 3. Approve the user (Login as manager first)
    # We need a manager. Let's register one.
    manager_email = 'manager_email@test.com'
    manager_data = {
        'username': 'manager_email',
        'password': password,
        'role': 'MANAGER',
        'email': manager_email
    }
    requests.post(f'{BASE_URL}/register/', json=manager_data)
    
    # Login Manager
    print("\n3. Login Manager (with Email)...")
    res = requests.post(f'{BASE_URL}/login/', json={'email': manager_email, 'password': password})
    if res.status_code == 200:
        manager_token = res.json().get('token')
        print("Manager logged in.")
        
        # Approve Employee
        # First get ID of pending user
        headers = {'Authorization': f'Token {manager_token}'}
        pending_res = requests.get(f'{BASE_URL}/manager/pending-users/', headers=headers)
        pending = pending_res.json()
        
        target_id = None
        for u in pending:
            if u['email'] == email_user:
                target_id = u['id']
                break
        
        if target_id:
            print(f"Approving user {target_id}...")
            requests.post(f'{BASE_URL}/manager/approve-user/{target_id}/', headers=headers)
        else:
            print("Target user not found in pending list (maybe already approved?)")

    # 4. Login with EMAIL (Should Succeed)
    print("\n4. Logging in with EMAIL (Should Succeed)...")
    res = requests.post(f'{BASE_URL}/login/', json=login_data)
    print("Login Status (Expect 200):", res.status_code)
    if res.status_code == 200:
        print("Success! Token:", res.json().get('token'))
    else:
         print("Failed:", res.text)

if __name__ == '__main__':
    test_email_login_flow()
