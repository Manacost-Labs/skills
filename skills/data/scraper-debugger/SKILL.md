---
name: scraper-debugger
description: Investigate why a crawl is underperforming — group failures by signature, quantify each cause, and prescribe the correct remedy for 403/429/5xx, empty 200s, challenges, timeouts and parse failures. Use when a run's coverage is below target, when asked "why did this domain only parse at 76%", when deciding whether blocking is real, or before spending money on a paid provider. Also trigger on Russian requests such as "почему парсится только часть", "меня банит", "разбери ошибки прогона", "стоит ли включать платный провайдер".
---

# Scraper debugger

Triage classifies one response. This skill answers the operational question:
**why is this run collecting only N%, and what is the correct response?**

The expensive mistake in scraping is answering an origin outage or a wall of
404s by turning on a paid provider. So never reason from a raw failure count —
group the failures first, then act per group.

## Run it

```bash
# From a run's state directory (reads its queue's attempt log):
ws-diagnose --state-dir state

# Or a specific queue, or a JSON list of attempts:
ws-diagnose --queue state/queue.sqlite3 --json
ws-diagnose --attempts-json attempts.json
```

## What you get

A breakdown ordered by size, each group carrying its root cause, the remedy, and
whether policy even permits paid escalation:

```
  57%  ORIGIN_DOWN @L1  (4)  [NO paid]
         cause:  the origin server is failing or unreachable (5xx / timeout / DNS)
         action: retry on the next sweep with backoff; the site is down, not blocking us
  29%  BLOCKED @L1      (2)  [paid OK]
         cause:  anti-bot mitigation served a block or challenge
         action: try alternative routes at the same level, then a browser (L2)
```

Reasons are normalized before grouping, so `HTTP 502` and `HTTP 503` form one
operational group instead of two.

## Remedy per verdict

| Verdict | Cause | Correct action | Paid? |
|---|---|---|---|
| `ORIGIN_DOWN` | site down / timeout / DNS | retry next sweep with backoff | **no** |
| `DEAD_URL` | 404/410 | quarantine, re-check rarely | **no** |
| `RATE_LIMITED` | 429 | honor `Retry-After`, lower concurrency | **no** |
| `BLOCKED` | block/challenge served | alt routes → warmed session → L2 | yes, in budget |
| `SOFT_BLOCK` | 2xx carrying a challenge | same as `BLOCKED` | yes, in budget |
| `THIN_CONTENT` | 2xx too small to be the page | check route returns full content | **no** |
| `PARSE_FAIL` | content arrived, fields did not | profile problem → `scraper-regression` | **no** |
| `ACCESS_DENIED` | refused on access-control grounds | verify the data is public at all | **no** |
| `AUTH_REQUIRED` | needs authentication | out of scope; get an authorized interface | **no** |
| `PROVIDER_ERROR` | our provider/proxy failed | check provider health, not the target | n/a |

`paid_escalation_share` in the JSON output tells you what fraction of failures
could legitimately reach a paid level. If it is small, buying credits will not
move coverage — fix the dominant group instead.

## Investigation order

1. **Run the breakdown.** Do not sample by hand; the grouping is what turns a
   vague "it's failing" into a decision.
2. **Take the largest group first.** Coverage is dominated by it; the tail rarely
   matters yet.
3. **Confirm a block is real** before treating it as one. A block signature must
   appear only on an actual block page — verify against a known-good page from
   the same site. (Two false positives have already been found this way: a bare
   `captcha` matching a theme's JS variable, and Cloudflare's JS-detection bundle
   which ships on ordinary pages.)
4. **If the group is `PARSE_FAIL`**, the site changed, not the defenses: switch to
   the `scraper-regression` skill.
5. **Check the per-domain counts.** Failures concentrated on one domain point at
   that site; failures spread across all domains point at us (network, pacing,
   a bad deploy).

## Rules

- Never recommend paid escalation for a group marked `NO paid`, regardless of its
  size. The flag is derived from the escalation contract, not from judgment.
- Never treat a rising failure count as a reason to raise retry counts: retries
  amplify a rate limit and do nothing for a redesign.
- Never attempt to work around authentication or access control.
