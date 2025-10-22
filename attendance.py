import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
import os

# disable proxy for device IP
os.environ["NO_PROXY"] = "10.1.191.11"

DEVICE_IP = "10.1.191.11"
USERNAME = "admin"
PASSWORD = "hik12345"

url = f"https://{DEVICE_IP}?format=json"
print(url)

try:
    # First try Digest
    resp = requests.get(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=5)
    print("Digest Auth:", resp.status_code, resp.text)

    # Then try Basic
    resp2 = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=5)
    print("Basic Auth:", resp2.status_code, resp2.text)

    response = requests.get(
        url,
        auth=HTTPDigestAuth(USERNAME, PASSWORD),
        timeout=5,
        verify=False
    )

    if response.status_code == 200:
        print("---------- SUCCESS ----------")
        try:
            data = response.json()
        except Exception:
            print("Response is not valid JSON:")
            print(response.text)
            exit()

        # Loop through events if present
        events = data.get("AcsEvent", [])
        if events:
            for event in events:
                print("Employee ID:", event.get("employeeNoString"))
                print("Time:", event.get("time"))
                print("Event:", event.get("eventType"))
                print("---------")
        else:
            print("No events found in response.")

    else:
        print("Error:", response.status_code, response.text)

except requests.exceptions.RequestException as e:
    print("Connection failed:", e)
