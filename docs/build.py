"""Build the site of eks-platform-lab from the pages in docs/pages/ and the files in parts/.

Usage: python docs/build.py [--out DIR] [--strict]

A part has moved to the site when docs/pages/<part>.html exists. Every page links every part: a part that has
moved to its page, a part that has not to its directory on GitHub. The README of a part that has moved is a stub
that points to the page.

A page is a Jinja template written in the order in which the part is understood and built. Its parts are the
functions of PageBuilder.template_functions():

    {{ page_head("Roll out a new version in steps") }}
    {% call stage("understand") %} {{ section("idea", "The idea") }} ... {% endcall %}
    {% call stage("build") %}
      {% call step("argo-rollouts", "Argo Rollouts") %}
        {% call what() %} what the step puts in place {% endcall %}
        {% call files() %}
          {% call file("parts/...", main=true) %} {{ note("text on the line", "what it says") }} {% endcall %}
          {{ external_link("parts/.../", "label", "https://...") }}
        {% endcall %}
        {% call apply() %}
          {% call command() %}{% call piece("what it does", "what it leads to") %}kubectl ...{% endcall %}{% endcall %}
          {% call ui("the administrator", "Settings|Clusters|in-cluster") %}why{% endcall %}
        {% endcall %}
        {% call confirm() %}
          {% call check("what should be true") %}command{% call output() %}what it prints{% endcall %}{% endcall %}
        {% endcall %}
      {% endcall %}
    {% endcall %}
    {% call stage("use") %} {% call run() %} checks and actions in the UI {% endcall %} {% endcall %}
    {% call stage("wrapup") %} teardown and cost {% endcall %}

A note matches the first line that contains its text; "anchor>>text" matches the first line with the text after the
line with the anchor, and "a||b" matches several lines. In specifications, notes, and checks, `name` is code.
Bodies of commands, checks, and outputs are plain text: the build escapes them.

The checks find references that lead nowhere: files, the lines of notes, paths in commands, links inside a page,
icons, screenshots, and the links between the READMEs and the pages. The shape of a page is not checked.
"""

import argparse
import base64
import hashlib
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup, escape

REPOSITORY = Path(__file__).resolve().parent.parent
SITE_URL = "https://hainet50b.github.io/eks-platform-lab/"
GITHUB_BLOB = "https://github.com/hainet50b/eks-platform-lab/blob/main/"
GITHUB_TREE = "https://github.com/hainet50b/eks-platform-lab/tree/main/"

STAGES = {"understand": "Understand", "build": "Build", "use": "Use", "wrapup": "Wrap up"}
CHECK_HEAD = "What should be true"
RUN_HEAD = "What you do, and what happens"


def as_code(text):
    """Escape text and show `name` as code."""
    return Markup(re.sub(r"`([^`<>\n]+)`", r"<code>\1</code>", str(escape(text))))


def body_text(caller):
    """The body of a call block as written, without the newlines around it."""
    return html.unescape(str(caller())).strip("\n")


PIECE = "\x00{}\x00"  # where a piece stands in the text of its command


def fill_pieces(text, pieces, mark=None):
    """The command with each piece in place: as plain text, or escaped with each piece marked."""
    out = []
    for i, chunk in enumerate(re.split(r"\x00(\d+)\x00", text)):
        if i % 2 == 0:
            out.append(chunk if mark is None else html.escape(chunk))
            continue
        number = int(chunk)
        piece = pieces[number - 1][1]
        out.append(piece if mark is None else str(mark(number, piece)))
    return "".join(out)


def highlight_yaml(line):
    """Escape a YAML line and mark its comment, its key, and its list dash."""
    whole_comment = re.match(r"^(\s*)(#.*)$", line)
    if whole_comment:
        indent, comment = whole_comment.groups()
        return html.escape(indent) + f'<span class="yaml-comment">{html.escape(comment)}</span>'
    code, comment = line, ""
    trailing_comment = re.search(r"\s#\s", line)
    if trailing_comment:
        code, comment = line[: trailing_comment.start()], line[trailing_comment.start() :]
    key = re.match(r"^(\s*)(- )?([\w./-]+)(:)(.*)$", code)
    if key:
        indent, dash, name, _, rest = key.groups()
        marked = html.escape(indent) + ('<span class="yaml-dash">- </span>' if dash else "")
        marked += f'<span class="yaml-key">{html.escape(name)}</span>:' + html.escape(rest)
    else:
        marked = html.escape(code)
    return marked + (f'<span class="yaml-comment">{html.escape(comment)}</span>' if comment else "")


