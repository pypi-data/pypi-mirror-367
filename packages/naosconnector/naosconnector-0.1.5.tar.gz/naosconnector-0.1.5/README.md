# naosconnector
Helper library for using Naos APIs

# How to use
create a new instance of the `NaosConnector` class with your Naos platform URL. Use the basic_auth function to authenticate with your username and password. NaosConnector then manages access and refreshes tokens automatically.

Once authenticated, you can use the `get`, `post`, `put`, and `delete` methods to interact with the Naos API. These methods will automatically include the access token in the request headers.

# naosconnector.py
from naosconnector.naosconnector import NaosConnector
# Example usage
naos = NaosConnector("https://your-naos-platform-url.com")
naos.basic_auth("your_username", "your_password")
## Example GET request
url = "/v1"
response = naos.get(url)
print(response)

