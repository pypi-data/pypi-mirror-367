import tests.configuration as cfg
import unrealircd_rpc_py.Definition as Dfn

rpc = cfg.start_valid_socket_admin_connection()

spamfobj = rpc.Spamfilter

def test_spamfilter_list():
    """Server Ban List"""
    response = spamfobj.list_()
    for spam in response:
        assert isinstance(spam, Dfn.Spamfilter)

    assert spamfobj.get_error.code == 0

def test_spamfilter_get():
    """Server Ban List"""
    assert spamfobj.get(
        name="*.supernets.*",
        match_type="simple",
        spamfilter_targets="cp",
        ban_action="gline"
    )
    assert spamfobj.get_error.code == 0

    assert not spamfobj.get(
        name="impossible_to_find_this_name",
        match_type="simple____",
        spamfilter_targets="cp____",
        ban_action="gline_____"
    )
    assert spamfobj.get_error.code != 0

def test_spamfilter_add():
    """Server Ban List"""
    assert spamfobj.add(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        ban_duration=1,
        spamfilter_targets="cp",
        reason="Coming from jsonrpc",
        set_by="json_user"
    )
    assert spamfobj.get_error.code == 0

    assert not spamfobj.add(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        ban_duration=1,
        spamfilter_targets="cp",
        reason="Coming from jsonrpc",
        set_by="json_user"
    )
    assert spamfobj.get_error.code == -1001 and spamfobj.get_error.message == "A spamfilter with that regex+action+target already exists"

def test_spamfilter_del():
    """Server Ban List"""
    assert spamfobj.del_(
        name="jsonrpc_add_spam",
        match_type="simple",
        ban_action="kill",
        spamfilter_targets="cp",
        _set_by="json_user"
    )
    assert spamfobj.get_error.code == 0