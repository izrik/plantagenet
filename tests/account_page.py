import plantagenet


def test_account_unauthenticated_returns_401(cl):
    response = cl.get('/account')
    assert response.status_code == 401


def test_account_regular_user_returns_200(cl, login, regular_user):
    login(regular_user)
    response = cl.get('/account')
    assert response.status_code == 200
    assert b'user@example.com' in response.data


def test_account_admin_returns_200(cl, login):
    login()
    response = cl.get('/account')
    assert response.status_code == 200


def test_account_post_updates_the_name(cl, login, regular_user):
    login(regular_user)
    response = cl.post('/account', data={'name': 'New Name'})
    assert response.status_code == 302

    assert plantagenet.User.get(regular_user.id).name == 'New Name'


def test_account_post_ignores_an_empty_name(cl, login, regular_user):
    login(regular_user)
    cl.post('/account', data={'name': ''})

    assert plantagenet.User.get(regular_user.id).name == 'User'


def test_account_post_changes_the_password(cl, login, regular_user):
    login(regular_user)
    response = cl.post('/account', data={'name': '',
                                         'current_password': 'password123',
                                         'new_password': 'newpassword'})
    assert response.status_code == 302

    assert plantagenet.User.get(regular_user.id).check_password('newpassword')


def test_account_post_wrong_current_password_keeps_it(cl, login,
                                                      regular_user):
    login(regular_user)
    response = cl.post('/account', data={'name': '',
                                         'current_password': 'wrong',
                                         'new_password': 'newpassword'})
    assert response.status_code == 302
    assert '/account' in response.headers['Location']

    assert plantagenet.User.get(regular_user.id).check_password('password123')


def test_account_post_short_new_password_returns_400(cl, login,
                                                     regular_user):
    login(regular_user)
    response = cl.post('/account', data={'name': '',
                                         'current_password': 'password123',
                                         'new_password': 'short'})
    assert response.status_code == 400

    assert plantagenet.User.get(regular_user.id).check_password('password123')


def test_account_post_cannot_change_the_email(cl, login, regular_user):
    login(regular_user)
    cl.post('/account', data={'name': '', 'email': 'other@example.com'})

    assert plantagenet.User.get(regular_user.id).email == 'user@example.com'


def test_account_post_does_not_grant_admin(cl, login, regular_user):
    login(regular_user)
    cl.post('/account', data={'name': '', 'is_admin': '1'})

    assert plantagenet.User.get(regular_user.id).is_admin is False
