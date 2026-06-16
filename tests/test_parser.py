from uri_control.parser import parse_uri


def test_parse_custom_uri():
    uri = parse_uri("browser://default/page/open?wait=true#frag")
    assert uri.scheme == "browser"
    assert uri.authority == "default"
    assert uri.path == ("page", "open")
    assert uri.body == "default/page/open"
    assert uri.query == {"wait": "true"}
    assert uri.fragment == "frag"
