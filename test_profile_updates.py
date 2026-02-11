#!/usr/bin/env python
"""
Test Profile Update with different field combinations
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ems_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()

def create_test_image():
    """Create a simple test PNG image"""
    image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return SimpleUploadedFile(
        "test_profile.png",
        image_content,
        content_type="image/png"
    )

def test_profile_updates():
    """Test various profile update scenarios"""
    client = APIClient()
    
    print("\n" + "="*70)
    print("PROFILE UPDATE TESTS")
    print("="*70)
    
    # Clean up
    User.objects.filter(username='profile_test_user').delete()
    
    # Register test user
    print("\n[Setup] Creating test user...")
    response = client.post('/api/accounts/register/', {
        'username': 'profile_test_user',
        'email': 'profiletest@example.com',
        'password': 'TestPassword123!',
        'role': 'MANAGER',
        'blood_group': 'A+',
        'mobile_number': '1234567890'
    })
    
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.json()}")
        return False
    
    print("✅ User created")
    
    # Login
    print("\n[Setup] Logging in...")
    response = client.post('/api/accounts/login/', {
        'email': 'profiletest@example.com',
        'password': 'TestPassword123!'
    })
    
    token = response.json().get('token')
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    print("✅ Logged in")
    
    # Test 1: Update only mobile number
    print("\n[Test 1] Update mobile number only...")
    response = client.patch('/api/accounts/profile/update/', {
        'mobile_number': '9876543210'
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Mobile: {user_data.get('mobile_number')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 2: Update blood group
    print("\n[Test 2] Update blood group...")
    response = client.patch('/api/accounts/profile/update/', {
        'blood_group': 'B+'
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Blood Group: {user_data.get('blood_group')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 3: Update both mobile and blood group
    print("\n[Test 3] Update mobile and blood group together...")
    response = client.patch('/api/accounts/profile/update/', {
        'mobile_number': '5555555555',
        'blood_group': 'O+'
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Mobile: {user_data.get('mobile_number')}")
        print(f"   Blood Group: {user_data.get('blood_group')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 4: Upload profile picture alone
    print("\n[Test 4] Upload profile picture...")
    image_file = create_test_image()
    response = client.patch('/api/accounts/profile/update/', {
        'profile_picture': image_file
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Profile Picture URL: {user_data.get('profile_picture_url')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 5: Upload picture + update other fields
    print("\n[Test 5] Upload picture and update mobile...")
    image_file = create_test_image()
    response = client.patch('/api/accounts/profile/update/', {
        'profile_picture': image_file,
        'mobile_number': '1111111111'
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Mobile: {user_data.get('mobile_number')}")
        print(f"   Profile Picture URL: {user_data.get('profile_picture_url')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 6: Clear blood group (set to None)
    print("\n[Test 6] Clear blood group...")
    response = client.patch('/api/accounts/profile/update/', {
        'blood_group': ''
    }, format='multipart')
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json().get('message')}")
        user_data = response.json().get('user', {})
        print(f"   Blood Group: {user_data.get('blood_group')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    # Test 7: Get final profile state
    print("\n[Test 7] Retrieve final profile state...")
    response = client.get('/api/accounts/me/')
    
    if response.status_code == 200:
        print(f"✅ Success")
        user_data = response.json()
        print(f"   Username: {user_data.get('username')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Mobile: {user_data.get('mobile_number')}")
        print(f"   Blood Group: {user_data.get('blood_group')}")
        print(f"   Profile Picture: {user_data.get('profile_picture')}")
    else:
        print(f"❌ Failed ({response.status_code}): {response.json()}")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL PROFILE UPDATE TESTS PASSED!")
    print("="*70)
    return True

if __name__ == '__main__':
    try:
        success = test_profile_updates()
        import sys
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
