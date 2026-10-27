# Licensing options (Adam decides — this PR does not change LICENSE)

GitHub currently classifies the repo as license **Other**, even though
[LICENSE](../LICENSE) is MIT text. That usually happens when extra
paragraphs sit under the MIT grant (here: the MAGIX disclaimer and the
voluntary CC0 credit for MarcoRavich/VEGAS-AI-control). SPDX/`licensee`
then refuses to call it MIT.

**This PR does not edit `LICENSE`.** The notes below are options for a
later commit if you want a free, open release that still asks people to
credit SwampBewdy.

## What you said you want

A free, open release that **requires credit to SwampBewdy**
(Twitch / YouTube / Discord). Those two goals pull in opposite
directions: OSI-approved licenses make credit *easy* and *conventional*,
but almost none make a vanity credit *binding*.

## Options

### 1. Keep MIT, add a "please credit" line in the README (recommended for adoption)

- **Legal:** MIT already requires preserving the copyright notice
  (`Copyright (c) 2026 RFingAdam`) in copies. It does **not** require
  "Made by SwampBewdy", a Twitch link, or a shout-out on stream.
- **Social:** a README / NOTICE request ("If this saves you a cut, credit
  SwampBewdy") is how most creator tools actually get credited. It is not
  enforceable. People who would ignore it would also ignore a custom
  clause.
- **GitHub:** if you also *delete the extra paragraphs from LICENSE*
  (move MAGIX + CC0 notes into NOTICE only), `licensee` will show MIT.
  That is a later commit; not this PR.
- **Adoption:** best. npm/pypi/MCP registries, corporate forks, and
  "can I vendor this?" all stay easy.

### 2. Apache-2.0 + NOTICE attribution

- **Legal:** copyright notice + a NOTICE file must be preserved. You can
  put `vegas-director-mcp — created by SwampBewdy (Adam)` in NOTICE.
  Recipients must include NOTICE in distributions. They still do **not**
  have to put your name on a YouTube thumbnail.
- **Patent grant:** Apache-2.0 adds an express patent license. Nice if
  you ever care; irrelevant for a VEGAS/Resolve script host today.
- **Adoption:** still OSI, still GitHub-green. Slightly more paperwork
  than MIT. Fine for a "I want NOTICE to travel with the code" goal.

### 3. MIT or Apache-2.0 *plus* a binding attribution clause in LICENSE

- **Legal:** "You must display 'Made by SwampBewdy' in the UI / README of
  any derivative" is an extra restriction. OSI and GitHub will treat it
  as a **custom / Other** license again — the situation you already have.
- **Enforcement:** you would need to police forks. Most will not notice.
  A few companies will refuse to touch it.
- **Adoption:** worse than #1/#2. MCP directories and "awesome-*" lists
  often filter on SPDX.

### 4. CC-BY-4.0 (do not use for this repo)

- Creative Commons **BY** is built for *content* (video, writing, images),
  not source code. No patent language, awkward with copyleft, and the
  official CC FAQ tells you not to use CC licenses on software.
- "Credit SwampBewdy" *is* what BY is for — on a thumbnail pack, not on
  a Python package.

### 5. Stay on the current file (MIT + extra paragraphs = GitHub Other)

- Functionally MIT for anyone who reads the text.
- Badge/filter pain continues.
- Changing nothing is valid if you do not care about the SPDX badge.

## Trade-offs vs adoption

| Choice | SPDX / GitHub | Binding SwampBewdy credit | Fork/registry friction |
|---|---|---|---|
| MIT + README ask (#1) | MIT once extras leave LICENSE | No (ask only) | Lowest |
| Apache-2.0 + NOTICE (#2) | Apache-2.0 | NOTICE must ship; still no UI credit | Low |
| Custom "must credit" clause (#3) | Other | On paper, yes | Highest |
| CC-BY (#4) | Other / wrong tool | Yes, for *content* | High, and a poor fit |
| Status quo (#5) | Other | No | Medium (badge only) |

## Practical suggestion

Ship **#1**: keep MIT, put MAGIX / Blackmagic / CC0 notes in NOTICE,
and put a tasteful "Made by SwampBewdy" block in the README (this PR
already adds the credit block; it does not touch LICENSE). If a later
you wants NOTICE to be mandatory on redistribution, switch the SPDX to
Apache-2.0 in a dedicated license PR.

Credit links you asked for:

- Twitch: https://twitch.tv/swampbewdy
- YouTube: SwampBewdy
- Discord: https://discord.gg/WWvJXUS6mb
