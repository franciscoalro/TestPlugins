#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Any, Dict, List, Set
from urllib.parse import urlparse


REPO_REQUIRED_KEYS: Set[str] = {"name", "manifestVersion", "pluginLists"}
PLUGIN_REQUIRED_KEYS: Set[str] = {
    "url",
    "status",
    "version",
    "apiVersion",
    "name",
    "internalName",
    "authors",
    "description",
    "repositoryUrl",
    "tvTypes",
    "language",
    "iconUrl",
    "isAdult",
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def err(msg: str) -> None:
    print(f"ERROR: {msg}")


def warn(msg: str) -> None:
    print(f"WARN: {msg}")


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def validate_repo_json(repo: Dict[str, Any], strict: bool) -> int:
    errors = 0
    missing = REPO_REQUIRED_KEYS - set(repo.keys())
    if missing:
        err(f"repo.json missing keys: {sorted(missing)}")
        errors += 1

    extra = set(repo.keys()) - REPO_REQUIRED_KEYS - {"description", "iconUrl"}
    if extra:
        msg = f"repo.json has unknown keys: {sorted(extra)}"
        if strict:
            err(msg)
            errors += 1
        else:
            warn(msg)

    if repo.get("manifestVersion") != 1:
        err("repo.json manifestVersion must be 1")
        errors += 1

    plugin_lists = repo.get("pluginLists")
    if not isinstance(plugin_lists, list) or not plugin_lists:
        err("repo.json pluginLists must be a non-empty list")
        errors += 1
    else:
        for url in plugin_lists:
            if not isinstance(url, str) or not is_url(url):
                err(f"repo.json pluginLists contains invalid URL: {url}")
                errors += 1
            elif not url.endswith("plugins.json"):
                warn(f"repo.json pluginLists URL does not end with plugins.json: {url}")

    if errors == 0:
        ok("repo.json validated")
    return errors


def validate_plugin(plugin: Dict[str, Any], index: int, strict: bool, check_local: bool, root: str) -> int:
    errors = 0
    missing = PLUGIN_REQUIRED_KEYS - set(plugin.keys())
    if missing:
        err(f"plugins.json[{index}] missing keys: {sorted(missing)}")
        errors += 1

    extra = set(plugin.keys()) - PLUGIN_REQUIRED_KEYS
    if extra:
        msg = f"plugins.json[{index}] has unknown keys: {sorted(extra)}"
        if strict:
            err(msg)
            errors += 1
        else:
            warn(msg)

    if plugin.get("apiVersion") != 1:
        err(f"plugins.json[{index}] apiVersion must be 1")
        errors += 1

    url = plugin.get("url")
    if not isinstance(url, str) or not is_url(url):
        err(f"plugins.json[{index}] url is invalid: {url}")
        errors += 1
    elif not url.endswith(".cs3"):
        err(f"plugins.json[{index}] url must point to .cs3: {url}")
        errors += 1

    for key in ("repositoryUrl", "iconUrl"):
        value = plugin.get(key)
        if not isinstance(value, str) or not is_url(value):
            err(f"plugins.json[{index}] {key} is invalid: {value}")
            errors += 1

    if not isinstance(plugin.get("authors"), list) or not plugin.get("authors"):
        err(f"plugins.json[{index}] authors must be a non-empty list")
        errors += 1

    if not isinstance(plugin.get("tvTypes"), list) or not plugin.get("tvTypes"):
        err(f"plugins.json[{index}] tvTypes must be a non-empty list")
        errors += 1

    if check_local and isinstance(url, str):
        rel_path = urlparse(url).path
        filename = os.path.basename(rel_path)
        local_path = os.path.join(root, "builds", filename)
        if not os.path.exists(local_path):
            err(f"plugins.json[{index}] missing local file: {local_path}")
            errors += 1

    if errors == 0:
        ok(f"plugins.json[{index}] validated")
    return errors


def validate_plugins_json(plugins: Any, strict: bool, check_local: bool, root: str) -> int:
    errors = 0
    if not isinstance(plugins, list):
        err("plugins.json must be a list (array)")
        return 1

    if not plugins:
        err("plugins.json list is empty")
        return 1

    for i, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            err(f"plugins.json[{i}] must be an object")
            errors += 1
            continue
        errors += validate_plugin(plugin, i, strict, check_local, root)

    if errors == 0:
        ok("plugins.json validated")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Cloudstream repo.json and plugins.json")
    parser.add_argument("--repo", default="repo.json", help="Path to repo.json")
    parser.add_argument("--plugins", default="plugins.json", help="Path to plugins.json")
    parser.add_argument("--strict", action="store_true", help="Fail on unknown keys")
    parser.add_argument("--check-local", action="store_true", help="Check local builds/ files exist")
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(args.repo))

    repo = load_json(args.repo)
    plugins = load_json(args.plugins)

    errors = 0
    if not isinstance(repo, dict):
        err("repo.json must be an object")
        errors += 1
    else:
        errors += validate_repo_json(repo, args.strict)

    errors += validate_plugins_json(plugins, args.strict, args.check_local, root)

    if errors:
        err(f"Validation failed with {errors} error(s)")
        return 1
    ok("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
