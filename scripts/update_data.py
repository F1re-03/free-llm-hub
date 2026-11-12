# -*- coding: utf-8 -*-
"""
每日自动更新脚本：抓取各平台公开数据，重新生成 data.js
由 GitHub Actions 定时调用（.github/workflows/daily-update.yml）
也可本地手动运行：python scripts/update_data.py
"""
import json
import datetime
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))  # 北京时间
SITE_URL = "https://free-llm-hub-9pd.pages.dev/"

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""


def fetch_json(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_openrouter_free_models() -> list[dict]:
    """OpenRouter 公开模型列表接口（无需 API Key）。
    筛选定价为 0 的免费模型（id 以 :free 结尾）。"""
    data = fetch_json("https://openrouter.ai/api/v1/models", headers={
        "User-Agent": "Mozilla/5.0 (free-llm-hub)",
    })["data"]
    free = []
    for m in data:
        pricing = m.get("pricing") or {}

        def _p(k):
            try:
                return float(pricing.get(k) or 1)
            except (TypeError, ValueError):
                return 1.0

        is_free = m.get("id", "").endswith(":free") or (_p("prompt") == 0 and _p("completion") == 0)
        if is_free:
            free.append({
                "id": m.get("id"),
                "name": m.get("name"),
                "context": m.get("context_length"),
                "provider": (m.get("id") or "").split("/")[0],
            })
    free.sort(key=lambda x: x["id"])
    return free


def now_bj() -> str:
    return datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")


def load_platforms_extra() -> dict:
    p = ROOT / "platforms_extra.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_affiliates() -> dict:
    p = ROOT / "affiliates.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main():
    base_path = ROOT / "data_base.json"
    base = json.loads(base_path.read_text(encoding="utf-8"))
    extra = load_platforms_extra()
    affiliates = load_affiliates()

    # 合并 API 端点 + 返佣链接到每个条目
    for item in base["items"]:
        name_en = item.get("nameEn") or item["name"]
        x = extra.get(name_en, {})
        item["apiBase"] = x.get("apiBase")
        item["openaiCompat"] = x.get("openaiCompat", False)
        item["refInfo"] = x.get("refInfo", "")
        # affiliates.json 里既可能写中文名也可能写英文名，两者都匹配
        aff = affiliates.get(item["name"]) or affiliates.get(name_en) or ""
        item["affiliateUrl"] = aff if aff and "REPLACE_ME" not in aff else ""
        # 有返佣标记的优先展示
        item["hasRef"] = bool(item["affiliateUrl"]) or bool(item.get("refInfo"))

    live = {}
    errors = []
    try:
        live["openrouterFreeModels"] = fetch_openrouter_free_models()
    except Exception as e:  # 单个数据源失败不影响整体
        errors.append(f"openrouter: {e}")
        # 保留上一次生成的快照（如果有）
        try:
            old = (ROOT / "data.js").read_text(encoding="utf-8")
            old_data = json.loads(old[old.index("=") + 1: old.rindex(";")])
            live["openrouterFreeModels"] = old_data.get("live", {}).get("openrouterFreeModels", [])
        except Exception:
            live["openrouterFreeModels"] = []

    out = {
        "updated": now_bj(),
        "items": base["items"],
        "live": {
            "fetchedAt": now_bj(),
            "openrouterFreeModels": live["openrouterFreeModels"],
        },
    }

    payload = "const DATA = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n"
    (ROOT / "data.js").write_text(payload, encoding="utf-8")

    # sitemap 的 lastmod 跟随每日更新，方便搜索引擎判断抓取时机
    (ROOT / "sitemap.xml").write_text(
        SITEMAP.format(url=SITE_URL, lastmod=out["updated"][:10]), encoding="utf-8"
    )

    n_free = len(live["openrouterFreeModels"])
    n_ref = sum(1 for i in out["items"] if i.get("affiliateUrl"))
    print(f"[OK] data.js 已更新 @ {out['updated']}")
    print(f"     平台条目: {len(out['items'])}  OpenRouter 免费模型: {n_free}  已配置返佣链接: {n_ref}")


if __name__ == "__main__":
    main()