@dataclass(frozen=True)
class Part:
    directory: str  # 60-argo-rollouts
    number: str
    name: str
    description: str
    repository: Path = field(compare=False)

    @property
    def moved(self):
        return (self.repository / "docs" / "pages" / f"{self.directory}.html").exists()

    @property
    def page_url(self):
        return f"{SITE_URL}{self.directory}.html"

    @property
    def href(self):
        return f"{self.directory}.html" if self.moved else f"{GITHUB_TREE}parts/{self.directory}/"


def read_parts(repository):
    """The parts under parts/, with their descriptions from the table of parts in the root README."""
    readme = (repository / "README.md").read_text(encoding="utf-8")
    descriptions = dict(re.findall(r"^\| \[\d+ [\w-]+\]\(parts/([\w-]+)/README\.md\) \| (.*?) \|$", readme, re.M))
    descriptions.update(
        re.findall(r"^\| \[\d+ [\w-]+\]\(" + re.escape(SITE_URL) + r"([\w-]+)\.html\) \| (.*?) \|$", readme, re.M)
    )
    parts = []
    for directory in sorted(d for d in (repository / "parts").iterdir() if d.is_dir() and re.match(r"\d+-", d.name)):
        number, name = directory.name.split("-", 1)
        parts.append(Part(directory.name, number, name, descriptions.get(directory.name, ""), repository))
    return parts


def environment(docs):
    env = Environment(loader=FileSystemLoader([docs, docs / "templates"]), autoescape=True, keep_trailing_newline=True)

    def asset(name):
        """A file in assets/, with a hash of its content, so that a browser loads it again after a change."""
        digest = hashlib.sha256((docs / "assets" / name).read_bytes()).hexdigest()[:10]
        return f"assets/{name}?v={digest}"

    env.globals["asset"] = asset
    return env


class LinkCollector(HTMLParser):
    """The ids of the elements of a page and the targets of its links inside the page."""

    def __init__(self):
        super().__init__()
        self.ids, self.targets = set(), set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if (attributes.get("href") or "").startswith("#"):
            self.targets.add(attributes["href"][1:])


@dataclass
class Frame:
    """An open part of the page, which the parts inside it fill in."""

    kind: str
    data: dict = field(default_factory=dict)


