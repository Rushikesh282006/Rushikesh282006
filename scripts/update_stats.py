#!/usr/bin/env python3
"""
Fetch live GitHub + LeetCode stats and render two animated SVG dashboards.

  assets/github-live.svg     contribution heatmap, streaks, repos, languages
  assets/leetcode-live.svg   solved donut, per-difficulty progress, rank, recent solves
  assets/stats.json          last good data (used as a fallback if an API call fails)

Standard library only. Run by .github/workflows/update-stats.yml, or locally:

  python scripts/update_stats.py              # live data (needs GH_TOKEN for GitHub)
  python scripts/update_stats.py --placeholder
  python scripts/update_stats.py --demo --out /tmp/preview   # fake data, for design previews
"""
import argparse, datetime as dt, html, json, math, os, random, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GH_USER = os.environ.get("GH_USER", "Rushikesh282006")
LC_USER = os.environ.get("LEETCODE_USER", "Rushi_28")

SANS = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'Fira Code','SF Mono',Consolas,'DejaVu Sans Mono',monospace"
UTC = dt.timezone.utc


# ───────────────────────────── fetching ─────────────────────────────
def post_json(url, payload, headers, retries=3):
    body = json.dumps(payload).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def gh_query(query, variables):
    res = post_json(
        "https://api.github.com/graphql",
        {"query": query, "variables": variables},
        {"Authorization": f"bearer {os.environ.get('GH_TOKEN', '')}",
         "Content-Type": "application/json", "User-Agent": "profile-live-stats"},
    )
    if res.get("errors"):
        raise RuntimeError(res["errors"][0].get("message", "GraphQL error"))
    return res["data"]


Q_PROFILE = """query($login:String!){ user(login:$login){ createdAt followers{totalCount}
  repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){ totalCount
    nodes{ stargazerCount languages(first:6,orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } } } } } }"""
Q_YEAR = """query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
  contributionsCollection(from:$from,to:$to){ contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }"""


