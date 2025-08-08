from types import NoneType, SimpleNamespace
import unrealircd_rpc_py.Definition as Dfn
import tests.configuration as cnf

rpc = cnf.start_valid_socket_admin_connection()

channel_name = "#welcome"

def test_list_channels():
    """list all channels"""

    obj = rpc.Channel

    for i in range(0, 6):
        # noinspection
        channels = obj.list_(i)
        assert isinstance(obj.get_response_np, SimpleNamespace)
        assert not isinstance(obj.get_response, NoneType)

        for channel in channels:
            assert isinstance(channel, Dfn.Channel)

            for ban in channel.bans:
                assert isinstance(ban, Dfn.ChannelBans)
            for ban_exemption in channel.ban_exemptions:
                assert isinstance(ban_exemption, Dfn.ChannelBanExemptions)
            for member in channel.members:
                assert isinstance(member, Dfn.ChannelMembers)
            for invite_exception in channel.invite_exceptions:
                assert isinstance(invite_exception, Dfn.ChannelInviteExceptions)

        if i == 5:
            assert obj.get_error.code == -32602

def test_get_channel():
    """Get specific channel"""

    obj = rpc.Channel

    channel = obj.get(channel=channel_name, object_detail_level=5)

    assert isinstance(channel, Dfn.Channel)

    for member in channel.members:
        assert isinstance(member, Dfn.ChannelMembers)
        assert isinstance(member.user, Dfn.User)
        assert isinstance(member.tls, Dfn.Tls)
        assert isinstance(member.geoip, Dfn.Geoip)

    channel = obj.get(channel="wrongchannel", object_detail_level=5)

    assert isinstance(channel, NoneType)
    assert obj.get_error.message == "Channel not found"

def test_set_mode():
    """Set mode to a channel"""

    obj = rpc.Channel

    assert obj.set_mode("#jsonrpc", "+be", "adator_test!rpc_test@jsonrpc.deb.biz.st") == True
    assert obj.set_mode("#jsonrpc", "-be", "adator_test!rpc_test@jsonrpc.deb.biz.st") == True
    assert obj.set_mode("#jsonrpc", "-ntl") == True
    assert obj.set_mode("#jsonrpc", "+nt") == True

def test_set_topic():
    """Set topic to a channel"""

    obj = rpc.Channel

    assert obj.set_topic("#jsonrpc", "This topic has been written from jsonrpc")

    # Test wrong channel
    assert not obj.set_topic("jsonrpc", "This topic has been written from jsonrpc")
    assert obj.get_error.code == -1000 and obj.get_error.message == 'Channel not found'

def test_kick():
    """Kick nick on a channel"""

    obj_user = rpc.User
    obj = rpc.Channel

    assert obj.kick("#jsonrpc", "adator_test", "Kicked from JSONRPC User")

    # Test wrong channel
    assert not obj.kick("jsonrpc", "wrong_channel", "Kicked from JSONRPC User")
    assert obj.get_error.code == -1000 and obj.get_error.message == 'Channel not found'

    assert obj_user.join("adator_test", "#jsonrpc", '', True)