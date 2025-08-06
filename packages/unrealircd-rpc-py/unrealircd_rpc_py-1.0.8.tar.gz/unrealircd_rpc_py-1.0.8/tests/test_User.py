from unrealircd_rpc_py.Loader import Loader
import unrealircd_rpc_py.Definition as Dfn

rpc = Loader(
                req_method='socket',
                url='https://deb.biz.st:8600/api',
                username='adminpanel',
                password='25T@bler@ne',
                debug_level=50
            )

nickname_for_get_user = 'adator'

nickname = 'adator_test'
nickname_new = 'rpc_test'
username = 'rpc_test'

nickname_not_available = 'xxxxxxx'


def test_get_user():
    """Get a user adator"""

    UserObj = rpc.User

    get_user = UserObj.get(nickname_for_get_user)
    assert get_user.name == nickname_for_get_user
    assert isinstance(get_user, Dfn.Client)

    get_user = UserObj.get('nickname_not_available_for_sure')
    assert get_user is None
    assert UserObj.get_error.message == 'Nickname not found'

def test_list_users():
    """Get a user adator"""

    UserObj = rpc.User

    for i in range(1, 4):
        list_user = UserObj.list_(i)
        assert type(list_user) == list

    list_user = UserObj.list_(3)
    assert UserObj.Error.code == -32602

def test_set_nick():
    """Get a user adator"""

    UserObj = rpc.User

    set_nick = UserObj.set_nick(nickname, nickname_new, True)
    assert set_nick == True

    set_nick = UserObj.set_nick(nickname_not_available, 'adator_test', True)
    assert set_nick == False

    set_nick = UserObj.set_nick(nickname_new, nickname, True)
    assert set_nick == True

def test_set_username():
    """Get a user adator"""

    UserObj = rpc.User

    set_nick = UserObj.set_username(nickname, username)
    assert type(set_nick) == bool
    
    if not set_nick:
        assert UserObj.Error.code != 0

    set_nick = UserObj.set_username(nickname_not_available, 'adator_test')
    assert set_nick == False

def test_set_realname():
    """Set realname"""

    UserObj = rpc.User

    UserObj.set_realname('adator_test', 'jrpc_test')

    assert UserObj.set_realname('adator_test', 'jrpc_original')
    assert UserObj.get_error.code == 0


    assert not UserObj.set_realname('xxxxxx', 'adator_test')
    assert UserObj.get_error.code != 0

def test_set_vhost():
    """Set realname"""

    UserObj = rpc.User

    UserObj.set_vhost('adator_test', 'jsonrpc.deb.biz.st')

    assert UserObj.set_vhost('adator_test', 'jsonrpc_original.deb.biz.st')
    assert UserObj.get_error.code == 0

    assert not UserObj.set_vhost('xxxxxx', 'jsonrpc.deb.biz.st')
    assert UserObj.get_error.code != 0

def test_set_mode():
    """Set realname"""

    UserObj = rpc.User

    assert UserObj.set_mode('adator_test', '-o')
    assert UserObj.get_error.code == 0

    assert UserObj.set_mode('adator_test', '+t')
    assert UserObj.get_error.code == 0

    assert UserObj.set_mode('adator_test', '-t')
    assert UserObj.get_error.code == 0

    assert not UserObj.set_mode('xxxxxx', 'jsonrpc.deb.biz.st')
    assert UserObj.get_error.code != 0

def test_set_snomask():
    """Set snomask"""

    UserObj = rpc.User

    assert UserObj.set_snomask(nickname, '+s')
    assert UserObj.get_error.code == 0
    UserObj.set_snomask(nickname, '-s')

    assert not UserObj.set_snomask(nickname_not_available, '-x')
    assert UserObj.get_error.code != 0

def test_set_oper():
    """Set oper"""

    UserObj = rpc.User

    assert UserObj.set_oper(nickname, 'adator', 'adator')
    assert UserObj.get_error.code == 0
