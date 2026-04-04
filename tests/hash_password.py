import plantagenet


def test_hash_password():
    # given
    unhashed_password = '12345'

    # when
    result = plantagenet.hash_password(unhashed_password)

    # then
    assert plantagenet.bcrypt.check_password_hash(result, unhashed_password)
