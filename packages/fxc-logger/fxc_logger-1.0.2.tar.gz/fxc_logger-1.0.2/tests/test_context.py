from fxc_logger import set_correlation_id, get_correlation_id


def test_set_correlation_id():
    set_correlation_id("123")
    assert get_correlation_id() == "123"

def test_get_correlation_id():
    set_correlation_id("123")
    assert get_correlation_id() == "123"

test_set_correlation_id()
test_get_correlation_id()