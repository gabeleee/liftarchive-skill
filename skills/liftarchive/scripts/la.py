#!/usr/bin/env python3
"""Tiny client for LiftArchive's public MCP server (https://liftarchive.com/mcp/). Standard library only.

  python3 la.py suggest https://example.com/pricing [--page-type pricing-page] [--vertical saas] [--limit 8]
  python3 la.py search [--query "sticky cta"] [--page-type landing-page] [--element form-fields] [--vertical lead-gen] [--outcome won] [--limit 10]
  python3 la.py get <slug-or-url>
  python3 la.py facets
  python3 la.py expert [--vertical saas] [--page-type pricing-page]

Prints the tool's JSON result. Set LIFTARCHIVE_MCP to point at another server.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("LIFTARCHIVE_MCP", "https://liftarchive.com/mcp/")
if not ENDPOINT.startswith(("https://", "http://localhost:", "http://127.0.0.1:")):
    sys.exit("LIFTARCHIVE_MCP must be an https:// URL (or localhost for testing).")


def call(tool, args):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": {k: v for k, v in args.items() if v not in (None, "")}}}).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
               "MCP-Protocol-Version": "2025-06-18", "User-Agent": "liftarchive-skill/1.0"}
    req = urllib.request.Request(ENDPOINT, body, headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            msg = json.loads(r.read())
    except urllib.error.HTTPError as ex:
        sys.exit(f"LiftArchive returned HTTP {ex.code}: {ex.read()[:300].decode(errors='replace')}")
    except urllib.error.URLError as ex:
        if "CERTIFICATE_VERIFY_FAILED" not in str(ex.reason):
            sys.exit(f"Couldn't reach {ENDPOINT}: {ex.reason}")
        # Python installs without CA certificates (common on macOS): curl uses the system's.
        cmd = ["curl", "-sS", "--max-time", "40", "-X", "POST", ENDPOINT, "--data-binary", "@-"] + [x for k, v in headers.items() for x in ("-H", f"{k}: {v}")]
        p = subprocess.run(cmd, input=body, capture_output=True)
        if p.returncode:
            sys.exit(f"Couldn't reach {ENDPOINT}: {p.stderr.decode(errors='replace').strip()}")
        msg = json.loads(p.stdout)
    if "error" in msg:
        sys.exit(f"LiftArchive error: {msg['error'].get('message')}")
    res = msg["result"]
    out = res.get("structuredContent")
    if out is None:
        text = "".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        try:
            out = json.loads(text)
        except ValueError:
            out = text
    if res.get("isError"):
        print(json.dumps(out, indent=1, ensure_ascii=False))
        sys.exit(1)
    return out


def main():
    ap = argparse.ArgumentParser(description="Query LiftArchive's database of real A/B test results.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest", help="tests to run on a public page, from what it's missing")
    s.add_argument("url")
    s.add_argument("--page-type")
    s.add_argument("--vertical", choices=["ecommerce", "saas", "lead-gen"])
    s.add_argument("--limit", type=int, default=8)
    q = sub.add_parser("search", help="search tests by text, page type, element, vertical and outcome")
    q.add_argument("--query")
    q.add_argument("--page-type")
    q.add_argument("--element")
    q.add_argument("--vertical", choices=["ecommerce", "saas", "lead-gen"])
    q.add_argument("--outcome", choices=["won", "lost", "flat", "idea"])
    q.add_argument("--limit", type=int, default=10)
    g = sub.add_parser("get", help="the full record of one test")
    g.add_argument("slug")
    sub.add_parser("facets", help="page types, elements and verticals, with counts")
    e = sub.add_parser("expert", help="CRO experts who publish their results")
    e.add_argument("--vertical", choices=["ecommerce", "saas", "lead-gen"])
    e.add_argument("--page-type")
    a = ap.parse_args()
    if a.cmd == "suggest":
        out = call("suggest_tests_for_site", {"url": a.url, "page_type": a.page_type, "vertical": a.vertical, "limit": a.limit})
    elif a.cmd == "search":
        out = call("search_tests", {"query": a.query, "page_type": a.page_type, "element": a.element, "vertical": a.vertical,
                                    "outcome": a.outcome, "limit": a.limit})
    elif a.cmd == "get":
        out = call("get_test", {"url": a.slug} if a.slug.startswith("http") else {"slug": a.slug})
    elif a.cmd == "facets":
        out = call("list_facets", {})
    else:
        out = call("find_expert", {"vertical": a.vertical, "page_type": a.page_type})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
