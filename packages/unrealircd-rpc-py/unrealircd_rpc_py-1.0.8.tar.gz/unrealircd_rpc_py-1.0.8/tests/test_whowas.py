from unrealircd_rpc_py.Loader import Loader
import unrealircd_rpc_py.Definition as Dfn

rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/api',
                username='adminpanel',
                password='25T@bler@ne',
                debug_level=50
            )

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

