from unrealircd_rpc_py.Loader import Loader

rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/api',
                username='readonly',
                password='uT9!x7GzV1#sDk3bL5wP@8YrX&f6mQa',
                debug_level=50
            )

def test_rpc_info():
    """## Wrong link
    """

    assert rpc.Error.code == 0

    Rpc = rpc.Rpc
    rpcInfos = Rpc.info()

    assert rpcInfos[0].name == 'stats.get'
    assert rpcInfos[0].module == 'rpc/stats'

    rpcSetIssuer = Rpc.set_issuer('adator')
    assert rpcSetIssuer == True

