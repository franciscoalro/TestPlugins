#!/usr/bin/env python3
"""
Runner unico para testes PlayerEmbedAPI (offline).
"""

import sys

from test_playerembedapi_capture import (
    test_is_video_candidate,
    test_normalize_video_urls,
    test_extract_urls_from_jwplayer_config,
)

def main():
    print("\n" + "=" * 60)
    print("PlayerEmbedAPI - Runner de Testes (offline)")
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

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
