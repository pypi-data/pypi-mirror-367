from typing import Literal
from unrealircd_rpc_py import Loader

__debug_level: Literal[50] = 50

__valid_url = 'http://172.18.132.244:8600/api'

__valid_admin_username = 'adminpanel'
__valid_admin_password = '25T@bler@ne'

__valid_readonly_username = 'readonly'
__valid_readonly_password = 'uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa'

def start_valid_socket_admin_connection() -> Loader:

    return Loader(
        req_method='socket',
        url=__valid_url,
        username=__valid_admin_username,
        password=__valid_admin_password,
        debug_level=__debug_level
    )

def start_valid_requests_admin_connection() -> Loader:

    return Loader(
        req_method='requests',
        url=__valid_url,
        username=__valid_admin_username,
        password=__valid_admin_password,
        debug_level=__debug_level
    )

def start_valid_socket_readonly_connection() -> Loader:

    return Loader(
        req_method='socket',
        url=__valid_url,
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_valid_requests_readonly_connection() -> Loader:

    return Loader(
        req_method='requests',
        url=__valid_url,
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_socket_readonly_connection_with_wrong_credentials() -> Loader:

    return Loader(
        req_method='socket',
        url=__valid_url,
        username=f'{__valid_readonly_username}-wrong-user',
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_socket_readonly_connection_with_wrong_link() -> Loader:

    return Loader(
        req_method='socket',
        url=f'{__valid_url}-wrong-link',
        username=__valid_readonly_username,
        password=__valid_readonly_password,
        debug_level=__debug_level
    )

def start_requests_connection_with_invalid_readonly_credentials() -> Loader:
    """## Authentication failed with requests
    """
    return Loader(
                req_method='requests',
                url=__valid_url,
                username=f'{__valid_readonly_username}-wrong-username',
                password=__valid_readonly_password,
                debug_level=__debug_level
            )

def start_invalid_method_connection():
    """## Invalid method
    """
    return Loader(
                req_method='mynewmethod',
                url=__valid_url,
                username='',
                password='',
                debug_level=__debug_level
            )