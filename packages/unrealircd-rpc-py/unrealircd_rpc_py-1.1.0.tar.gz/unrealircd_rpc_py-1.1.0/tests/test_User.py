import unrealircd_rpc_py.Definition as Dfn
import tests.configuration as cfg

rpc =cfg.start_valid_socket_admin_connection()

nickname_for_get_user = 'adator'

nickname = 'adator_test'
nickname_new = 'rpc_test'
username = 'rpc_test'

nickname_not_available = 'xxxxxxx'


def test_get_user():
    """Get a user adator"""

    user_obj = rpc.User

    client = user_obj.get(nickname_for_get_user)
    assert client.name == nickname_for_get_user
    assert isinstance(client, Dfn.Client)
    assert isinstance(client.geoip, Dfn.Geoip)
    assert isinstance(client.tls, Dfn.Tls)
    assert isinstance(client.user, Dfn.User)
    for channel in client.user.channels:
        assert isinstance(channel, Dfn.UserChannel)

    get_user = user_obj.get('nickname_not_available_for_sure')
    assert get_user is None
    assert user_obj.get_error.message == 'Nickname not found'

def test_list_users():
    """Get a user adator"""

    user_obj = rpc.User

    for i in range(1, 4):
        list_user = user_obj.list_(i)
        assert type(list_user) == list

    list_user = user_obj.list_(4)
    for client in list_user:
        assert isinstance(client, Dfn.Client)
        assert isinstance(client.geoip, Dfn.Geoip)
        assert isinstance(client.tls, Dfn.Tls)
        assert isinstance(client.user, Dfn.User)
        for channel in client.user.channels:
            assert isinstance(channel, Dfn.UserChannel)

    # Error level 3 doesnt exist
    user_obj.list_(3)
    assert user_obj.Error.code == -32602

def test_set_nick():
    """Get a user adator"""

    user_obj = rpc.User
    assert user_obj.set_nick(nickname, nickname_new, True)
    assert not user_obj.set_nick(nickname_not_available, 'adator_test', True)
    assert user_obj.set_nick(nickname_new, nickname, True)

def test_set_username():
    """Get a user adator"""

    user_obj = rpc.User

    set_nick = user_obj.set_username(nickname, username)
    assert type(set_nick) == bool
    
    if not set_nick:
        assert user_obj.Error.code != 0

    assert not user_obj.set_username(nickname_not_available, 'adator_test')

def test_set_realname():
    """Set realname"""

    user_obj = rpc.User

    user_obj.set_realname('adator_test', 'jrpc_test')

    assert user_obj.set_realname('adator_test', 'jrpc_original')
    assert user_obj.get_error.code == 0


    assert not user_obj.set_realname('xxxxxx', 'adator_test')
    assert user_obj.get_error.code != 0

def test_set_vhost():
    """Set realname"""

    user_obj = rpc.User

    user_obj.set_vhost('adator_test', 'jsonrpc.deb.biz.st')

    assert user_obj.set_vhost('adator_test', 'jsonrpc_original.deb.biz.st')
    assert user_obj.get_error.code == 0

    assert not user_obj.set_vhost('xxxxxx', 'jsonrpc.deb.biz.st')
    assert user_obj.get_error.code != 0

def test_set_mode():
    """Set realname"""

    user_obj = rpc.User

    assert user_obj.set_mode('adator_test', '-o')
    assert user_obj.get_error.code == 0

    assert user_obj.set_mode('adator_test', '+t')
    assert user_obj.get_error.code == 0

    assert user_obj.set_mode('adator_test', '-t')
    assert user_obj.get_error.code == 0

    assert not user_obj.set_mode('xxxxxx', 'jsonrpc.deb.biz.st')
    assert user_obj.get_error.code != 0

def test_set_snomask():
    """Set snomask"""

    user_obj = rpc.User

    assert user_obj.set_snomask(nickname, '+s')
    assert user_obj.get_error.code == 0
    user_obj.set_snomask(nickname, '-s')

    assert not user_obj.set_snomask(nickname_not_available, '-x')
    assert user_obj.get_error.code != 0

def test_set_oper():
    """Set oper"""

    user_obj = rpc.User

    assert user_obj.set_oper(nickname, 'adator', 'adator')
    assert user_obj.get_error.code == 0
