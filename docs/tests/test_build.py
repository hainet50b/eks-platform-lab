"""Tests of the build: the checks find references that lead nowhere."""

import shutil

import build


def make_repository(root, page):
    """A repository with one part, 10-sample, whose page is the given source."""
    shutil.copytree(build.REPOSITORY / "docs" / "templates", root / "docs" / "templates")
    (root / "docs" / "pages").mkdir(parents=True)
    (root / "docs" / "pages" / "10-sample.html").write_text(page, encoding="utf-8")
    manifests = root / "parts" / "10-sample" / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "a.yaml").write_text("kind: ConfigMap\nmetadata:\n  name: a\n", encoding="utf-8")
    url = f"{build.SITE_URL}10-sample.html"
    (root / "parts" / "10-sample" / "README.md").write_text(f"# 10 sample\n\n{url}\n", encoding="utf-8")
    (root / "README.md").write_text(f"| [10 sample]({url}) | A sample |\n", encoding="utf-8")
    return root


PAGE = """{{ page_head("A sample") }}
{% call stage("build") %}
{% call step("first", "First") %}
{% call files() %}
{% call file("parts/10-sample/manifests/a.yaml") %}{{ note("name: a", "A note.") }}{% endcall %}
{% endcall %}
{% call apply() %}{% call command() %}kubectl apply -f parts/10-sample/manifests/a.yaml{% endcall %}{% endcall %}
{% endcall %}
{% endcall %}
<a href="#first">a link</a>
"""


def test_a_page_whose_references_lead_somewhere_has_no_findings(tmp_path):
    repository = make_repository(tmp_path / "repository", PAGE)
    assert build.build(repository, tmp_path / "site") == []


def test_the_checks_find_references_that_lead_nowhere(tmp_path):
    page = (
        PAGE.replace('note("name: a"', 'note("no such text"')
        .replace("apply -f parts/10-sample/manifests/a.yaml", "apply -f parts/10-sample/manifests/b.yaml")
        .replace("#first", "#nowhere")
        .replace("{% endcall %}\n{% endcall %}\n<a", '{{ icon("aws/none") }}{% endcall %}\n{% endcall %}\n<a')
    )
    repository = make_repository(tmp_path / "repository", page)
    findings = build.build(repository, tmp_path / "site")
    assert findings == [
        "10-sample: parts/10-sample/manifests/a.yaml: no line has the text 'no such text' of a note",
        "10-sample: step 1 (First): the command refers to parts/10-sample/manifests/b.yaml, "
        "which the repository does not have",
        "10-sample: no icon aws/none in docs/icons/",
        "10-sample: a link goes to #nowhere, which the page does not have",
    ]
