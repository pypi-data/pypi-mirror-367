import tests.configuration as cfg

def test_wrong_link():
    """## Wrong link
    """
    rpc = cfg.start_socket_readonly_connection_with_wrong_link()
    assert rpc.get_error.code == -1

def test_invalid_auth_socket():
    """### Authentication failed with Socket
    """
    rpc = cfg.start_socket_readonly_connection_with_wrong_credentials()
    assert rpc.get_error.code == -1
    assert rpc.get_error.message == '>> Authentication required <<'

def test_invalid_auth_requests():
    """## Authentication failed with requests
    """
    rpc = cfg.start_requests_connection_with_invalid_readonly_credentials()
    assert rpc.get_error.code == -1
    assert rpc.get_error.message == '>> Authentication required <<' or ">> Connection Aborted <<"

def test_invalid_method():
    """## Invalid method
    """
    rpc = cfg.start_invalid_method_connection()
    assert rpc.get_error.code == -1
    assert rpc.get_error.message == '<< Invalid method >>'