from unrealircd_rpc_py.Loader import Loader

def test_wrong_link():
    """## Wrong link
    """
    rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/ap2i',
                username='readonly',
                password='uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa',
                debug_level=50
            )

    assert rpc.get_error.code == -1

def test_invalid_auth_socket():
    """### Authentication failed with Socket
    """
    rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/api',
                username='thisuserdontexist',
                password='uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa',
                debug_level=50
            )

    assert rpc.get_error.code == -1
    assert rpc.get_error.message == '>> Authentication required <<'

def test_invalid_auth_requests():
    """## Authentication failed with requests
    """
    rpc = Loader(
                req_method='requests',
                url='https://deb.biz.st:8600/api',
                username='readonly1',
                password='uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa',
                debug_level=50
            )

    assert rpc.get_error.code == -1
    assert rpc.get_error.message == '>> Authentication required <<' or ">> Connection Aborted <<"

def test_invalid_method():
    """## Invalid method
    """
    test_rpc = Loader(
                req_method='mynewmethod',
                url='https://deb.biz.st:8600/api',
                username='readonly1',
                password='uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa',
                debug_level=50
            )

    assert test_rpc.get_error.code == -1
    assert test_rpc.get_error.message == '<< Invalid method >>'