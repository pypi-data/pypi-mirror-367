import requests
import json

def generate_prompt(api_key: str, api_url: str, raw_input: str, language_code: str = "en-US", timeout: int = 10):
    """
    Makes a POST request to the prompts-testing API to generate content.

    Args:
        api_key (str): The user's API key.
        api_url (str): The URL of the API endpoint.
        raw_input (str): The raw text input for the API.
        language_code (str, optional): The language code for the input. Defaults to "en-US".
        timeout (int, optional): The request timeout in seconds. Defaults to 10.

    Returns:
        dict: The JSON response from the API if successful.
        None: If an error occurs.
    """
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "raw_input": raw_input,
        "language_code": language_code
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response body: {response.text}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return None