class PageBuilder:
    """Renders one page, and collects its findings."""

    def __init__(self, env, part, parts):
        self.env = env
        self.markup = env.get_template("components.html").module
        self.part = part
        self.parts = parts
        self.repository = part.repository
        self.docs = part.repository / "docs"
        self.own_files = f"parts/{part.directory}/"
        self.findings = []
        self.outline = []
        self.frames = []
        self.steps = 0
        self.explorers = 0

    def add_finding(self, message):
        self.findings.append(message)

    def template_functions(self):
        return {
            name: getattr(self, name)
            for name in (
                "page_head",
                "stage",
                "section",
                "step",
                "what",
                "files",
                "file",
                "note",
                "external_link",
                "apply",
                "command",
                "piece",
                "ui",
                "confirm",
                "run",
                "check",
                "output",
                "icon",
            )
        }

    def build(self):
        """The page as HTML, and the ids of its elements."""
        template = self.env.get_template(f"pages/{self.part.directory}.html")
        content = template.render(**self.template_functions()).strip("\n")
        links = LinkCollector()
        links.feed(content)
        for target in sorted(links.targets - links.ids):
            self.add_finding(f"a link goes to #{target}, which the page does not have")
        current = Markup(f'<span class="part-number">{escape(self.part.number)}</span> {escape(self.part.name)}')
        page = self.env.get_template("layout.html").render(
            title=f"{self.part.number} {self.part.name}",
            current=current,
            current_part=self.part,
            parts=self.parts,
            outline=self.markup.outline(self.outline),
            content=Markup(content),
        )
        return page, links.ids

    # ---- the frame of the page ----

    def page_head(self, title):
        index = self.parts.index(self.part)
        previous = self.parts[index - 1] if index > 0 else None
        following = self.parts[index + 1] if index + 1 < len(self.parts) else None
        return self.markup.page_head(self.part, title, previous, following)

    def icon(self, name):
        svg = self.docs / "icons" / f"{name}.svg"
        if not svg.exists():
            self.add_finding(f"no icon {name} in docs/icons/")
            return ""
        return "data:image/svg+xml;base64," + base64.b64encode(svg.read_bytes()).decode()

    def stage(self, name, caller):
        label = STAGES[name]
        frame = self.open("stage", name=name, sections=[], outline_at=len(self.outline))
        self.outline.append({"kind": "stage", "label": label})
        content = caller()
        self.close(frame)
        sections = frame.data["sections"]
        # a stage whose first section has the stage's name keeps its rule, but not a second title
        label_hidden = bool(sections) and sections[0][1] == label
        if label_hidden:
            stage_item = frame.data["outline_at"]
            del self.outline[stage_item]
            self.outline[stage_item]["kind"] = "stage-section"
        return self.markup.stage(label, label_hidden, content)

    def section(self, section_id, title):
        self.current("stage").data["sections"].append((section_id, title))
        self.outline.append({"kind": "section", "id": section_id, "label": title})
        return self.markup.section(section_id, title)

    # ---- steps ----

    def step(self, step_id, title, caller):
        self.steps += 1
        number = self.steps
        self.outline.append({"kind": "step", "id": step_id, "number": number, "label": title})
        frame = self.open("step", section=f"step {number} ({title})", beats={})
        caller()
        self.close(frame)
        beats = [
            {"label": label, "body": frame.data["beats"][kind]}
            for kind, label in (("what", "What"), ("files", "Write"), ("apply", "Apply"), ("confirm", "Confirm"))
            if kind in frame.data["beats"]
        ]
        return self.markup.step(number, step_id, title, beats)

    def beat(self, kind, body):
        step = self.current("step", required=False)
        if step:
            step.data["beats"][kind] = body
            return ""
        return body

    def section_name(self):
        step = self.current("step", required=False)
        if step:
            return step.data["section"]
        return "run" if self.current("stage").data["name"] == "use" else "teardown"

    def what(self, caller):
        return self.beat("what", caller())

    # ---- files ----

    def files(self, caller):
        frame = self.open("files", files=[], links=[])
        caller()
        self.close(frame)
        missing = [f["source"] for f in frame.data["files"] if not (self.repository / f["source"]).exists()]
        for source in missing:
            self.add_finding(f"{self.section_name()}: the file {source} is not in the repository")
        return self.beat("files", "" if missing else self.explorer(frame.data["files"], frame.data["links"]))

    def file(self, source, main=False, caller=None):
        frame = self.open("file", notes=[])
        if caller:
            caller()
        self.close(frame)
        self.current("files").data["files"].append({"source": source, "main": main, "notes": frame.data["notes"]})
        return ""

    def note(self, match, spec, caller=None):
        reason = caller() if caller else ""
        self.current("file").data["notes"].append({"match": match, "spec": spec, "reason": reason})
        return ""

    def external_link(self, directory, label, href):
        self.current("files").data["links"].append({"directory": directory, "label": label, "href": href})
        return ""

    def display_path(self, path):
        """A path as the page shows it: relative to the part of the page, or "part NN: ..." for another part."""
        if path.startswith(self.own_files):
            return path[len(self.own_files) :]
        other = re.match(r"parts/(\d+)-[^/]+/(.*)", path)
        return f"part {other.group(1)}: {other.group(2)}" if other else path

    def explorer(self, files, links):
        """A tree of the files of a step, and a viewer of the selected one. One file gets the explorer too,
        so that every step reads alike."""
        self.explorers += 1
        shown = [self.display_path(f["source"]) for f in files]
        directories = [path.rsplit("/", 1)[0] + "/" if "/" in path else "" for path in shown] + [
            self.display_path(link["directory"]) for link in links
        ]
        root = directories[0]
        for directory in directories:
            while not directory.startswith(root):
                root = root[: root.rstrip("/").rfind("/") + 1]
        selected = next((i for i, f in enumerate(files) if f["main"]), 0)

        tree = {}
        for i, path in enumerate(shown):
            *folders, name = path[len(root) :].split("/")
            node = tree
            for folder in folders:
                node = node.setdefault(folder + "/", {})
            node[name] = {"kind": "file", "index": i, "other_part": not files[i]["source"].startswith(self.own_files)}
        for link in links:
            node = tree
            for folder in [f for f in self.display_path(link["directory"])[len(root) :].split("/") if f]:
                node = node.setdefault(folder + "/", {})
            node[link["label"]] = {"kind": "link", "href": link["href"]}
        panels = [self.file_figure(f) for f in files]
        return self.markup.explorer(self.explorers, root, self.tree_nodes(tree, 0), selected, panels)

    def tree_nodes(self, tree, depth):
        """The nodes of a tree in the order of a file browser: folders first; a folder with only one folder
        in it shows as one."""
        nodes = []
        for name in sorted(tree, key=lambda key: (not key.endswith("/"), key)):
            entry = tree[name]
            if "kind" in entry:
                nodes.append({**entry, "label": name, "depth": depth})
                continue
            label = name
            while len(entry) == 1 and "kind" not in next(iter(entry.values())):
                only = next(iter(entry))
                label += only
                entry = entry[only]
            nodes.append(
                {"kind": "folder", "label": label, "depth": depth, "children": self.tree_nodes(entry, depth + 1)}
            )
        return nodes

    def file_figure(self, file):
        """A file with its specification: each note is numbered, and so are the lines that it is about."""
        source = file["source"]
        lines = (self.repository / source).read_text(encoding="utf-8").rstrip("\n").split("\n")
        pins = {}
        for number, note in enumerate(file["notes"], 1):
            for text in note["match"].split("||"):
                start = 0
                if ">>" in text:
                    anchor, text = text.split(">>", 1)
                    start = next((i for i, line in enumerate(lines) if anchor in line), len(lines))
                found = next((i for i in range(start, len(lines)) if text in lines[i]), None)
                if found is None:
                    self.add_finding(f"{source}: no line has the text {text!r} of a note")
                    continue
                pins.setdefault(found, []).append(number)
        notes = [
            {"number": number, "spec": as_code(note["spec"]), "reason": as_code(note["reason"])}
            for number, note in enumerate(file["notes"], 1)
        ]
        highlight = highlight_yaml if source.endswith((".yaml", ".yml", ".tf")) else html.escape
        rows = [
            {"number": i + 1, "html": Markup(highlight(line)), "pins": pins.get(i, [])} for i, line in enumerate(lines)
        ]
        return self.markup.file_figure(source, self.display_path(source), GITHUB_BLOB + source, rows, notes)

    # ---- commands, checks, and actions in the UI ----

    def apply(self, caller):
        frame = self.open("apply")
        content = caller()
        self.close(frame)
        return self.beat("apply", content)

    def command(self, caller):
        frame = self.open("command", pieces=[])
        text = body_text(caller)
        self.close(frame)
        pieces = frame.data["pieces"]
        plain = fill_pieces(text, pieces)
        section = self.section_name()
        for path in re.findall(r"parts/[\w./-]+", plain):
            if not (self.repository / path.rstrip("/.")).exists():
                self.add_finding(f"{section}: the command refers to {path}, which the repository does not have")
        marked = Markup(fill_pieces(text, pieces, self.markup.command_part)).rstrip()
        items = [{"text": as_code(description), "reason": as_code(reason)} for description, _, reason in pieces]
        return self.markup.command_card(items, marked)

    def piece(self, description, reason="", caller=None):
        """A piece of a command, numbered, with what it does and, if it helps, what it leads to."""
        pieces = self.current("command").data["pieces"]
        pieces.append((description, body_text(caller), reason))
        return PIECE.format(len(pieces))

    def confirm(self, caller):
        return self.beat("confirm", self.checks(caller, CHECK_HEAD))

    def run(self, caller):
        return self.checks(caller, RUN_HEAD)

    def checks(self, caller, head):
        frame = self.open("checks", rows=[], head=head)
        caller()
        self.close(frame)
        return self.markup.check_table(head, frame.data["rows"])

    def check(self, statement, caller):
        table = self.current("checks")
        frame = self.open("check", output="")
        command = body_text(caller)
        self.close(frame)
        output = frame.data["output"]
        number = len(table.data["rows"]) + 1
        table.data["rows"].append(
            self.markup.check_row(table.data["head"], number, as_code(statement), command, output)
        )
        return ""

    def output(self, caller):
        self.current("check").data["output"] = body_text(caller)
        return ""

    def ui(self, who, path, opens_url=False, screenshot=None, caller=None):
        """An action in the Argo CD UI: a row in a table of checks, or a sentence in Apply."""
        items = path.split("|")
        section = self.section_name()
        note = Markup(str(caller()).strip()) if caller else ""
        figure = ""
        if screenshot:
            if not (self.docs / screenshot).exists():
                self.add_finding(f"{section}: the screenshot {screenshot} is not in docs/")
            figure = self.markup.screenshot(screenshot, " > ".join(items))
        ui_path = self.markup.ui_path(items)
        table = self.current("checks", required=False)
        if table:
            number = len(table.data["rows"]) + 1
            table.data["rows"].append(
                self.markup.ui_row(table.data["head"], number, as_code(note), who, ui_path, figure)
            )
            return ""
        # open: the first action in the UI, right after the command that prints the URL
        lead = f"Open the URL, sign in as {who}, and select" if opens_url else f"In the Argo CD UI, as {who}, select"
        return self.markup.ui_sentence(lead, ui_path, note, figure)

    # ---- frames ----

    def open(self, kind, **data):
        frame = Frame(kind, data)
        self.frames.append(frame)
        return frame

    def close(self, frame):
        assert self.frames.pop() is frame

    def current(self, kind, required=True):
        frame = next((f for f in reversed(self.frames) if f.kind == kind), None)
        if required and frame is None:
            raise ValueError(f"{kind}() is missing around this part of the page")
        return frame


