#!/usr/bin/env python3
"""
PlayerEmbedAPI - Testes de captura de video (unitarios, offline)
Valida funcoes de filtro/normalizacao e extracao de URLs do JWPlayer.
"""

from playerembedapi_capture_utils import (
    is_video_candidate,
    normalize_video_urls,
    extract_urls_from_jwplayer_config,
)

def test_is_video_candidate():
    print("\n" + "=" * 60)
    print("TESTE 1: is_video_candidate")
    print("=" * 60)

    valid = [
        "https://cdn.example.com/video/master.m3u8",
        "https://cdn.example.com/video/720p.mp4",
        "https://cdn.example.com/video/seg-0001.ts",
        "https://kBJLtxCD3.sssrr.org/sora/28930647/",
        "https://cdn.sssrr.org/sora/28930647/",
    ]
    invalid = [
        "https://cdn.example.com/app.js",
        "https://cdn.example.com/styles.css",
        "",
        None,
    ]

    passed = 0
    for url in valid:
        if is_video_candidate(url):
            print(f"  PASS: {url}")
            passed += 1
        else:
            print(f"  FAIL: {url}")

    for url in invalid:
        if not is_video_candidate(url):
            print(f"  PASS: {url}")
            passed += 1
        else:
            print(f"  FAIL: {url}")

    total = len(valid) + len(invalid)
    print(f"\nResultado: {passed}/{total} testes passaram")
    return passed == total

def test_normalize_video_urls():
    print("\n" + "=" * 60)
    print("TESTE 2: normalize_video_urls (dedupe + filtro)")
    print("=" * 60)

    urls = [
        "https://cdn.example.com/video/master.m3u8",
        "https://cdn.example.com/video/master.m3u8",
        "https://cdn.example.com/app.js",
        "https://cdn.example.com/video/seg-0001.ts",
        "",
        None,
        "https://cdn.example.com/video/720p.mp4",
    ]

    normalized = normalize_video_urls(urls)
    expected = [
        "https://cdn.example.com/video/master.m3u8",
        "https://cdn.example.com/video/seg-0001.ts",
        "https://cdn.example.com/video/720p.mp4",
    ]

    if normalized == expected:
        print("  PASS: lista normalizada corretamente")
        return True

    print(f"  FAIL: esperado {expected}, obtido {normalized}")
    return False

def test_extract_urls_from_jwplayer_config():
    print("\n" + "=" * 60)
    print("TESTE 3: extract_urls_from_jwplayer_config")
    print("=" * 60)

    config = {
        "file": "https://cdn.example.com/video/master.m3u8",
        "sources": [
            {"file": "https://cdn.example.com/video/720p.mp4", "label": "720p"},
            {"file": "https://cdn.example.com/video/1080p.mp4", "label": "1080p"},
        ],
        "playlist": [
            {"file": "https://cdn.example.com/video/playlist_1.m3u8"},
            {
                "sources": [
                    {"file": "https://cdn.example.com/video/playlist_2.m3u8"},
                    {"file": "https://cdn.example.com/app.js"},
                ]
            },
        ],
        "playlistItem": {
            "file": "https://cdn.example.com/video/item.m3u8",
            "sources": [{"file": "https://cdn.example.com/video/item_720p.mp4"}],
        },
    }

    urls = extract_urls_from_jwplayer_config(config)
    expected = [
        "https://cdn.example.com/video/master.m3u8",
        "https://cdn.example.com/video/720p.mp4",
        "https://cdn.example.com/video/1080p.mp4",
        "https://cdn.example.com/video/playlist_1.m3u8",
        "https://cdn.example.com/video/playlist_2.m3u8",
        "https://cdn.example.com/video/item.m3u8",
        "https://cdn.example.com/video/item_720p.mp4",
    ]

    if urls == expected:
        print("  PASS: URLs extraidas corretamente")
        return True

    print(f"  FAIL: esperado {expected}, obtido {urls}")
    return False

def main():
    print("\n" + "=" * 60)
    print("PlayerEmbedAPI - Suite de Testes de Captura (offline)")
    print("=" * 60)

    results = [
        ("is_video_candidate", test_is_video_candidate()),
        ("normalize_video_urls", test_normalize_video_urls()),
        ("extract_urls_from_jwplayer_config", test_extract_urls_from_jwplayer_config()),
    ]

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {name}")
    print(f"\nTotal: {passed}/{total} suites passaram")

if __name__ == "__main__":
    main()
