import plantagenet


def test_users_unauthenticated_returns_401(cl):
    response = cl.get('/users')
    assert response.status_code == 401


def test_users_non_admin_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.get('/users')
    assert response.status_code == 403


def test_users_admin_returns_200(cl, login):
    login()
    response = cl.get('/users')
    assert response.status_code == 200


def test_users_lists_the_users(cl, login, regular_user):
    login()
    response = cl.get('/users')
    assert b'user@example.com' in response.data
    assert b'admin@example.com' in response.data


def test_users_post_creates_a_user(cl, login):
    login()
    response = cl.post('/users', data={'email': 'new@example.com',
                                       'name': 'New User',
                                       'password': 'password123'})
    assert response.status_code == 302

    user = plantagenet.User.get_by_email('new@example.com')
    assert user is not None
    assert user.name == 'New User'
    assert user.is_admin is False
    assert user.check_password('password123')


def test_users_post_creates_an_admin(cl, login):
    login()
    cl.post('/users', data={'email': 'new@example.com', 'name': '',
                            'password': 'password123', 'is_admin': '1'})

    user = plantagenet.User.get_by_email('new@example.com')
    assert user.is_admin is True
    assert user.name == 'new@example.com'


def test_users_post_non_admin_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.post('/users', data={'email': 'new@example.com',
                                       'name': '',
                                       'password': 'password123'})
    assert response.status_code == 403
    assert plantagenet.User.get_by_email('new@example.com') is None


def test_users_post_duplicate_email_returns_400(cl, login, regular_user):
    login()
    response = cl.post('/users', data={'email': 'user@example.com',
                                       'name': '',
                                       'password': 'password123'})
    assert response.status_code == 400
    assert plantagenet.User.count() == 2


def test_users_post_invalid_email_returns_400(cl, login):
    login()
    response = cl.post('/users', data={'email': 'not-an-email', 'name': '',
                                       'password': 'password123'})
    assert response.status_code == 400


def test_users_post_short_password_returns_400(cl, login):
    login()
    response = cl.post('/users', data={'email': 'new@example.com',
                                       'name': '', 'password': 'short'})
    assert response.status_code == 400
    assert plantagenet.User.get_by_email('new@example.com') is None


def test_edit_user_unauthenticated_returns_401(cl, regular_user):
    response = cl.get('/users/{}'.format(regular_user.id))
    assert response.status_code == 401


def test_edit_user_non_admin_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.get('/users/{}'.format(regular_user.id))
    assert response.status_code == 403


def test_edit_user_returns_200(cl, login, regular_user):
    login()
    response = cl.get('/users/{}'.format(regular_user.id))
    assert response.status_code == 200
    assert b'user@example.com' in response.data


def test_edit_user_missing_returns_404(cl, login):
    login()
    response = cl.get('/users/12345')
    assert response.status_code == 404


def test_edit_user_post_updates_the_user(cl, login, regular_user):
    login()
    response = cl.post('/users/{}'.format(regular_user.id),
                       data={'email': 'changed@example.com',
                             'name': 'Changed'})
    assert response.status_code == 302

    user = plantagenet.User.get(regular_user.id)
    assert user.email == 'changed@example.com'
    assert user.name == 'Changed'
    assert user.is_admin is False


def test_edit_user_post_grants_admin(cl, login, regular_user):
    login()
    cl.post('/users/{}'.format(regular_user.id),
            data={'email': regular_user.email, 'name': 'User',
                  'is_admin': '1'})

    assert plantagenet.User.get(regular_user.id).is_admin is True


def test_edit_user_post_revokes_admin(cl, login, admin_user, make_user):
    other = make_user('other@example.com', 'Other', is_admin=True)
    login()
    cl.post('/users/{}'.format(other.id),
            data={'email': other.email, 'name': other.name})

    assert plantagenet.User.get(other.id).is_admin is False


def test_edit_user_post_cannot_revoke_the_last_admin(cl, login, admin_user):
    login()
    response = cl.post('/users/{}'.format(admin_user.id),
                       data={'email': admin_user.email, 'name': 'Admin'})
    assert response.status_code == 400
    assert plantagenet.User.get(admin_user.id).is_admin is True


def test_edit_user_post_changes_the_password(cl, login, regular_user):
    login()
    cl.post('/users/{}'.format(regular_user.id),
            data={'email': regular_user.email, 'name': 'User',
                  'new_password': 'newpassword'})

    assert plantagenet.User.get(regular_user.id).check_password('newpassword')


def test_edit_user_post_keeps_the_password_when_blank(cl, login,
                                                      regular_user):
    login()
    cl.post('/users/{}'.format(regular_user.id),
            data={'email': regular_user.email, 'name': 'User',
                  'new_password': ''})

    assert plantagenet.User.get(regular_user.id).check_password('password123')


def test_edit_user_post_short_password_returns_400(cl, login, regular_user):
    login()
    response = cl.post('/users/{}'.format(regular_user.id),
                       data={'email': regular_user.email, 'name': 'User',
                             'new_password': 'short'})
    assert response.status_code == 400
    assert plantagenet.User.get(regular_user.id).check_password('password123')


def test_edit_user_post_duplicate_email_returns_400(cl, login, admin_user,
                                                    regular_user):
    login()
    response = cl.post('/users/{}'.format(regular_user.id),
                       data={'email': admin_user.email, 'name': 'User'})
    assert response.status_code == 400


def test_edit_user_post_keeping_own_email_is_allowed(cl, login,
                                                     regular_user):
    login()
    response = cl.post('/users/{}'.format(regular_user.id),
                       data={'email': regular_user.email, 'name': 'Renamed'})
    assert response.status_code == 302
    assert plantagenet.User.get(regular_user.id).name == 'Renamed'


def test_edit_user_post_blank_name_defaults_to_email(cl, login,
                                                     regular_user):
    login()
    cl.post('/users/{}'.format(regular_user.id),
            data={'email': regular_user.email, 'name': ''})

    user = plantagenet.User.get(regular_user.id)
    assert user.name == user.email


def test_delete_user_unauthenticated_returns_401(cl, regular_user):
    response = cl.post('/users/{}/delete'.format(regular_user.id))
    assert response.status_code == 401


def test_delete_user_non_admin_returns_403(cl, login, regular_user):
    login(regular_user)
    response = cl.post('/users/{}/delete'.format(regular_user.id))
    assert response.status_code == 403
    assert plantagenet.User.get(regular_user.id) is not None


def test_delete_user_removes_the_user(cl, login, regular_user):
    user_id = regular_user.id
    login()
    response = cl.post('/users/{}/delete'.format(user_id))
    assert response.status_code == 302
    assert plantagenet.User.get(user_id) is None


def test_delete_user_missing_returns_404(cl, login):
    login()
    response = cl.post('/users/12345/delete')
    assert response.status_code == 404


def test_delete_user_cannot_delete_self(cl, login, admin_user):
    login()
    response = cl.post('/users/{}/delete'.format(admin_user.id))
    assert response.status_code == 400
    assert plantagenet.User.get(admin_user.id) is not None


def test_delete_user_can_delete_another_admin(cl, login, admin_user,
                                              make_user):
    other = make_user('other@example.com', 'Other', is_admin=True)
    other_id = other.id
    login()
    response = cl.post('/users/{}/delete'.format(other_id))
    assert response.status_code == 302
    assert plantagenet.User.get(other_id) is None
