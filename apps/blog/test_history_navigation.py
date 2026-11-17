from dataclasses import replace

from apps.blog.markdown import render_blog_markdown
from apps.blog.services import django_history_html, django_history_schema, get_blog_post


def test_history_sections_have_consistent_fixed_navigation_and_schema():
    post = get_blog_post("verify-django-history-write-paths")
    body = django_history_html(post)
    steps = django_history_schema(post)["@graph"][0]["step"]
    assert len(steps) == 6
    for step in steps:
        number = step["position"]
        assert f'<h2 id="history-step-{number}">{number}. {step["name"]}</h2>' in body
    # A content-supplied id is still stripped; only exact known headings are decorated later.
    untrusted = render_blog_markdown('<h2 id="arbitrary">Other heading</h2>')
    assert 'id="arbitrary"' not in untrusted
    assert django_history_html(replace(post, html=untrusted)) == untrusted
