from unrealircd_rpc_py.Loader import Loader
import unrealircd_rpc_py.Definition as Dfn

rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/api',
                username='adminpanel',
                password='25T@bler@ne',
                debug_level=50
            )

stats_obj = rpc.Stats

def test_stats_get():
    """Get a user adator"""

    for i in range(0, 8):
        response = stats_obj.get(i)
        
        assert isinstance(response, Dfn.Stats)
        assert isinstance(response.server, Dfn.StatsServer)
        assert isinstance(response.server_ban, Dfn.StatsServerBan)
        assert isinstance(response.channel, Dfn.StatsChannel)
        assert isinstance(response.user, Dfn.StatsUser)
        for country in response.user.countries:
            assert isinstance(country, Dfn.StatsUserCountries)
