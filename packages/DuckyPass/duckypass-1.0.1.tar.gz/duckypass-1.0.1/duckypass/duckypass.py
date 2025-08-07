import requests

def DuckyPass(password_type, count):
    """
    Generates password(s) using the DuckyPass API.
    Args:
        password_type (str): "simple" or "secure"
        count (int): Number of passwords to generate
    Returns:
        str or list: A password string if count == 1, or a list of passwords if count > 1
    Raises:
        Exception: If the API request fails.
    """
    if password_type not in ["simple", "secure"]:
        raise ValueError("password_type must be 'simple' or 'secure'")
    if not isinstance(count, int) or count < 1:
        raise ValueError("count must be an integer greater than 0")

    url = f"https://api.duckypass.net/{password_type}"
    params = {}
    if count > 1:
        params["quantity"] = count

    response = requests.get(url, params=params)
    if response.status_code == 200:
        if count == 1:
            return response.text.strip()
        else:
            return response.json().get("passwords", [])
    else:
        raise Exception(f"Failed to generate password(s): {response.status_code} - {response.text}")