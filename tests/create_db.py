import pytest
from sqlalchemy.exc import OperationalError

import plantagenet
from plantagenet import app


def test_create_db_command():
    # given an app with uninitialized database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    app.testing = True

    # precondition: the database tables have not been created yet
    with app.app_context():
        def query_post():
            plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Post)).first()

        def query_tag():
            plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Tag)).first()

        def query_option():
            plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Option)).first()

        with pytest.raises(OperationalError):
            query_post()
        plantagenet.db.session.rollback()
        with pytest.raises(OperationalError):
            query_tag()
        plantagenet.db.session.rollback()
        with pytest.raises(OperationalError):
            query_option()
        plantagenet.db.session.rollback()

    # when the create_db function is called
    plantagenet.cmd_create_db()

    # then the database tables are created
    with app.app_context():
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Post)).first() is None
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Tag)).first() is None
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Option)).first() is None
