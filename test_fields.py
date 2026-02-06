import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api/accounts'

def test_registration_with_fields():
    print("Test Registering Employee with Profile Fields...")
    data = {
        'username': 'new_employee_v2',
        'password': 'password123',
        'role': 'EMPLOYEE',
        'email': 'newemp@test.com',
        'department': 'Engineering',
        'designation': 'Software Engineer',
        'blood_group': 'O+',
        'mobile_number': '1234567890'
    }
    
    try:
        res = requests.post(f'{BASE_URL}/register/', json=data)
        print("Register Status:", res.status_code)
        print("Response:", res.text)
        
        if res.status_code == 201:
            print("Successfully registered with new fields!")
    except Exception as e:
        print("Failed to connect:", e)

if __name__ == '__main__':
    test_registration_with_fields()
