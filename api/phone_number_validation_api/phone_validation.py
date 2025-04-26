from os import getenv

from requests import Session
from requests.adapters import HTTPAdapter, Retry


def validate_phone_number(phone_number: str) -> bool:
    """
    This func use api for validating a phone number.
    :param phone_number: number to check
    :return: is phone  valid
    """
    server = 'https://phonevalidation.abstractapi.com/v1/'
    with Session() as session:
        retry = Retry(total=10, connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        params = {
            'api_key': getenv('phone_validate_api_key'),
            'phone': phone_number
        }
        response = session.get(server, params=params)
        if response.status_code != 200:
            return False
    content = response.json()
    return content.get('valid')
