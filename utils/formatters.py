import json


def to_markdown(digest):
    lines = [f"# Your News Digest ({digest['date']})", ""]
    for interest, items in digest["sections"].items():
        lines.append(f"## {interest}")
        for it in items:
            lines.append(f"### [{it['title']}]({it['link']})")
            meta = " · ".join(x for x in [it["source"], it["published"]] if x)
            if meta:
                lines.append(f"*{meta}*")
            lines.append(it["summary"])
            lines.append("")
    if digest.get("empty"):
        lines.append("## No matching stories")
        lines.append(", ".join(digest["empty"]))
    return "\n".join(lines).rstrip() + "\n"


def to_json(digest):
    return json.dumps(digest, indent=2)
