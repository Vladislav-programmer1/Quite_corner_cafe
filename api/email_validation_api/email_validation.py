# from os import getenv
#
# from aiohttp import ClientSession, ClientTimeout
#

def validate_email(email: str) -> bool:
    """
    This func use api for validating an email
    :param email: e-mail address to check
    :return: is e-mail address valid
    """
    # server = 'https://emailvalidation.abstractapi.com/v1'
    # async with ClientSession(timeout=ClientTimeout(total=2)) as session:
    #
    #     params = {
    #         'api_key': getenv('email_validate_api_key'),
    #         'email': email
    #     }
    #     try:
    #         async with session.get(server, params=params) as response:
    #             match response:
    #                 case 200:
    #                     pass
    #                 case 422 | 500 | 503:
    #                     return True
    #                 case _:
    #                     return False
    #     except TimeoutError:
    #         return False
    #
    # content = await response.json()
    # return content.get('is_smtp_valid', dict()).get('value', False)
    return True
