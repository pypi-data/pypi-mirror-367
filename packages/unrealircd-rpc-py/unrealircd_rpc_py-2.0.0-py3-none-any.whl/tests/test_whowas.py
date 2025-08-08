import tests.configuration as cfg
import unrealircd_rpc_py.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

whowas = rpc.Whowas

def test_whowas_get():
    """Get a user adator"""

    for i in range(0, 8):
        whowas_list = whowas.get("adator_test", None, i)
        
        for whs in whowas_list:
            assert isinstance(whs, Dfn.Whowas)
            assert isinstance(whs.user, Dfn.WhowasUser)
            assert isinstance(whs.geoip, Dfn.Geoip)
    
    # Should be empty list
    assert whowas.get("for_sure_this_nick_is_not_available") == []

