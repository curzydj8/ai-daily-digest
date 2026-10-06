#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI日报每日采集脚本
板块1 开源AI工具排行榜：GitHub新AI项目 + 知名AI项目Star增长 + HF热门模型
板块2 GitHub热门项目榜：Python/Go/Java/Rust/C# 近7天新仓库按Star排序
板块3 编程学习知识库：每日轮换 Python/Go/SQL 各一个知识点
板块4 AI提示词库：每日轮换 ChatGPT/Gemini/Muse/图像 各一条
板块5 AI工具导航站：工具目录 + 本周新增
纯标准库 + GitHub API 认证。
"""
import sys
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response
import urllib.request, urllib.parse, urllib.error
import json, os, time
from datetime import datetime, timezone, timedelta, date

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
SNAP_FILE = os.path.join(DATA_DIR, "star_snapshot.json")
TZ_SH = timezone(timedelta(hours=8))
UA = "muse-ai-digest"
GH_API = "https://api.github.com"
CRED = "custom.github"

# Star增长观察名单（知名AI项目）
WATCHLIST = [
    "huggingface/transformers", "langchain-ai/langchain", "ollama/ollama",
    "openai/whisper", "AUTOMATIC1111/stable-diffusion-webui",
    "comfyanonymous/ComfyUI", "ggerganov/llama.cpp", "oobabooga/text-generation-webui",
    "microsoft/autogen", "FlowiseAI/Flowise", "assafelovic/gpt-researcher",
    "black-forest-labs/flux",
]
LANGS = ["Python", "Go", "Java", "Rust", "C#"]


def gh(path, params=None):
    url = GH_API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": UA,
    })
    add_surrogate_to_request(req, CRED, allowed_hosts=["api.github.com"])
    with urllib.request.urlopen(req, timeout=30) as r:
        return read_json_response(r)


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def repo_info(r):
    return {
        "full_name": r["full_name"],
        "name": r["name"],
        "desc": (r.get("description") or "")[:160],
        "stars": r["stargazers_count"],
        "lang": r.get("language"),
        "url": r["html_url"],
        "created": (r.get("created_at") or "")[:10],
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.now(TZ_SH).date()
    week_ago = (today - timedelta(days=7)).isoformat()
    day_idx = (today - date(2026, 10, 6)).days

    # ---- 板块1a: 新发布AI项目 ----
    print("fetch new AI projects ...", flush=True)
    new_projects = []
    try:
        d = gh("/search/repositories", {
            "q": f"topic:artificial-intelligence created:>{week_ago}",
            "sort": "stars", "order": "desc", "per_page": 10})
        new_projects = [repo_info(r) for r in d.get("items", [])]
    except Exception as e:
        print(f"  [fail] {e}", flush=True)
    time.sleep(2)

    # ---- 板块1b: Star增长 ----
    print("fetch star watchlist ...", flush=True)
    snap = {}
    if os.path.exists(SNAP_FILE):
        try:
            snap = json.load(open(SNAP_FILE, encoding="utf-8"))
        except Exception:
            pass
    growth = []
    new_snap = {}
    for full in WATCHLIST:
        try:
            r = gh(f"/repos/{full}")
            stars = r["stargazers_count"]
            new_snap[full] = stars
            prev = snap.get(full)
            growth.append({
                "full_name": full,
                "desc": (r.get("description") or "")[:120],
                "stars": stars,
                "delta": (stars - prev) if prev is not None else None,
                "url": r["html_url"],
            })
            time.sleep(1)
        except Exception as e:
            print(f"  [fail] {full}: {e}", flush=True)
    if new_snap:
        json.dump(new_snap, open(SNAP_FILE, "w", encoding="utf-8"))
    growth.sort(key=lambda x: (x["delta"] is not None, x["delta"] or 0), reverse=True)

    # ---- 板块1c: HF热门模型 ----
    print("fetch HF trending models ...", flush=True)
    models = []
    try:
        ms = get("https://huggingface.co/api/models?sort=likes&direction=-1&limit=10")
        for m in ms:
            models.append({
                "id": m["id"],
                "likes": m.get("likes", 0),
                "downloads": m.get("downloads", 0),
                "pipeline": (m.get("pipeline_tag") or "-"),
                "url": f"https://huggingface.co/{m['id']}",
            })
    except Exception as e:
        print(f"  [fail] {e}", flush=True)

    # ---- 板块2: 各语言热门 ----
    print("fetch language trending ...", flush=True)
    lang_trending = {}
    for lang in LANGS:
        try:
            d = gh("/search/repositories", {
                "q": f"language:{lang} created:>{week_ago}",
                "sort": "stars", "order": "desc", "per_page": 8})
            lang_trending[lang] = [repo_info(r) for r in d.get("items", [])]
            print(f"  {lang}: {len(lang_trending[lang])}", flush=True)
        except Exception as e:
            print(f"  [fail] {lang}: {e}", flush=True)
            lang_trending[lang] = []
        time.sleep(2)

    # ---- 板块3: 知识库轮换 ----
    print("pick knowledge ...", flush=True)
    knowledge = {}
    for k in ["python", "go", "sql"]:
        pool = json.load(open(os.path.join(BASE, "knowledge", f"{k}.json"), encoding="utf-8"))
        knowledge[k] = pool[day_idx % len(pool)]
        knowledge[k]["total"] = len(pool)
        knowledge[k]["day_n"] = day_idx % len(pool) + 1

    # ---- 板块4: 提示词轮换 ----
    print("pick prompts ...", flush=True)
    prompts = {}
    pool = json.load(open(os.path.join(BASE, "prompts", "prompts.json"), encoding="utf-8"))
    cats = {}
    for p in pool:
        cats.setdefault(p["category"], []).append(p)
    for cat, items in cats.items():
        it = items[day_idx % len(items)]
        prompts[cat] = {"title": it["title"], "prompt": it["prompt"],
                        "total": len(items), "day_n": day_idx % len(items) + 1}

    # ---- 板块5: 工具导航 ----
    print("build tools dir ...", flush=True)
    tools = json.load(open(os.path.join(BASE, "tools", "tools.json"), encoding="utf-8"))
    cats_out, new_week = {}, []
    for t in tools:
        cats_out.setdefault(t["category"], []).append(t)
        try:
            added = date.fromisoformat(t["added"])
            if (today - added).days <= 7:
                new_week.append(t)
        except Exception:
            pass

    day_data = {
        "date": today.isoformat(),
        "ai_rank": {"new_projects": new_projects, "star_growth": growth[:10], "trending_models": models},
        "lang_trending": lang_trending,
        "knowledge": knowledge,
        "prompts": prompts,
        "tools": {"categories": cats_out, "new_this_week": new_week},
    }
    json.dump(day_data, open(os.path.join(DATA_DIR, f"{today.isoformat()}.json"), "w", encoding="utf-8"),
                             ensure_ascii=False, indent=1)

    idx_file = os.path.join(DATA_DIR, "index.json")
    idx = []
    if os.path.exists(idx_file):
        try:
            idx = json.load(open(idx_file, encoding="utf-8"))
        except Exception:
            pass
    dates = {d["date"]: d for d in idx}
    dates[today.isoformat()] = {
        "date": today.isoformat(),
        "ai_projects": len(new_projects),
        "models": len(models),
    }
    idx = sorted(dates.values(), key=lambda d: d["date"], reverse=True)
    json.dump(idx, open(idx_file, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"done: {today.isoformat()}", flush=True)


if __name__ == "__main__":
    main()
