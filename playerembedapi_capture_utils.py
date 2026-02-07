#!/usr/bin/env python3
"""
Utils para captura de video do PlayerEmbedAPI (offline/testavel).
"""

VIDEO_URL_EXTENSIONS = (".m3u8", ".mp4", ".ts")
VIDEO_URL_HINTS = ("/sora/", "sssrr.org")

def is_video_candidate(url):
    if not url or not isinstance(url, str):
        return False
    lower = url.lower()
    if any(ext in lower for ext in VIDEO_URL_EXTENSIONS):
        return True
    if any(hint in lower for hint in VIDEO_URL_HINTS):
        return True
    return False

def normalize_video_urls(urls):
    seen = set()
    normalized = []
    for url in urls:
        if not is_video_candidate(url):
            continue
        if url in seen:
            continue
        seen.add(url)
        normalized.append(url)
    return normalized

def extract_urls_from_jwplayer_config(jwplayer_config):
    urls = []
    if not jwplayer_config or not isinstance(jwplayer_config, dict):
        return urls

    direct_file = jwplayer_config.get("file")
    if direct_file:
        urls.append(direct_file)

    sources = jwplayer_config.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict) and source.get("file"):
                urls.append(source["file"])

    playlist = jwplayer_config.get("playlist")
    if isinstance(playlist, list):
        for item in playlist:
            if not isinstance(item, dict):
                continue
            if item.get("file"):
                urls.append(item["file"])
            item_sources = item.get("sources")
            if isinstance(item_sources, list):
                for source in item_sources:
                    if isinstance(source, dict) and source.get("file"):
                        urls.append(source["file"])

    playlist_item = jwplayer_config.get("playlistItem")
    if isinstance(playlist_item, dict):
        if playlist_item.get("file"):
            urls.append(playlist_item["file"])
        item_sources = playlist_item.get("sources")
        if isinstance(item_sources, list):
            for source in item_sources:
                if isinstance(source, dict) and source.get("file"):
                    urls.append(source["file"])

    return normalize_video_urls(urls)
