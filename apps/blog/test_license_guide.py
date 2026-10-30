import re
from html import unescape
from urllib.parse import parse_qs, urlsplit

from apps.blog.services import get_blog_post


def test_license_guide_preserves_dual_license_search_and_versioned_evidence():
    post = get_blog_post("filter-github-repositories-by-license")
    links = [unescape(value) for value in re.findall(r'href="([^"]+)"', post.html)]
    searches = [parse_qs(urlsplit(link).query) for link in links if link.startswith("/repos/?")]

    for license_name in ("MIT", "Unlicense"):
        assert {"q": ["ripgrep"], "license": [license_name]} in searches
    assert {"q": ["ripgrep"]} in searches
    evidence = [
        re.fullmatch(
            r"https://github.com/BurntSushi/ripgrep/blob/([0-9a-f]{40})/(COPYING|Cargo.toml)", link
        )
        for link in links
    ]
    pinned_files = {(match[1], match[2]) for match in evidence if match}
    assert len({revision for revision, _ in pinned_files}) == 1
    assert {filename for _, filename in pinned_files} == {"COPYING", "Cargo.toml"}
    assert "NOASSERTION" in post.html
