"""Parser for the manifest tree (`xmltree` dump of `AndroidManifest.xml`).

The dump is an indented tree: `E: <element> (line=N)` for elements and `A: <attribute>=<value>`
for the attributes of the element one level above. Declared components are the children of
`application`; their intent-filter actions become separate artifacts. A component that does not
fit (no `name`) is a `failed` row that keeps its element line. Names stay as printed (they may
be relative, such as `.Main`); the normalizer qualifies them.
"""

import re
from dataclasses import dataclass, field

from app.core import raw_sources
from app.parsing.apk_static._common import BundleParser
from app.parsing.base import ParsedArtifact

COMPONENT_KINDS = frozenset({"activity", "activity-alias", "receiver", "service", "provider"})
_LINE = re.compile(r"(?P<indent> *)(?P<kind>[NEA]): (?P<rest>.*)")
_ELEMENT = re.compile(r"(?P<name>[A-Za-z][A-Za-z0-9_.\-]*) \(line=\d+\)")
_QUOTED = re.compile(r'"(?P<value>.*?)"(?: \(Raw: ".*"\))?')


@dataclass
class _Element:
    name: str
    indent: int
    line_no: int
    raw: str
    attributes: dict[str, str] = field(default_factory=dict)
    children: list["_Element"] = field(default_factory=list)


class ApkManifestParser(BundleParser):
    parser_name = "apk_static.manifest"
    raw_source = raw_sources.STATIC_MANIFEST
    artifact_type = "apk_component"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        root, problems = self._tree(lines)
        if root is None or root.name != "manifest":
            return self.whole_failure(package, lines[0][1], "pohon tidak berakar pada 'manifest'")
        declared = root.attributes.get("package")
        if declared is None:
            return self.whole_failure(package, lines[0][1], "atribut package tidak ada")
        if declared != package:
            return self.whole_failure(
                package, lines[0][1], f"paket pada manifes ({declared}) tidak sama dengan parameter"
            )

        rows: list[ParsedArtifact] = [
            self.failed_line(self.artifact_type, package, number, line, note)
            for number, line, note in problems
        ]
        seen_actions: set[tuple[str, str]] = set()
        for application in (c for c in root.children if c.name == "application"):
            for component in (c for c in application.children if c.name in COMPONENT_KINDS):
                name = component.attributes.get("name")
                if not name:
                    rows.append(
                        self.failed_line(
                            self.artifact_type,
                            package,
                            component.line_no,
                            component.raw,
                            "komponen tanpa atribut name",
                        )
                    )
                    continue
                rows.append(
                    self.artifact(
                        self.artifact_type,
                        package,
                        component.raw,
                        {
                            "kind": component.name,
                            "name": name,
                            "package": package,
                            "permission": component.attributes.get("permission"),
                            "exported": _boolean(component.attributes.get("exported")),
                            "enabled": _boolean(component.attributes.get("enabled")),
                            "line_no": component.line_no,
                        },
                    )
                )
                for action, number in _actions(component):
                    if (name, action) in seen_actions:
                        continue
                    seen_actions.add((name, action))
                    rows.append(
                        self.artifact(
                            "apk_intent_action",
                            package,
                            f"{component.raw} -> {action}",
                            {
                                "component": name,
                                "action": action,
                                "package": package,
                                "line_no": number,
                            },
                        )
                    )
        return rows

    @staticmethod
    def _tree(
        lines: list[tuple[int, str]],
    ) -> tuple[_Element | None, list[tuple[int, str, str]]]:
        """The element tree and the lines that did not fit it."""
        root: _Element | None = None
        stack: list[_Element] = []
        problems: list[tuple[int, str, str]] = []
        for number, line in lines:
            match = _LINE.fullmatch(line)
            if match is None:
                problems.append((number, line, "baris tidak sesuai bentuk pohon manifes"))
                continue
            indent, kind, rest = len(match["indent"]), match["kind"], match["rest"]
            if kind == "N":
                continue  # namespace declarations carry no claim
            if kind == "E":
                element = _ELEMENT.fullmatch(rest)
                if element is None:
                    problems.append((number, line, "baris elemen tidak dikenal"))
                    continue
                node = _Element(element["name"], indent, number, line.strip())
                while stack and stack[-1].indent >= indent:
                    stack.pop()
                if stack:
                    stack[-1].children.append(node)
                elif root is None:
                    root = node
                else:
                    problems.append((number, line, "lebih dari satu elemen akar"))
                    continue
                stack.append(node)
                continue
            owner = stack[-1] if stack else None
            if owner is None or indent != owner.indent + 2:
                problems.append((number, line, "atribut tanpa elemen pemilik"))
                continue
            key, _, value = rest.partition("=")
            name = re.sub(r"\(0x[0-9a-fA-F]+\)$", "", key.rsplit(":", 1)[-1])
            if not name or value == "":
                problems.append((number, line, "atribut tidak dikenal"))
                continue
            quoted = _QUOTED.fullmatch(value)
            owner.attributes.setdefault(name, quoted["value"] if quoted else value)
        return root, problems


def _boolean(value: str | None) -> bool | None:
    return {"true": True, "false": False}.get(value or "")


def _actions(component: _Element) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for node in component.children:
        if node.name != "intent-filter":
            continue
        for child in node.children:
            action = child.attributes.get("name")
            if child.name == "action" and action:
                result.append((action, child.line_no))
    return result
