from os import getenv

from requests import Session
from requests.adapters import HTTPAdapter, Retry


def validate_email(email: str) -> bool:
    """
    This func use api for validating an email
    :param email: e-mail address to check
    :return: is e-mail address valid
    """
    server = 'https://emailvalidation.abstractapi.com/v1'
    with Session() as session:
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        params = {
            'api_key': getenv('email_validate_api_key'),
            'email': email
        }
        response = session.get(server, **params)
        if response.status_code != 200:
            return False
    content = response.json()
    return content.get('is_smtp_valid').get('value', False)
