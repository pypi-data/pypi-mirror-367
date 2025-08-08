import tests.configuration as cfg
import unrealircd_rpc_py.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

def test_rpc_info():
    """Test RPC Info
    """

    # Test connection response
    assert rpc.get_error.code == 0

    rpc_obj = rpc.Rpc
    responses = rpc_obj.info()

    for info in responses:
        assert isinstance(info, Dfn.RpcInfo)

    assert rpc_obj.get_error.code == 0

def test_rpc_set_issuer():
    """Test RPC set issuer
    """
    rpc_obj = rpc.Rpc
    assert rpc_obj.set_issuer('adator_test')
