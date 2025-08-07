from types import NoneType
import tests.configuration as cfg
import unrealircd_rpc_py.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

servobj = rpc.Server

def test_server_list():
    """Server Ban List"""
    response = servobj.list_()

    for serv in response:
        assert isinstance(serv, Dfn.ClientServer)
        assert isinstance(serv.server, Dfn.Server)
        assert isinstance(serv.server.features, Dfn.ServerFeatures)
        for rpc_module in serv.server.features.rpc_modules:
            assert isinstance(rpc_module, Dfn.ServerRpcModules)

        assert isinstance(serv.tls, Dfn.Tls)

    assert servobj.get_error.code == 0

def test_server_get():
    """Server Ban List"""
    server = servobj.get(serverorsid="001")

    assert isinstance(server, Dfn.ClientServer)
    assert servobj.get_error.code == 0

    server = servobj.get(serverorsid="X01")

    assert isinstance(server, NoneType)
    assert servobj.get_error.code != 0

def test_server_module_list():
    """Server Ban List"""
    modules = servobj.module_list(serverorsid="001")

    for module in modules:
        assert isinstance(module, Dfn.ServerModule)

    assert servobj.get_error.code == 0
