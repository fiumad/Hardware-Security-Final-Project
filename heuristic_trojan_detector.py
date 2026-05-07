"""Lightweight static heuristic detector for generated Trojaned Verilog.

The detector is intentionally explainable. It scores rare trigger evidence,
payload evidence, and whether the two are syntactically linked. It does not
use the literal word "trojan" as a scoring feature.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


TRIGGER_NAME_RE = re.compile(
    r"\b(?:trigger\w*|active|activated|enable\w*|auth\w*|key\w*|pattern\w*|sequence\w*)\b",
    re.IGNORECASE,
)
COUNTER_NAME_RE = re.compile(r"\b\w*(?:count|counter|cnt)\w*\b", re.IGNORECASE)
LEAK_NAME_RE = re.compile(r"\b\w*(?:leak|secret|shadow|covert|buffer|parity)\w*\b", re.IGNORECASE)
POWER_NAME_RE = re.compile(r"\b\w*(?:power|sink|toggle|lfsr|thermal|shift)\w*\b", re.IGNORECASE)

VERILOG_CONST_RE = re.compile(r"\b\d+'[bhd][0-9a-fA-F_xXzZ]+\b")
RARE_CONST_RE = re.compile(
    r"\b(?:16'h[fF]{4}|8'h(?:[fF]{2}|03)|32'h55555555|0x(?:FFFF|FF|03|EE)|255|65535|65,535)\b"
)
ASSIGN_RE = re.compile(r"(?:assign\s+)?(?P<lhs>\w+)\s*(?:<=|=)\s*(?P<rhs>[^;]+);")
PORT_RE = re.compile(r"\b(?P<direction>input|output)\b(?:\s+(?:wire|reg))?(?:\s+\[[^\]]+\])?\s+(?P<names>[^;,)]+)")
REG_RE = re.compile(r"\breg\b(?:\s+\[[^\]]+\])?\s+(?P<names>[^;]+);")


@dataclass
class DetectionResult:
    file: str
    known_type: str
    predicted_type: str
    risk: str
    trigger_score: int
    payload_score: int
    link_score: int
    total_score: int
    detection_pass: bool
    classification_pass: bool
    trigger_evidence: list[str]
    payload_evidence: list[str]
    link_evidence: list[str]

    def to_row(self) -> dict[str, object]:
        return {
            "file": self.file,
            "known_type": self.known_type,
            "predicted_type": self.predicted_type,
            "risk": self.risk,
            "trigger_score": self.trigger_score,
            "payload_score": self.payload_score,
            "link_score": self.link_score,
            "total_score": self.total_score,
            "detection_pass": self.detection_pass,
            "classification_pass": self.classification_pass,
            "trigger_evidence": "; ".join(self.trigger_evidence[:3]),
            "payload_evidence": "; ".join(self.payload_evidence[:3]),
            "link_evidence": "; ".join(self.link_evidence[:3]),
        }


def strip_comments(verilog: str) -> str:
    """Remove Verilog comments before scoring so marker comments do not drive results."""
    verilog = re.sub(r"/\*.*?\*/", "", verilog, flags=re.DOTALL)
    verilog = re.sub(r"//.*", "", verilog)
    return verilog


def split_names(names: str) -> list[str]:
    clean = names.replace("\n", " ")
    return [name.strip().split()[-1] for name in clean.split(",") if name.strip()]


def extract_ports(verilog: str) -> tuple[set[str], set[str]]:
    inputs: set[str] = set()
    outputs: set[str] = set()
    header = verilog[: verilog.find(");") + 2] if ");" in verilog else verilog
    for match in PORT_RE.finditer(header):
        names = split_names(match.group("names"))
        if match.group("direction") == "input":
            inputs.update(names)
        else:
            outputs.update(names)
    return inputs, outputs


def extract_regs(verilog: str) -> set[str]:
    regs: set[str] = set()
    for match in REG_RE.finditer(verilog):
        regs.update(split_names(match.group("names")))
    return regs


def infer_known_type(path: Path) -> str:
    match = re.search(r"_H(T[1-4])_", path.name)
    return match.group(1) if match else "Clean"


def add_feature(score: int, evidence: list[str], points: int, message: str) -> int:
    evidence.append(f"+{points} {message}")
    return score + points


def analyze_verilog_file(path: str | Path) -> DetectionResult:
    path = Path(path)
    original = path.read_text()
    verilog = strip_comments(original)
    lines = verilog.splitlines()
    inputs, outputs = extract_ports(verilog)
    regs = extract_regs(verilog)
    known_type = infer_known_type(path)

    trigger_score = 0
    payload_score = 0
    link_score = 0
    trigger_evidence: list[str] = []
    payload_evidence: list[str] = []
    link_evidence: list[str] = []
    type_scores = {"T1": 0, "T2": 0, "T3": 0, "T4": 0}
    rare_trigger_present = False

    counter_names = {name for name in regs if COUNTER_NAME_RE.search(name)}
    trigger_names = {name for name in regs if TRIGGER_NAME_RE.search(name)}
    leak_names = {name for name in regs | outputs if LEAK_NAME_RE.search(name)}
    power_names = {name for name in regs if POWER_NAME_RE.search(name)}

    if counter_names:
        trigger_score = add_feature(
            trigger_score,
            trigger_evidence,
            1,
            f"counter-like state: {', '.join(sorted(counter_names)[:4])}",
        )

    if trigger_names:
        trigger_score = add_feature(
            trigger_score,
            trigger_evidence,
            1,
            f"trigger/active/key state: {', '.join(sorted(trigger_names)[:4])}",
        )

    long_counter_patterns = [
        r"==\s*16'h[fF]{4}",
        r">=\s*16'h[fF]{4}",
        r"==\s*255\b",
        r">=\s*255\b",
        r"==\s*65535\b",
        r">=\s*65535\b",
        r"==\s*65,535\b",
    ]
    if any(re.search(pattern, verilog) for pattern in long_counter_patterns):
        trigger_score = add_feature(trigger_score, trigger_evidence, 3, "long counter threshold")
        rare_trigger_present = True

    rare_conditions = re.findall(r"\b\w+\s*==\s*(?:8'h(?:[fF]{2}|03)|16'h[fF]{4}|32'h55555555|\d+)", verilog)
    if rare_conditions:
        trigger_score = add_feature(
            trigger_score,
            trigger_evidence,
            2,
            f"rare constant compare: {rare_conditions[0].strip()}",
        )
        rare_trigger_present = True

    if re.search(r"\bif\s*\([^)]*(?:&&|\|\|)[^)]*\)", verilog):
        trigger_score = add_feature(trigger_score, trigger_evidence, 1, "compound trigger condition")

    sequence_hits = len(re.findall(r"\b(?:state|sequence|pattern|buffer)\w*\s*(?:<=|=)\s*[\w']+", verilog, re.I))
    if sequence_hits >= 2:
        trigger_score = add_feature(trigger_score, trigger_evidence, 2, "sequence/state detector behavior")
        type_scores["T2"] += 2

    sticky_latches = re.findall(r"\b(\w*(?:active|triggered|enable)\w*)\s*<=\s*1'b1", verilog, re.I)
    if sticky_latches:
        trigger_score = add_feature(
            trigger_score,
            trigger_evidence,
            2,
            f"sticky trigger latch: {sticky_latches[0]}",
        )
        rare_trigger_present = True

    if leak_names:
        payload_score = add_feature(
            payload_score,
            payload_evidence,
            2,
            f"leak/shadow/covert signal: {', '.join(sorted(leak_names)[:4])}",
        )
        type_scores["T2"] += 3

    if LEAK_NAME_RE.search(verilog) and not leak_names:
        payload_score = add_feature(payload_score, payload_evidence, 1, "leak/secret/shadow identifier")
        type_scores["T2"] += 2

    if outputs and any(name for name in outputs if LEAK_NAME_RE.search(name)):
        payload_score = add_feature(payload_score, payload_evidence, 2, "covert-looking output port")
        type_scores["T2"] += 2

    output_assigns = []
    for match in ASSIGN_RE.finditer(verilog):
        lhs = match.group("lhs")
        rhs = match.group("rhs")
        if lhs in outputs:
            output_assigns.append((lhs, rhs))

    forced_constants = [(lhs, rhs) for lhs, rhs in output_assigns if re.search(r"\b(?:1'b[01]|8'h[0-9a-fA-F]{2}|32'h[0-9a-fA-F]+|0)\b", rhs)]
    if forced_constants:
        payload_score = add_feature(
            payload_score,
            payload_evidence,
            3,
            f"output forced to constant: {forced_constants[0][0]} <= {forced_constants[0][1].strip()}",
        )

    corruption_patterns = [
        r"~\s*\w+",
        r"\+\s*(?:1|2|1'b1|8'h01)",
        r"\^\s*\w+",
        r"\b8'h(?:EE|00)\b",
    ]
    if any(re.search(pattern, verilog, re.I) for pattern in corruption_patterns):
        payload_score = add_feature(payload_score, payload_evidence, 2, "bit/arithmetic corruption pattern")
        type_scores["T1"] += 2

    if re.search(r"\b(?:parity|\^|xor)\b", verilog, re.I) or any("^" in rhs for _, rhs in output_assigns):
        payload_score = add_feature(payload_score, payload_evidence, 2, "XOR/parity/modulation logic")
        type_scores["T2"] += 2

    high_toggle = re.search(
        r"\w+\s*<=\s*(?:~\s*\w+|~\s*{[^}]+}|\w+\s*\+\s*32'h55555555)",
        verilog,
    )
    power_specific_names = {
        name
        for name in regs
        if re.search(r"(?:power|sink|toggle|lfsr|thermal)", name, re.IGNORECASE)
    }
    wide_power_state = bool(power_specific_names) and bool(re.search(r"reg\s+\[[1-9]\d*:\s*0\]", verilog))
    if high_toggle and wide_power_state:
        payload_score = add_feature(
            payload_score,
            payload_evidence,
            3,
            f"high-toggle state: {high_toggle.group(0).strip()}",
        )
        type_scores["T4"] += 4

    if any(re.search(rf"\b{name}\b", "\n".join(rhs for _, rhs in output_assigns)) for name in leak_names):
        payload_score = add_feature(payload_score, payload_evidence, 3, "output depends on shadow/leak signal")
        type_scores["T2"] += 3

    if re.search(r"\b(?:tx|data_out|result)\s*<=\s*(?:1'b1|8'h00)", verilog):
        payload_score = add_feature(payload_score, payload_evidence, 3, "DoS-style forced idle/zero output")

    dos_active_override = re.search(
        r"if\s*\([^)]*(?:active|triggered)[^)]*\)\s*begin\s*\w+\s*(?:<=|=)\s*(?:1'b1|8'h00)",
        verilog,
        re.IGNORECASE | re.DOTALL,
    ) or re.search(
        r"\w+\s*(?:<=|=)\s*\w*(?:active|triggered)\w*\s*\?\s*(?:1'b1|8'h00)\s*:",
        verilog,
        re.IGNORECASE,
    )
    if dos_active_override:
        type_scores["T3"] += 4

    link_terms = sorted(trigger_names | counter_names | {"active", "triggered", "trojan_active"})
    for idx, line in enumerate(lines):
        if "if" not in line:
            continue
        if not any(re.search(rf"\b{re.escape(term)}\b", line) for term in link_terms):
            continue
        window = "\n".join(lines[idx : idx + 8])
        if ASSIGN_RE.search(window):
            link_score = add_feature(link_score, link_evidence, 2, f"payload assignment near trigger guard: {line.strip()}")
            break

    has_suspicious_name = bool(trigger_names or leak_names or power_specific_names)
    if not rare_trigger_present and not has_suspicious_name:
        risk = "Low" if trigger_score + payload_score + link_score >= 4 else "None"
    elif trigger_score >= 4 and payload_score >= 4 and link_score >= 2:
        risk = "High"
    elif trigger_score + payload_score + link_score >= 7 and (trigger_score >= 3 or payload_score >= 3):
        risk = "Medium"
    elif trigger_score + payload_score + link_score >= 4:
        risk = "Low"
    else:
        risk = "None"

    if risk in {"Low", "None"}:
        predicted_type = "Unknown"
    elif type_scores["T4"] >= 4:
        predicted_type = "T4"
    elif type_scores["T3"] >= 3:
        predicted_type = "T3"
    elif type_scores["T2"] >= 3:
        predicted_type = "T2"
    elif type_scores["T1"] >= 2:
        predicted_type = "T1"
    else:
        predicted_type = "Unknown"

    detection_pass = risk in {"Medium", "High"}
    classification_pass = known_type == predicted_type if known_type.startswith("T") else predicted_type == "Unknown"

    return DetectionResult(
        file=str(path),
        known_type=known_type,
        predicted_type=predicted_type,
        risk=risk,
        trigger_score=trigger_score,
        payload_score=payload_score,
        link_score=link_score,
        total_score=trigger_score + payload_score + link_score,
        detection_pass=detection_pass,
        classification_pass=classification_pass,
        trigger_evidence=trigger_evidence,
        payload_evidence=payload_evidence,
        link_evidence=link_evidence,
    )


def iter_verilog_files(root: str | Path) -> Iterable[Path]:
    root = Path(root)
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob("*.v")):
        if ".ipynb_checkpoints" not in path.parts:
            yield path


def scan_directory(root: str | Path) -> list[DetectionResult]:
    return [analyze_verilog_file(path) for path in iter_verilog_files(root)]


def summarize_results(results: list[DetectionResult]) -> dict[str, object]:
    total = len(results)
    detected = sum(result.detection_pass for result in results)
    classified = sum(result.classification_pass for result in results if result.known_type.startswith("T"))
    vulnerable = sum(result.known_type.startswith("T") for result in results)
    by_risk = {risk: sum(result.risk == risk for result in results) for risk in ["High", "Medium", "Low", "None"]}
    return {
        "total": total,
        "detected": detected,
        "detection_rate": detected / total if total else 0.0,
        "vulnerable": vulnerable,
        "classified": classified,
        "classification_rate": classified / vulnerable if vulnerable else 0.0,
        "by_risk": by_risk,
    }


def print_results_table(results: list[DetectionResult]) -> None:
    columns = [
        "File",
        "Known",
        "Pred",
        "Risk",
        "Trig",
        "Payload",
        "Link",
        "Detect",
        "Class",
    ]
    rows = []
    for result in results:
        rows.append(
            [
                Path(result.file).name,
                result.known_type,
                result.predicted_type,
                result.risk,
                str(result.trigger_score),
                str(result.payload_score),
                str(result.link_score),
                "PASS" if result.detection_pass else "FAIL",
                "PASS" if result.classification_pass else "FAIL",
            ]
        )
    widths = [max(len(row[idx]) for row in [columns] + rows) for idx in range(len(columns))]
    print(" | ".join(col.ljust(widths[idx]) for idx, col in enumerate(columns)))
    print("-|-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row)))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run heuristic Trojan detection on Verilog files")
    parser.add_argument("root", nargs="?", default="trojan_outputs", help="Verilog file or directory to scan")
    args = parser.parse_args()

    scan_results = scan_directory(args.root)
    print_results_table(scan_results)
    print()
    print(summarize_results(scan_results))
