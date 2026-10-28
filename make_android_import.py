#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Prepare Wubi86/98/06 and Rime Ice from two local upstream downloads. Fully offline."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import zipfile


UPSTREAM_REPO = "https://github.com/myshiqiqi/rime-wubi/tree/master"
ICE_REPO = "https://github.com/iDvel/rime-ice"
VERSIONS = ("86", "98", "06")
MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_HEADER_BYTES = 65536
DOC_NAMES = ("README.txt", "MANUAL-INSTALL.txt", "NOTICE.txt", "LICENSE.txt")
OWN_NAMES = (
    "default.custom.yaml", "pinyin_aux.schema.yaml",
    "wb_spelling86.schema.yaml", "wb_spelling98.schema.yaml", "wb_spelling06.schema.yaml",
    "wubi86.schema.yaml", "wubi98.schema.yaml", "wubi06.schema.yaml",
    "wubi86.custom.yaml", "wubi98.custom.yaml", "wubi06.custom.yaml",
    "wubi.custom.yaml",
    "rime_ice.custom.yaml", "melt_eng.custom.yaml", "radical_pinyin.custom.yaml",
)
OWN_ASSETS = ("lua/wubi_calculator_guard.lua", "lua/wubi_switcher_guard.lua")
SHARED_NAMES = (
    "wubi.schema.yaml", "default.yaml", "key_bindings.yaml", "punctuation.yaml",
    "symbols.yaml", "rime.lua", "pinyin.dict.yaml", "pinyin.schema.yaml", "quick_symbols.dict.yaml",
    "opencc/es.json", "opencc/es.txt",
    "lua/Submit_text.lua", "lua/calculator.lua", "lua/date_extend_ts.lua",
    "lua/date_ts.lua", "lua/helper.lua", "lua/lib/basic.lua", "lua/lunarDate.lua",
    "lua/lunarGz.lua", "lua/lunarJq.lua", "lua/new_spelling.lua", "lua/number.lua",
    "lua/switcher.lua",
)
ICE_NAMES = (
    "rime_ice.schema.yaml", "rime_ice.dict.yaml", "melt_eng.schema.yaml",
    "melt_eng.dict.yaml", "radical_pinyin.schema.yaml", "radical_pinyin.dict.yaml",
    "custom_phrase.txt", "symbols_v.yaml",
    "cn_dicts/8105.dict.yaml", "cn_dicts/base.dict.yaml", "cn_dicts/ext.dict.yaml",
    "cn_dicts/tencent.dict.yaml", "cn_dicts/others.dict.yaml",
    "en_dicts/en.dict.yaml", "en_dicts/en_ext.dict.yaml", "en_dicts/cn_en.txt",
    "opencc/emoji.json", "opencc/emoji.txt", "opencc/others.txt",
    "lua/select_character.lua", "lua/date_translator.lua", "lua/lunar.lua",
    "lua/uuid.lua", "lua/unicode.lua", "lua/number_translator.lua",
    "lua/calc_translator.lua", "lua/force_gc.lua", "lua/corrector.lua",
    "lua/autocap_filter.lua", "lua/v_filter.lua", "lua/pin_cand_filter.lua",
    "lua/long_word_filter.lua", "lua/reduce_english_filter.lua", "lua/search.lua",
    "lua/convert_ar_num_to_zh.lua", "lua/lunar.db",
)
ICE_RENAMED = (
    ("default.yaml", "ice_defaults.yaml"),
    ("LICENSE", "source-info/rime-ice/LICENSE"),
    ("others/docs/Credits.md", "source-info/rime-ice/Credits.md"),
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_file(root, relative, *, binary=False):
    path = root / relative
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        raise ValueError("Source file escapes its selected folder: " + relative)
    if not path.is_file():
        raise ValueError("Required file missing: " + str(path) +
                         ". Check that the source and overlay ZIPs were fully extracted.")
    with path.open("rb") as source:
        data = source.read(MAX_FILE_BYTES + 1)
    if not data or len(data) > MAX_FILE_BYTES:
        raise ValueError("Empty or oversized source file: " + relative)
    # Only Ice's explicitly selected lunar.db is binary; keep it byte-for-byte.
    if not binary:
        data.decode("utf-8-sig")
    return data


def dictionary_header(data, expected_name):
    end = re.search(rb"(?m)^\.\.\.[ \t]*\r?$", data[:MAX_HEADER_BYTES])
    if end is None:
        raise ValueError("Incomplete Rime dictionary header: " + expected_name)
    header = data[:end.start()]
    names = list(re.finditer(rb"(?m)^(name:[ \t]*)([^#\r\n]*?)([ \t]*(?:#[^\r\n]*)?\r?)$", header))
    if len(names) != 1:
        raise ValueError("Expected one dictionary name in header: " + expected_name)
    raw_name = names[0].group(2)
    if raw_name not in (expected_name.encode(), ("'" + expected_name + "'").encode(),
                        ('"' + expected_name + '"').encode()):
        raise ValueError("Unexpected dictionary name; expected " + expected_name)
    return header, end.start(), names[0]


def rename_dictionary(data, expected_name, new_name):
    header, boundary, name = dictionary_header(data, expected_name)
    if re.search(rb"(?m)^[ \t]*import_tables[ \t]*:", header):
        raise ValueError("Unexpected imported tables in " + expected_name)
    literal = name.group(2)
    quote = literal[:1] if literal[:1] in (b"'", b'"') else b""
    return (header[:name.start(2)] + quote + new_name.encode() + quote +
            header[name.end(2):] + data[boundary:])


def rename_extended(data, version):
    header, boundary, name = dictionary_header(data, "wubi.extended")
    blocks = list(re.finditer(
        rb"(?m)^import_tables:[ \t]*(?:#[^\r\n]*)?\r?\n((?:[ \t]+-[^\r\n]*\r?\n)+)", header
    ))
    if len(blocks) != 1:
        raise ValueError("Expected the upstream extended dictionary's import_tables block.")
    block = blocks[0]
    entries = list(re.finditer(
        rb"(?m)^([ \t]+-[ \t]+)([^#\r\n]*?)([ \t]*(?:#[^\r\n]*)?\r?)$", block.group(1)
    ))
    if len(entries) != 2 or any(
        entry.group(2) not in (expected, b"'" + expected + b"'", b'"' + expected + b'"')
        for entry, expected in zip(entries, (b"wubi", b"quick_symbols"))
    ):
        raise ValueError("Only the standard wubi + quick_symbols imports are supported.")
    first = entries[0]
    literal = first.group(2)
    quote = literal[:1] if literal[:1] in (b"'", b'"') else b""
    start = block.start(1) + first.start(2)
    finish = block.start(1) + first.end(2)
    edits = [
        (start, finish, quote + ("wubi" + version).encode() + quote),
        (name.start(2), name.end(2),
         (name.group(2)[:1] if name.group(2)[:1] in (b"'", b'"') else b"") +
         ("wubi" + version + ".extended").encode() +
         (name.group(2)[-1:] if name.group(2)[-1:] in (b"'", b'"') else b"")),
    ]
    for start, finish, replacement in sorted(edits, reverse=True):
        header = header[:start] + replacement + header[finish:]
    return header + data[boundary:]


def build_files(upstream, kit, ice_upstream):
    upstream = upstream.resolve()
    ice_upstream = ice_upstream.resolve()
    output = {}
    records = []
    source_cache = {}
    total = 0

    def source(relative, project="wubi"):
        nonlocal total
        key = (project, relative)
        if key not in source_cache:
            root = upstream if project == "wubi" else ice_upstream
            data = read_file(root, relative, binary=(project == "ice" and relative == "lua/lunar.db"))
            total += len(data)
            if total > MAX_TOTAL_BYTES:
                raise ValueError("The selected source resources exceed the supported total size.")
            source_cache[key] = data
        return source_cache[key]

    def add_source(relative, destination, transformed=None, change="Unchanged", project="wubi"):
        original = source(relative, project)
        content = original if transformed is None else transformed
        if destination in output:
            raise ValueError("Selected resources collide at: " + destination)
        output[destination] = content
        records.append({"project": project, "source": relative, "destination": destination,
                        "source_sha256": sha256(original), "output_sha256": sha256(content),
                        "change": change})

    for name in SHARED_NAMES:
        add_source(name, name)
    for name, expected in (("pinyin.dict.yaml", "pinyin"), ("quick_symbols.dict.yaml", "quick_symbols")):
        header, _, _ = dictionary_header(output[name], expected)
        if re.search(rb"(?m)^[ \t]*import_tables[ \t]*:", header):
            raise ValueError("Unexpected imported tables in shared dictionary " + expected)
    extended = source("wubi.extended.dict.yaml")
    for version in VERSIONS:
        main = "tables/" + version + "/wubi.dict.yaml"
        spelling = "tables/" + version + "/wb_spelling.dict.yaml"
        add_source(main, "wubi" + version + ".dict.yaml",
                   rename_dictionary(source(main), "wubi", "wubi" + version),
                   "Only header name renamed for independent versioned dictionary")
        add_source(spelling, "wb_spelling" + version + ".dict.yaml",
                   rename_dictionary(source(spelling), "wb_spelling", "wb_spelling" + version),
                   "Only header name renamed for independent decomposition database")
        add_source("wubi.extended.dict.yaml", "wubi" + version + ".extended.dict.yaml",
                   rename_extended(extended, version),
                   "Only header name and wubi import renamed; comments and entry payload retained")
    for name in ICE_NAMES:
        add_source(name, name, project="ice")
    for name, destination in ICE_RENAMED:
        add_source(name, destination, project="ice", change="Only filename/location changed; bytes retained")
    for name in OWN_NAMES:
        output[name] = read_file(kit / "rime", name)
    for name in OWN_ASSETS:
        output[name] = read_file(kit, name)
    notice = [
        "Resources supplied from this user's two local upstream downloads.",
        "Wubi reference: " + UPSTREAM_REPO,
        "Rime Ice reference: " + ICE_REPO,
        "Third-party resources retain their original rights and attribution.",
        "Only new overlay/configuration/helper/compatibility files are covered by the kit's CC0 dedication.",
        "Dictionary header identifiers are adapted locally so 86/98/06 can coexist.",
        "Original comments, attribution and dictionary entry payloads are retained.",
        "Rime Ice resources are copied unchanged; default.yaml is named ice_defaults.yaml locally.",
        "Rime Ice license/credits: source-info/rime-ice/LICENSE and Credits.md.",
        "Consult the source's terms before redistributing a generated data package.", "",
    ]
    for record in records:
        notice.extend([record["project"] + ": " + record["source"] + " -> " + record["destination"],
                       "  Source SHA-256: " + record["source_sha256"],
                       "  Output SHA-256: " + record["output_sha256"],
                       "  Change: " + record["change"], ""])
    output["UPSTREAM-SOURCE.txt"] = "\n".join(notice).encode("utf-8")
    docs = {name: read_file(kit, name) for name in DOC_NAMES}
    return output, docs, records


def write_prepared(destination, files, docs):
    if destination.exists():
        raise ValueError("Prepared folder already exists; choose a new destination: " + str(destination))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="wubi-prepare-", dir=destination.parent))
    try:
        for name, data in {**files, **docs}.items():
            target = temporary / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def write_android(destination, files, docs, package_name):
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix="wubi-import-", suffix=".zip", dir=destination.parent)
    os.close(handle)
    metadata = {"packageName": package_name, "versionCode": 0,
                "versionName": "wubi-and-rime-ice-config", "exportTime": int(time.time() * 1000)}
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            directories = {"external/", "external/data/", "external/data/rime/"}
            for name in files:
                parent = Path(name).parent
                while parent != Path("."):
                    directories.add("external/data/rime/" + parent.as_posix() + "/")
                    parent = parent.parent
            for name in sorted(directories, key=lambda item: (item.count("/"), item)):
                archive.writestr(name, b"")
            archive.writestr("metadata.json", json.dumps(metadata, indent=2) + "\n")
            for name, data in files.items():
                assert name.isascii() and ".." not in Path(name).parts
                archive.writestr("external/data/rime/" + name, data)
            for name, data in docs.items():
                archive.writestr(name, data)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity check failed.")
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True, help="Extracted upstream rime-wubi-master folder")
    parser.add_argument("--ice-upstream", type=Path, required=True, help="Extracted upstream rime-ice-main folder")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare", type=Path, help="Create a new Rime folder for manual copying")
    modes.add_argument("--output", type=Path, help="Android ZIP destination")
    parser.add_argument("--package-name", default="org.fcitx.fcitx5.android", help="Installed main-app package ID")
    args = parser.parse_args()
    kit = Path(__file__).resolve().parent
    upstream = args.upstream.resolve()
    ice_upstream = args.ice_upstream.resolve()
    destination = (args.prepare or args.output or kit / "wubi-and-ice-android.zip").resolve()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)+", args.package_name):
        parser.error("Invalid Android package ID.")
    for source_root in (upstream, ice_upstream):
        try:
            destination.relative_to(source_root)
        except ValueError:
            pass
        else:
            parser.error("Choose an output outside both downloaded upstream source folders.")
    protected = {kit / "make_android_import.py"} | {kit / name for name in DOC_NAMES}
    protected |= {kit / "rime" / name for name in OWN_NAMES}
    protected |= {kit / name for name in OWN_ASSETS}
    protected.add(kit / "manual/UPSTREAM-SOURCE.txt")
    if destination in {path.resolve() for path in protected}:
        parser.error("Choose an output different from the kit's source files.")
    try:
        files, docs, _ = build_files(upstream, kit, ice_upstream)
        if args.prepare is not None:
            write_prepared(destination, files, docs)
        else:
            write_android(destination, files, docs, args.package_name)
    except (ValueError, UnicodeError, OSError) as error:
        parser.error(str(error))
    print("Created:", destination)
    print("Available schemas: New Century Wubi06 / Wubi86 / Wubi98 / Rime Ice full Pinyin.")
    print("Android: import or copy, restart, run Rime Deploy, restart again, then choose a schema.")
    print("Import merges existing files. Generated resources retain upstream rights; see NOTICE.txt.")


if __name__ == "__main__":
    main()
