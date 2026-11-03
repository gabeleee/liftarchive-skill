# LiftArchive CRO audit skill

A Claude skill that audits any web page for conversions, backed by real A/B test results.

It checks the page, matches what it sees against tests that ran on the same kind of page, and tells you what to fix first.

Every suggestion comes with the test that backs it: the result, what changed, and who ran it.

It works for online stores, SaaS, lead-gen and service sites, and apps.

The data comes from [LiftArchive](https://liftarchive.com), a free database of 1,800+ real A/B tests, each credited to the person or team that ran it.

## What it does

1. Works out the page type (homepage, product page, pricing page, signup form, landing page…) and the kind of site.
2. Checks the first phone screen: is the main button visible, is there proof near the headline, is there a long form, does a popup cover the page?
3. Gives you a short ranked list (FIX FIRST, THEN, ALREADY DOING), with the evidence for each item.
4. Builds the fixes you pick as **A/B test variants** behind your testing tool or a feature flag, never as silent rewrites.

It also works on local pages and code (localhost, components, templates) by reading the code.

## Install

**Claude Code (plugin, includes the MCP server):**

```
/plugin marketplace add gabeleee/liftarchive-skill
/plugin install liftarchive@liftarchive
```

**Claude Code (skill only):**

```
git clone https://github.com/gabeleee/liftarchive-skill
cp -R liftarchive-skill/skills/liftarchive ~/.claude/skills/
```

**Claude.ai / Claude desktop:** zip the `skills/liftarchive` folder and upload it under Settings → Capabilities → Skills.

## Use

```
/liftarchive audit https://example.com/pricing
```

Or just ask: "What should I A/B test on this page?"

## How it gets the data

The skill calls LiftArchive's public, read-only MCP server at `https://liftarchive.com/mcp/`.

If the MCP tools aren't connected, it uses `scripts/la.py`, a small Python client with no dependencies that calls the same server.

No API key or account is needed.

You can also connect the MCP server to ChatGPT, Claude or any MCP client on its own. See [liftarchive.com/ai/](https://liftarchive.com/ai/).

## Safety

The skill treats the audited page as untrusted data.

It won't follow instructions hidden in a page, run commands a page asks for, or read secrets, and it tells you if a page contains instructions aimed at AI tools.

The only network calls it makes are to the page being audited and to liftarchive.com.

## No coding agent?

Run the same audit in your browser, with a phone screenshot: [liftarchive.com/cro-audit/](https://liftarchive.com/cro-audit/).

## License

MIT
