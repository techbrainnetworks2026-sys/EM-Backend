#!/usr/bin/env python
"""
Test script to verify profile picture upload and retrieval functionality
Run this after starting the Django server
"""
import os
import sys
import django

# Setup Django
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

def test_profile_picture_complete():
    """Complete test of profile picture functionality"""
    client = APIClient()
    
    print("\n" + "="*60)
    print("PROFILE PICTURE UPLOAD TEST")
    print("="*60)
    
    # Clean up any previous test data
    User.objects.filter(username='test_profile_user').delete()
    
    # Step 1: Register user
    print("\n[1] Creating test user...")
    response = client.post('/api/accounts/register/', {
        'username': 'test_profile_user',
        'email': 'testprofile@example.com',
        'password': 'TestPassword123!',
        'role': 'MANAGER'
    })
    
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.json()}")
        return False
    
    print("✅ User registered successfully")
    user = User.objects.get(username='test_profile_user')
    token, _ = Token.objects.get_or_create(user=user)
    
    # Step 2: Login
    print("\n[2] Logging in user...")
    response = client.post('/api/accounts/login/', {
        'email': 'testprofile@example.com',
        'password': 'TestPassword123!'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        return False
    
    token_key = response.json().get('token')
    print(f"✅ Login successful, Token: {token_key[:20]}...")
    
    # Step 3: Get initial profile
    print("\n[3] Fetching initial profile...")
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_key}')
    response = client.get('/api/accounts/me/')
    
    if response.status_code != 200:
        print(f"❌ Failed to get profile: {response.json()}")
        return False
    
    initial_data = response.json()
    print(f"✅ Initial profile retrieved")
    print(f"   - Username: {initial_data.get('username')}")
    print(f"   - Email: {initial_data.get('email')}")
    print(f"   - Profile Picture: {initial_data.get('profile_picture')}")
    print(f"   - Profile Picture URL: {initial_data.get('profile_picture_url')}")
    
    # Step 4: Upload profile picture
    print("\n[4] Uploading profile picture...")
    image_file = create_test_image()
    
    response = client.patch('/api/accounts/profile/update/', {
        'profile_picture': image_file,
        'blood_group': 'AB+',
        'mobile_number': '9876543210'
    }, format='multipart')
    
    if response.status_code != 200:
        print(f"❌ Profile update failed: {response.json()}")
        return False
    
    updated_data = response.json()
    print(f"✅ Profile picture uploaded successfully")
    print(f"   - Message: {updated_data.get('message')}")
    
    user_data = updated_data.get('user', {})
    profile_file = user_data.get('profile_picture')
    profile_url = user_data.get('profile_picture_url')
    
    print(f"   - Profile Picture File: {profile_file}")
    print(f"   - Profile Picture URL: {profile_url}")
    
    if not profile_file or not profile_url:
        print("❌ Profile picture not returned in response")
        return False
    
    # Step 5: Verify picture is stored
    print("\n[5] Verifying profile picture is stored on disk...")
    user.refresh_from_db()
    if user.profile_picture:
        print(f"✅ Profile picture stored: {user.profile_picture.name}")
        print(f"   - File size: {user.profile_picture.size} bytes")
        print(f"   - Full path: {user.profile_picture.path}")
    else:
        print("❌ Profile picture not found in database")
        return False
    
    # Step 6: Retrieve updated profile
    print("\n[6] Retrieving updated profile...")
    response = client.get('/api/accounts/me/')
    
    if response.status_code != 200:
        print(f"❌ Failed to get updated profile: {response.json()}")
        return False
    
    final_data = response.json()
    print(f"✅ Updated profile retrieved")
    print(f"   - Blood Group: {final_data.get('blood_group')}")
    print(f"   - Mobile: {final_data.get('mobile_number')}")
    print(f"   - Profile Picture: {final_data.get('profile_picture')}")
    print(f"   - Profile Picture URL: {final_data.get('profile_picture_url')}")
    
    # Verify changes
    if final_data.get('profile_picture') and final_data.get('profile_picture_url'):
        print("\n✅ PROFILE PICTURE UPLOAD TEST PASSED!")
        return True
    else:
        print("\n❌ PROFILE PICTURE UPLOAD TEST FAILED!")
        return False

if __name__ == '__main__':
    try:
        success = test_profile_picture_complete()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
