import requests
from requests.auth import HTTPBasicAuth

# Configuration
wp_url = "https://biddenham.org.uk/wp-json/wp/v2/posts"  # Use 'tribe/events/v1/events' for the calendar
username = "MattLavis"
app_password = "ceLp N53Z M8x6 h2w5 hmFV D9Ph"  # The one you just generated


def test_wp_connection():
    # A simple test to see if we can reach the user endpoint
    test_url = "https://biddenham.org.uk/wp-json/wp/v2/users/me"

    response = requests.get(test_url, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 200:
        print("Success! Python can talk to your WordPress account.")
        print(f"Logged in as: {response.json().get('name')}")
    else:
        print(f"Failed. Error code: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    test_wp_connection()
