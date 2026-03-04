import html
import re
import urllib.parse
import urllib.request


def web_search(query: str, max_results: int = 3, timeout: int = 6):
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "FOK/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html_text = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return []
    title_matches = list(re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html_text))
    snippet_matches = list(re.finditer(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html_text))
    results = []
    for i, m in enumerate(title_matches):
        link = html.unescape(m.group(1))
        title = re.sub(r"<.*?>", "", m.group(2))
        title = html.unescape(title).strip()
        snippet = ""
        if i < len(snippet_matches):
            snippet = re.sub(r"<.*?>", "", snippet_matches[i].group(1))
            snippet = html.unescape(snippet).strip()
        results.append({"title": title, "snippet": snippet, "url": link})
        if len(results) >= max_results:
            break
    return results


def wants_web(cfg: dict, text: str) -> bool:
    if not cfg.get("web_enabled", True):
        return False
    t = text.lower()
    words = cfg.get("web_trigger_words", ["web:", "search:", "google", "lookup:", "internetten", "ara:"])
    return any(k in t for k in words)


def normalize_web_query(cfg: dict, text: str) -> str:
    t = text.strip()
    for w in cfg.get("web_trigger_words", ["web:", "search:", "google", "lookup:", "internetten", "ara:"]):
        t = t.replace(w, " ")
    return " ".join(t.split())
