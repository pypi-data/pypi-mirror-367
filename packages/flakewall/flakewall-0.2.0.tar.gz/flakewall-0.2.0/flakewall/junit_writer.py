from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Iterable, Optional, Tuple


def split_test_id(test_id: str) -> Tuple[Optional[str], str]:
    if "::" in test_id:
        cls, name = test_id.split("::", 1)
        return cls, name
    return None, test_id


def write_junit_report(
    output_path: Path,
    suite_name: str,
    outcomes: Iterable[tuple[str, str, bool]],
    # outcomes: (test_id, status, flaky) where status in {pass, fail, error, skipped}
) -> None:
    testsuite = ET.Element("testsuite", attrib={"name": suite_name})
    for test_id, status, flaky in outcomes:
        classname, name = split_test_id(test_id)
        attrs = {"name": name}
        if classname:
            attrs["classname"] = classname
        tc = ET.SubElement(testsuite, "testcase", attrib=attrs)
        if flaky:
            props = ET.SubElement(tc, "properties")
            ET.SubElement(props, "property", attrib={"name": "flakewall_flaky", "value": "true"})
        if status == "fail":
            ET.SubElement(tc, "failure")
        elif status == "error":
            ET.SubElement(tc, "error")
        elif status == "skipped":
            ET.SubElement(tc, "skipped")
        # pass -> no child

    tree = ET.ElementTree(testsuite)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