def check_readmes(repository, parts, page_ids):
    """The root README links to the pages, and the README of a part that has moved is a stub."""
    findings = []
    readme = (repository / "README.md").read_text(encoding="utf-8")
    for part in parts:
        if not part.moved:
            continue
        if re.search(rf"\]\(parts/{part.directory}/README\.md", readme):
            findings.append(f"README.md links to parts/{part.directory}/README.md; link to {part.page_url} instead")
        for section_id in re.findall(re.escape(part.page_url) + r"#([\w-]+)", readme):
            if section_id not in page_ids[part.directory]:
                findings.append(f"README.md links to {part.directory}.html#{section_id}, which the page does not have")
        stub = repository / "parts" / part.directory / "README.md"
        text = stub.read_text(encoding="utf-8") if stub.exists() else ""
        if part.page_url not in text or len(text.strip().split("\n")) > 6:
            findings.append(f"parts/{part.directory}/README.md is not the stub that points to {part.page_url}")
    return findings


def build(repository, out):
    """Write the site to out, and return the findings of the checks."""
    docs = repository / "docs"
    out.mkdir(parents=True, exist_ok=True)
    for directory in ("assets", "images"):
        if (docs / directory).is_dir():
            shutil.copytree(docs / directory, out / directory, dirs_exist_ok=True)
    env = environment(docs)
    parts = read_parts(repository)
    findings, page_ids = [], {}
    for part in parts:
        if not part.moved:
            continue
        builder = PageBuilder(env, part, parts)
        page, page_ids[part.directory] = builder.build()
        findings += [f"{part.directory}: {finding}" for finding in builder.findings]
        (out / f"{part.directory}.html").write_text(page, encoding="utf-8", newline="\n")
    index = env.get_template("index.html").render(parts=parts).strip("\n")
    page = env.get_template("layout.html").render(
        title=None,
        current="Parts",
        current_part=None,
        parts=parts,
        outline=Markup('<li><a href="#parts">Parts</a></li>'),
        content=Markup(index),
    )
    (out / "index.html").write_text(page, encoding="utf-8", newline="\n")
    return findings + check_readmes(repository, parts, page_ids)


def main(argv):
    parser = argparse.ArgumentParser(description="Build the site of eks-platform-lab.")
    parser.add_argument("--out", type=Path, default=REPOSITORY / "_site", help="where to write the site")
    parser.add_argument("--strict", action="store_true", help="exit with an error when the checks find anything")
    args = parser.parse_args(argv)
    findings = build(REPOSITORY, args.out)
    print(f"checks: {'OK' if not findings else str(len(findings)) + ' finding(s)'}")
    for finding in findings:
        print("  - " + finding)
    return 1 if findings and args.strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