def fetch_github(now):
    u = gh_query(Q_PROFILE, {"login": GH_USER})["user"]
    created = dt.datetime.strptime(u["createdAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    langs = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            n = e["node"]
            cur = langs.setdefault(n["name"], {"color": n["color"] or "#8b949e", "size": 0})
            cur["size"] += e["size"]
    top = sorted(langs.items(), key=lambda kv: -kv[1]["size"])[:6]

    days = {}
    for year in range(created.year, now.year + 1):
        frm = dt.datetime(year, 1, 1, tzinfo=UTC)
        to = min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=UTC), now)
        data = gh_query(Q_YEAR, {"login": GH_USER, "from": frm.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "to": to.strftime("%Y-%m-%dT%H:%M:%SZ")})
        for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                if d["contributionCount"] > 0:
                    days[d["date"]] = max(days.get(d["date"], 0), d["contributionCount"])
    return {
        "created": created.date().isoformat(),
        "followers": u["followers"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "stars": stars,
        "langs": [[k, v["color"], v["size"]] for k, v in top],
        "days": days,
        "synced": now.strftime("%Y-%m-%d %H:%M UTC"),
    }


LC_URL = "https://leetcode.com/graphql"
LC_H = {"Content-Type": "application/json", "Referer": "https://leetcode.com/", "Origin": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def lc_query(q, v):
    res = post_json(LC_URL, {"query": q, "variables": v}, LC_H)
    if not res.get("data"):
        raise RuntimeError(str(res.get("errors", "empty response"))[:200])
    return res["data"]


def fetch_leetcode(now, prev):
    lc = dict(prev or {})
    ok = 0
    try:
        d = lc_query("""query($u:String!){ allQuestionsCount{difficulty count}
          matchedUser(username:$u){ profile{ranking} submitStatsGlobal{acSubmissionNum{difficulty count}} } }""", {"u": LC_USER})
        lc["totals"] = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
        lc["solved"] = {x["difficulty"]: x["count"] for x in d["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
        lc["rank"] = d["matchedUser"]["profile"]["ranking"]
        ok += 1
    except Exception as e:  # noqa: BLE001
        print(f"! LeetCode stats failed: {e}", file=sys.stderr)
    try:
        d = lc_query("""query($u:String!){ recentAcSubmissionList(username:$u,limit:20){ title titleSlug timestamp } }""", {"u": LC_USER})
        seen, recent = set(), []
        for s in d["recentAcSubmissionList"]:
            if s["titleSlug"] in seen:
                continue
            seen.add(s["titleSlug"])
            recent.append({"title": s["title"], "slug": s["titleSlug"], "ts": int(s["timestamp"])})
        lc["recent"] = recent[:5]
        ok += 1
    except Exception as e:  # noqa: BLE001
        print(f"! LeetCode recent failed: {e}", file=sys.stderr)
    try:
        d = lc_query("""query($u:String!){ matchedUser(username:$u){ userCalendar{ streak totalActiveDays } } }""", {"u": LC_USER})
        cal = d["matchedUser"]["userCalendar"]
        lc["streak"], lc["active_days"] = cal["streak"], cal["totalActiveDays"]
        ok += 1
    except Exception as e:  # noqa: BLE001
        print(f"! LeetCode calendar failed: {e}", file=sys.stderr)
    if ok:
        lc["synced"] = now.strftime("%Y-%m-%d %H:%M UTC")
    return lc if lc.get("solved") else None


# ───────────────────────────── helpers ─────────────────────────────
def esc(s): return html.escape(str(s), quote=True)
def V(x): return "—" if x is None else f"{x:,}"
def short(d): return f"{d:%b} {d.day}"
def trunc(s, n): return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def streaks(days, today):
    one = dt.timedelta(days=1)
    d = today
    if days.get(d.isoformat(), 0) == 0:
        d -= one  # today not over yet, so don't break the streak
    end, cur = d, 0
    while days.get(d.isoformat(), 0) > 0:
        cur += 1
        d -= one
    cur_range = (end - dt.timedelta(days=cur - 1), end) if cur else None
    best, best_range, run, run_start, prev = 0, None, 0, None, None
    for x in sorted(dt.date.fromisoformat(k) for k, v in days.items() if v > 0):
        if prev and (x - prev).days == 1:
            run += 1
        else:
            run, run_start = 1, x
        if run > best:
            best, best_range = run, (run_start, x)
        prev = x
    return cur, cur_range, best, best_range


def rng(r): return "—" if not r else (short(r[0]) if r[0] == r[1] else f"{short(r[0])} – {short(r[1])}")


COMMON_DEFS = """
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0f1f"/><stop offset="1" stop-color="#141a3a"/></linearGradient>
  <linearGradient id="tg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <style>
    @keyframes pop{from{opacity:0}to{opacity:1}}
    @keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
    @keyframes beat{0%,100%{opacity:.35}50%{opacity:1}}
    .c{animation:pop .5s ease-out both}
    .t{animation:rise .7s ease-out both}
    .today{animation:beat 1.6s ease-in-out infinite}
  </style>"""


def live_pill(x, y):
    return (f'<rect x="{x}" y="{y}" width="64" height="22" rx="11" fill="#4ade80" fill-opacity=".12" stroke="#4ade80" stroke-opacity=".55"/>'
            f'<circle cx="{x+16}" cy="{y+11}" r="4" fill="#4ade80"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="3.5;5;3.5" dur="1.6s" repeatCount="indefinite"/></circle>'
            f'<text x="{x+28}" y="{y+15}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#4ade80" letter-spacing="1.5">LIVE</text>')


def frame(w, h): return (f'<rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>'
                         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="18" fill="none" stroke="#38bdf8" stroke-opacity=".25"/>')


# ───────────────────────────── GitHub SVG ─────────────────────────────
LEVELS = ["#151c36", "#155e75", "#0ea5e9", "#818cf8", "#c084fc"]


def render_github(gh, now):
    W, H = 1000, 436
    today = now.date()
    days = (gh or {}).get("days", {})
    synced = gh["synced"] if gh else "awaiting first sync"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Live GitHub activity for {esc(GH_USER)}: contribution heatmap, streaks, repositories and top languages">',
         f'<defs>{COMMON_DEFS}<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         f'<clipPath id="hm"><rect x="76" y="86" width="845" height="109"/></clipPath>'
         f'<clipPath id="lb"><rect x="50" y="376" width="900" height="14" rx="7"/></clipPath></defs>', frame(W, H),
         live_pill(40, 19),
         f'<text x="116" y="36" font-family="{SANS}" font-size="17" font-weight="700" fill="#f1f5f9">GitHub activity · @{esc(GH_USER)}</text>',
         f'<text x="960" y="35" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#64748b">synced {esc(synced)}</text>']

    # heatmap grid
    wd = (today.weekday() + 1) % 7  # Sunday = 0
    start = today - dt.timedelta(days=wd) - dt.timedelta(weeks=52)
    vals = [days.get((start + dt.timedelta(days=7 * c + r)).isoformat(), 0)
            for c in range(53) for r in range(7) if start + dt.timedelta(days=7 * c + r) <= today]
    mx = max(vals + [1])
    last_month = None
    for c in range(53):
        d0 = start + dt.timedelta(days=7 * c)
        if d0.month != last_month and d0.day <= 7 and c < 51:
            o.append(f'<text x="{76 + c*16}" y="77" font-family="{MONO}" font-size="10" fill="#64748b">{d0:%b}</text>')
        last_month = d0.month
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        o.append(f'<text x="66" y="{86 + r*16 + 10}" text-anchor="end" font-family="{MONO}" font-size="9.5" fill="#64748b">{name}</text>')
    for c in range(53):
        for r in range(7):
            d = start + dt.timedelta(days=7 * c + r)
            if d > today:
                continue
            n = days.get(d.isoformat(), 0)
            lvl = 0 if n == 0 else 1 if n / mx <= .25 else 2 if n / mx <= .5 else 3 if n / mx <= .75 else 4
            cls = "c today" if d == today else "c"
            stroke = ' stroke="#f8fafc" stroke-width="1.4"' if d == today else ""
            o.append(f'<rect class="{cls}" x="{76 + c*16}" y="{86 + r*16}" width="13" height="13" rx="3" fill="{LEVELS[lvl]}"{stroke} '
                     f'style="animation-delay:{c*0.022:.2f}s"/>')
    o.append('<g clip-path="url(#hm)"><rect y="86" width="140" height="109" fill="url(#sweep)">'
             '<animateTransform attributeName="transform" type="translate" from="-140 0" to="1000 0" dur="6s" repeatCount="indefinite"/></rect></g>')
    # legend
    lx = 770
    o.append(f'<text x="{lx}" y="216" text-anchor="end" font-family="{MONO}" font-size="10" fill="#64748b">Less</text>')
    for i, col in enumerate(LEVELS):
        o.append(f'<rect x="{lx+8+i*16}" y="206" width="13" height="13" rx="3" fill="{col}"/>')
    o.append(f'<text x="{lx+8+5*16+4}" y="216" font-family="{MONO}" font-size="10" fill="#64748b">More</text>')

    # tiles
    if gh:
        total_all = sum(days.values())
        year_total = sum(v for k, v in days.items() if dt.date.fromisoformat(k) > today - dt.timedelta(days=365))
        cur, cur_r, best, best_r = streaks(days, today)
        created = dt.date.fromisoformat(gh["created"])
        tiles = [("CONTRIBUTIONS", V(total_all), f"since {created:%b %Y}"),
                 ("LAST 12 MONTHS", V(year_total), f"≈ {year_total/52:.1f} per week"),
                 ("CURRENT STREAK", f"{cur}d", rng(cur_r) if cur else "start one today"),
                 ("LONGEST STREAK", f"{best}d", rng(best_r)),
                 ("PUBLIC REPOS", V(gh["repos"]), f"{gh['stars']} stars earned"),
                 ("FOLLOWERS", V(gh["followers"]), "on GitHub")]
    else:
        tiles = [(a, "—", b) for a, b in (("CONTRIBUTIONS", "waiting"), ("LAST 12 MONTHS", "waiting"), ("CURRENT STREAK", "waiting"),
                                          ("LONGEST STREAK", "waiting"), ("PUBLIC REPOS", "waiting"), ("FOLLOWERS", "waiting"))]
    for i, (lab, big, sub) in enumerate(tiles):
        x = 50 + i * 152
        o.append(f'<g class="t" style="animation-delay:{0.3+i*0.1:.1f}s">'
                 f'<rect x="{x}" y="240" width="140" height="88" rx="12" fill="#0f1630" stroke="#38bdf8" stroke-opacity=".2"/>'
                 f'<text x="{x+14}" y="264" font-family="{MONO}" font-size="9.5" fill="#94a3b8" letter-spacing="1.2">{lab}</text>'
                 f'<text x="{x+14}" y="298" font-family="{SANS}" font-size="29" font-weight="800" fill="url(#tg)">{esc(big)}</text>'
                 f'<text x="{x+14}" y="317" font-family="{MONO}" font-size="10" fill="#64748b">{esc(sub)}</text></g>')

    # languages
    o.append(f'<text x="50" y="362" font-family="{MONO}" font-size="10" fill="#94a3b8" letter-spacing="1.5">TOP LANGUAGES · BY CODE SIZE</text>')
    langs = (gh or {}).get("langs") or []
    if langs:
        tot = sum(l[2] for l in langs) or 1
        x = 50.0
        o.append('<g clip-path="url(#lb)">')
        for name, col, size in langs:
            w = 900 * size / tot
            o.append(f'<rect x="{x:.1f}" y="376" width="{w:.1f}" height="14" fill="{esc(col)}"/>')
            x += w
        o.append('<rect x="50" y="376" width="900" height="14" fill="none"/></g>')
        o.append('<clipPath id="lb2"><rect x="50" y="376" width="900" height="14" rx="7"/></clipPath>')
        # reveal animation: cover with a bg-colored sliding mask
        o.append('<rect x="50" y="374" width="900" height="18" fill="#0a0f1f"><animate attributeName="x" from="50" to="950" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'
                 '<animate attributeName="width" from="900" to="0" dur="1.4s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>')
        for i, (name, col, size) in enumerate(langs):
            lx0 = 50 + i * 150
            o.append(f'<circle cx="{lx0+5}" cy="410" r="5" fill="{esc(col)}"/>'
                     f'<text x="{lx0+16}" y="414" font-family="{MONO}" font-size="11" fill="#cbd5e1">{esc(trunc(name, 15))} {100*size/tot:.0f}%</text>')
    else:
        o.append('<rect x="50" y="376" width="900" height="14" rx="7" fill="#1e293b"/>')
    o.append('</svg>')
    return "\n".join(o)


# ───────────────────────────── LeetCode SVG ─────────────────────────────
DIFF = [("Easy", "#22c55e"), ("Medium", "#f59e0b"), ("Hard", "#ef4444")]


def render_leetcode(lc, now):
    W, H = 1000, 340
    synced = lc["synced"] if lc else "awaiting first sync"
    solved = (lc or {}).get("solved", {})
    totals = (lc or {}).get("totals", {})
    total_solved = solved.get("All")
    R = 62
    C = 2 * math.pi * R
    cx, cy = 150, 168
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Live LeetCode stats for {esc(LC_USER)}: problems solved by difficulty, rank, and recent accepted submissions">',
         f'<defs>{COMMON_DEFS}</defs>', frame(W, H), live_pill(40, 19),
         f'<text x="116" y="36" font-family="{SANS}" font-size="17" font-weight="700" fill="#f1f5f9">LeetCode · {esc(LC_USER)}</text>',
         f'<text x="960" y="35" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#64748b">synced {esc(synced)}</text>']
    # donut
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#1e293b" stroke-width="14"/>')
    if total_solved:
        off = 0.0
        for i, (name, col) in enumerate(DIFF):
            v = solved.get(name, 0)
            ln = C * v / total_solved
            if v:
                o.append(f'<circle class="c" cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{col}" stroke-width="14" '
                         f'stroke-dasharray="{max(ln-2.5, .8):.2f} {C:.2f}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 {cx} {cy})" '
                         f'style="animation-delay:{0.2+i*0.35:.2f}s"/>')
            off += ln
    o.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="#f8fafc">{V(total_solved)}</text>'
             f'<text x="{cx}" y="{cy+26}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="#94a3b8">solved</text>'
             f'<text x="{cx}" y="268" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="#64748b">'
             f'of {V(totals.get("All"))} questions</text>')
    # bars
    for i, (name, col) in enumerate(DIFF):
        y = 92 + i * 52
        s, t = solved.get(name), totals.get(name)
        frac = (s / t) if (s is not None and t) else 0
        w = max(300 * frac, 4 if s else 0)
        o.append(f'<g class="t" style="animation-delay:{0.3+i*0.12:.2f}s">'
                 f'<text x="300" y="{y+12}" font-family="{SANS}" font-size="13" font-weight="700" fill="{col}">{name}</text>'
                 f'<text x="600" y="{y+12}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#cbd5e1">{V(s)} <tspan fill="#64748b">/ {V(t)}</tspan></text>'
                 f'<rect x="300" y="{y+20}" width="300" height="10" rx="5" fill="#1e293b"/>'
                 f'<rect x="300" y="{y+20}" width="{w:.1f}" height="10" rx="5" fill="{col}">'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" dur="1.3s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect></g>')
    # mini tiles
    def mini(x, lab, big, sub):
        return (f'<g class="t" style="animation-delay:.8s"><rect x="{x}" y="250" width="146" height="58" rx="12" fill="#0f1630" stroke="#38bdf8" stroke-opacity=".2"/>'
                f'<text x="{x+12}" y="270" font-family="{MONO}" font-size="9.5" fill="#94a3b8" letter-spacing="1.2">{lab}</text>'
                f'<text x="{x+12}" y="293" font-family="{SANS}" font-size="20" font-weight="800" fill="url(#tg)">{esc(big)}</text>'
                f'<text x="{x+134}" y="293" text-anchor="end" font-family="{MONO}" font-size="10" fill="#64748b">{esc(sub)}</text></g>')
    rank = (lc or {}).get("rank")
    o.append(mini(300, "GLOBAL RANK", f"#{rank:,}" if rank else "—", ""))
    ad, st = (lc or {}).get("active_days"), (lc or {}).get("streak")
    o.append(mini(454, "ACTIVE DAYS", V(ad), f"streak {st}d" if st is not None else ""))
    # recent list
    o.append(f'<text x="640" y="98" font-family="{MONO}" font-size="10" fill="#38bdf8" letter-spacing="1.5">RECENTLY SOLVED</text>')
    recent = (lc or {}).get("recent") or []
    for i in range(5):
        y = 110 + i * 38
        if i < len(recent):
            it = recent[i]
            d = dt.datetime.fromtimestamp(it["ts"], UTC).date()
            o.append(f'<g class="t" style="animation-delay:{0.4+i*0.12:.2f}s"><rect x="640" y="{y}" width="320" height="32" rx="9" fill="#0f1630" stroke="#38bdf8" stroke-opacity=".14"/>'
                     f'<circle cx="661" cy="{y+16}" r="8" fill="#22c55e" fill-opacity=".16"/>'
                     f'<path d="M657 {y+16} l3 3 l6 -6" fill="none" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<text x="678" y="{y+20}" font-family="{SANS}" font-size="12.5" fill="#e2e8f0">{esc(trunc(it["title"], 27))}</text>'
                     f'<text x="948" y="{y+20}" text-anchor="end" font-family="{MONO}" font-size="10" fill="#64748b">{short(d)}</text></g>')
        else:
            o.append(f'<rect x="640" y="{y}" width="320" height="32" rx="9" fill="#0f1630" fill-opacity=".5" stroke="#38bdf8" stroke-opacity=".08"/>')
    o.append('</svg>')
    return "\n".join(o)


# ───────────────────────────── demo / main ─────────────────────────────
def demo_data(now):
    random.seed(3)
    days = {}
    for i in range(0, 420):
        d = now.date() - dt.timedelta(days=i)
        if i < 2 or random.random() < .45:
            days[d.isoformat()] = random.choice([1, 1, 2, 3, 4, 6, 9, 14])
    gh = {"created": (now.date() - dt.timedelta(days=420)).isoformat(), "followers": 12, "repos": 14, "stars": 7,
          "langs": [["Python", "#3572A5", 620], ["JavaScript", "#f1e05a", 140], ["Jupyter Notebook", "#DA5B0B", 110],
                    ["HTML", "#e34c26", 70], ["CSS", "#563d7c", 40], ["Java", "#b07219", 20]],
          "days": days, "synced": now.strftime("%Y-%m-%d %H:%M UTC")}
    t = int(now.timestamp())
    lc = {"solved": {"All": 167, "Easy": 96, "Medium": 69, "Hard": 2}, "totals": {"All": 4105, "Easy": 975, "Medium": 2142, "Hard": 988},
          "rank": 1067227, "streak": 3, "active_days": 41, "synced": now.strftime("%Y-%m-%d %H:%M UTC"),
          "recent": [{"title": x, "slug": x, "ts": t - 86400 * k} for k, x in enumerate(
              ["Keys and Rooms", "Minimum Operations to Sort a Binary Tree", "Successful Pairs of Spells and Potions",
               "Average Selling Price", "Two Sum"])]}
    return gh, lc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="render fake data (design preview)")
    ap.add_argument("--placeholder", action="store_true", help="render empty skeletons")
    ap.add_argument("--out", default=str(ASSETS))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(UTC)
    cache_path = ASSETS / "stats.json"

    if a.demo:
        gh, lc = demo_data(now)
    elif a.placeholder:
        gh, lc = None, None
    else:
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        gh = lc = None
        try:
            gh = fetch_github(now)
        except Exception as e:  # noqa: BLE001
            print(f"! GitHub fetch failed, using cache: {e}", file=sys.stderr)
            gh = cache.get("github")
        lc = fetch_leetcode(now, cache.get("leetcode")) or cache.get("leetcode")
        if not gh and not lc:
            print("Nothing fetched and no cache. Check GH_TOKEN and network.", file=sys.stderr)
            sys.exit(1)
        cache_path.write_text(json.dumps({"github": gh, "leetcode": lc}, indent=1))

    (out / "github-live.svg").write_text(render_github(gh, now), encoding="utf-8")
    (out / "leetcode-live.svg").write_text(render_leetcode(lc, now), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
