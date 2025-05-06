# from asyncio import TimeoutError
# from os import getenv
#
# from aiohttp import ClientTimeout, ClientSession


def validate_phone_number(phone_number: str) -> bool:
    """
    This func use api for validating a phone number.
    :param phone_number: number to check
    :return: is phone  valid
    """
    # server = 'https://phonevalidation.abstractapi.com/v1/'
    # async with ClientSession(timeout=ClientTimeout(total=2)) as session:
    #     params = {
    #         'api_key': getenv('phone_validate_api_key'),
    #         'phone': phone_number
    #     }
    #     try:
    #         async with session.get(server, params=params) as response:
    #             match response.status:
    #                 case 200:
    #                     pass
    #                 case 503 | 500 | 422:
    #                     return True
    #                 case _:
    #                     return False
    #     except TimeoutError:
    #         return False
    #
    # content = await response.json()
    # return content.get('valid')
    return True