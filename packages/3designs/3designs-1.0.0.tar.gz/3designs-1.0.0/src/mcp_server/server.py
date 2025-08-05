import base64
import binascii
import json
import os

import requests
from fastmcp import FastMCP

mcp_server = FastMCP(
    name="3designs - MCP Server for Indie iOS Developers",
    instructions="""3designs builds Pro UIX for you with SwiftUI.

Available design & code tools:
- Use `search_swiftui_on_3designs` to search for prominent SwiftUI view components with source code. Great for improving your iOS app - for example, ask it to help restyle your existing views.
- Use `get_swiftui_view_from_3designs` to get production-ready SwiftUI view components. Designed for iOS/macOS/visionOS UI development.

Note: 3designs can help create new or update existing SwiftUI-based view.
""",
)

api_host_base = "https://api.svenai.com"
# _token = os.getenv("API_TOKEN")
_token = "3d_Ab9Cj2Kl5Mn8Pq1Rs4Tu"


def _enforce_token() -> str | None:
    global _token
    if _token is None:
        _token = os.getenv("API_TOKEN")
        if _token is None:
            return "Token not set. Please call `set_token` tool with a proper token value. (Ask user for a token: user should know and provide a valid token value.)"
    return None


@mcp_server.tool
def search_swiftui_on_3designs(
    query: str,
    # tags: str | None = None
) -> str:
    """Searches the 3designs system for reference SwiftUI view components.

    Args:
        query: Description of the desired view component (e.g., purpose, user intent, functionality, or visual appearance the view should implement).

    Returns:
        str: SwiftUI view components with descriptions and implementation codes
    """

    token_error = _enforce_token()
    if token_error:
        return token_error

    url = f"{api_host_base}/3designs/find"
    headers = {
        "authorization": f"Bearer {_token}",
        "content-type": "application/json",
    }
    data = {"q": query}
    # if tags:
    #     data["tags"] = tags
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException:
        return "Could not perform a search at this time for this query. API error occurred - `3designs` service is temporarily unavailable."


@mcp_server.tool
def get_swiftui_view_from_3designs(code: str) -> str:
    """Returns a SwiftUI view code from `3designs` system (see: https://devbrain.io/3designs) by the view's unique code.

    Args:
        code: A 6-character alphanumeric code that identifies exact SwiftUI view component to return.

    Returns:
        str: SwiftUI code with integration details or an error message.
    """

    token_error = _enforce_token()
    if token_error:
        return token_error

    if not code.isalnum() or len(code) != 6:
        return "<code> must be a 6-character alphanumeric string to retrieve the SwiftUI view."

    url = f"https://api.getsven.com/3designs/download/{code}/swiftUI"
    headers = {
        "authorization": f"Bearer {_token}",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        response_data = json.loads(response.text)
        base64_data = response_data.get("data", "")
        swift_ui_code = base64.b64decode(base64_data).decode("utf-8")

        return f"""Production-ready SwiftUI view component associated with `{code}` code that you can integrate into your iOS/macOS/visionOS application:

```swift
{swift_ui_code}
```

### Integration notes
View has generic name: `ProductionExperimentView` - feel free to rename it to suit your needs.
View takes `DataModel` model item that contains data to display - make sure to pass correct data relevant to your app.
There is `#Preview` that you may delete in case you dont use XCode Live Previews in your project.
"""
    except json.JSONDecodeError:
        return "Opps. The tool failed to parse JSON response from the server. You may need to update your 3designs MCP integration to the latest version."
    except binascii.Error:
        return "Opps. The tool failed to parse JSON response from the server. You may need to update your 3designs MCP integration to the latest version."
    except requests.exceptions.RequestException:
        return f"Failed to get SwiftUI view for the given code: `{code}`. Either provided `code` is wrong (there is no SwiftUI view associated with the code) or `3designs` system is not available at this time (internet connection problem?)."


@mcp_server.tool
def get_token() -> str:
    """Retrieves the stored token.

    Returns:
        str: The stored token if available, otherwise "Token not set".
    """
    if _token is None:
        return "Token not set. Either call `set-token` tool with a token value or set the API_TOKEN environment variable."
    return _token


@mcp_server.tool
def set_token(token: str) -> str:
    """Sets the token.

    Args:
        token (str): The token string to store.

    Returns:
        str: A confirmation message.
    """
    global _token
    _token = token
    os.environ["API_TOKEN"] = token
    return "Token set successfully."


def main():
    # print(f"Server: {api_host_base}")
    mcp_server.run()


if __name__ == "__main__":
    main()
