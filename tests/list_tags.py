from datetime import datetime

import plantagenet
from plantagenet import app


def test_list_tags_returns_200(cl):
    # when
    response = cl.get('/tags')

    # then
    assert response.status_code == 200


def test_list_tags_shows_tag_with_published_post(cl):
    # given a tag with one published post
    tag = plantagenet.Tag('mytag')
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    # when an unauthenticated user visits /tags
    response = cl.get('/tags')

    # then the tag is visible
    assert b'mytag' in response.data


def test_list_tags_hides_tag_with_only_draft_posts(cl):
    # given a tag whose only post is a draft
    tag = plantagenet.Tag('drafttag')
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            is_draft=True)
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    # when an unauthenticated user visits /tags
    response = cl.get('/tags')

    # then the tag is not visible
    assert b'drafttag' not in response.data


def test_list_tags_authenticated_shows_tag_with_only_draft_posts(cl, login):
    # given a tag whose only post is a draft
    tag = plantagenet.Tag('drafttag')
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            is_draft=True)
    post.tags.append(tag)
    app.db.session.add(post)
    app.db.session.commit()

    # when an authenticated user visits /tags
    login()
    response = cl.get('/tags')

    # then the tag is visible
    assert b'drafttag' in response.data
