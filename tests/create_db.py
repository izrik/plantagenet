import plantagenet
from plantagenet import app


def test_create_db_command():
    # db.create_all() runs at startup, so tables already exist.
    # cmd_create_db() should be idempotent and run without error.
    plantagenet.cmd_create_db()

    with app.app_context():
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Post)).first() is None
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Tag)).first() is None
        assert plantagenet.db.session.execute(
            plantagenet.db.select(plantagenet.Option)).first() is None
