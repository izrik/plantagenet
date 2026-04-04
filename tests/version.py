from plantagenet import Options


def test_version_number_is_correct():
    # expect
    assert Options.get_version() == 'unknown'
