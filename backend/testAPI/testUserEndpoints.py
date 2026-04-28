import os
import requests
import asyncio
import time
from pathlib import Path

# from dotenv import load_dotenv

# # Load .env from backend dir and project root so test uses same config as backend
# _backend_dir = Path(__file__).resolve().parent.parent
# _project_root = _backend_dir.parent
# load_dotenv(_backend_dir / ".env")
# load_dotenv(_project_root / ".env")

SUPABASE_URL = "https://bafblcxwhdvikgcpcnds.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_EHbCfU3Xd5oku8EZZTLD7g_1bxWBYnC"

EMAIL = "test@gmail.com"
PASSWORD = "testpass123"


def get_jwt():
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }

    json = {
        "email": EMAIL,
        "password": PASSWORD,
    }

    response = requests.post(url, headers=headers, json=json)

    if response.status_code != 200:
        print("Login failed:", response.text)
        exit()

    return response.json()["access_token"]

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}

TOKEN = get_jwt()



def testUserCreation():
    url = "http://0.0.0.0:8000/api/createUser"

    json = {
        "username": "pierce",
    }

    response = requests.post(
        url=url,
        json=json,
        headers={"Content-Type": "application/json", **AUTH_HEADERS},
    )

    print("CREATED USER")
    print(response.json())


def testUserDeletion():
    url = "http://0.0.0.0:8000/api/users/me"

    response = requests.delete(url, headers=AUTH_HEADERS)

    print("DELETED USER")
    print(response.json())


def testUserUpdates():
    url = "http://0.0.0.0:8000/api/updateUser"

    json = {
        "username": "pierce's cooler username",
    }

    response = requests.put(url=url, json=json, headers=AUTH_HEADERS)

    print("Updated USER")
    print(response.json())


def testUserGet():
    url = "http://0.0.0.0:8000/api/users/me"

    response = requests.get(url, headers=AUTH_HEADERS)

    print("USER json:")
    print(response.json())


test_no = 1

<<<<<<< Updated upstream
match test_no:

    case 0:
        testUserGet()

    case 1:
        """
        Test 1: Basic User creation and viewing of username:
        """
        testUserCreation()

    case 2:
        """
        Test 2: Update username and view result:
        """
        testUserUpdates()
        testUserGet()

    case 3:
        """
        Test 3: Delete user:
        """
        testUserDeletion()

    case 4:
        """
        Test 4: All tests combined:
        """
        testUserCreation()
        time.sleep(5)  
        testUserGet()
        time.sleep(5)
        testUserUpdates()
        time.sleep(5)
        testUserGet()
        time.sleep(5)
        testUserDeletion()
=======
if test_no == 0:
    print(get_jwt())
    testUserGet()
elif test_no == 1:
    """
    Test 1: Basic User creation and viewing of username:
    """
    testUserCreation()
    testUserGet()
elif test_no == 2:
    """
    Test 2: Update username and view result:
    """
    testUserUpdates()
    testUserGet()
elif test_no == 3:
    """
    Test 3: Delete user:
    """
    testUserDeletion()
elif test_no == 4:
    """
    Test 4: All tests combined:
    """
    testUserCreation()
    testUserGet()
    testUserUpdates()
    testUserGet()
    testUserDeletion()
>>>>>>> Stashed changes
