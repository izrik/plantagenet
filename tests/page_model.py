from datetime import datetime

import plantagenet
from plantagenet import app


def test_get_unique_slug_no_collision(ctx):
    slug = plantagenet.Page.get_unique_slug('My Page')
    assert slug == 'my-page'


def test_get_unique_slug_collision(ctx):
    page1 = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
    app.db.session.add(page1)
    app.db.session.commit()

    slug = plantagenet.Page.get_unique_slug('My Page')
    assert slug != 'my-page'
    assert 'my-page' in slug


def test_get_unique_slug_multiple_collisions(ctx):
    page1 = plantagenet.Page('Dup', 'content', datetime(2024, 1, 1))
    app.db.session.add(page1)
    app.db.session.commit()

    page2 = plantagenet.Page('Dup', 'content', datetime(2024, 1, 2))
    app.db.session.add(page2)
    app.db.session.commit()

    slug = plantagenet.Page.get_unique_slug('Dup')
    assert slug not in ('dup',)
