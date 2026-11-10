#!/usr/bin/env python3
"""Pack an extracted GTDB-Tk R232 data directory (without skani/ and msa/) into .tar.zst units.

Usage: package.py PARENT OUTDIR
PARENT holds release232/. Writes OUTDIR/*.tar.zst, MANIFEST.tsv, ARCHIVES.tsv, SHA256SUMS,
MD5SUMS and FASTTREE_LOGS.tsv. Paths inside the archives start with release232/, so every archive
unpacks into the same GTDB-Tk data directory layout. Fails if any archive is 2 GiB or larger.
"""
import hashlib
import os
import subprocess
import sys

TOP = "release232"
PREFIX = "gtdbtk-r232"
EXCLUDED_TOP = ("skani", "msa")
LIMIT = 2 * 1024**3  # GitHub release assets must be under 2 GiB


def file_hashes(path):
    s, m = hashlib.sha256(), hashlib.md5()
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 20), b""):
            s.update(buf)
            m.update(buf)
    return s.hexdigest(), m.hexdigest()


def main():
    parent, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    root = os.path.join(parent, TOP)

    files = []
    for dirpath, _dirs, names in os.walk(root):
        for n in names:
            rel = os.path.relpath(os.path.join(dirpath, n), parent)
            if rel.split("/")[1] in EXCLUDED_TOP:
                sys.exit(f"excluded folder present: {rel}")
            files.append(rel)
    files.sort()

    units = {}  # unit name -> path prefix
    units["split-backbone"] = f"{TOP}/split/backbone/"
    cls = os.path.join(root, "split/class_level/pplacer")
    for d in sorted(os.listdir(cls)):
        n = d.removeprefix("gtdbtk.package.").removesuffix(".refpkg")
        units[f"split-class-level-{n}"] = f"{TOP}/split/class_level/pplacer/{d}/"
    units["pplacer-bac120-full-tree"] = f"{TOP}/pplacer/gtdb_r232_bac120.refpkg/"
    units["pplacer-ar53"] = f"{TOP}/pplacer/gtdb_r232_ar53.refpkg/"

    assign = {u: [] for u in units}
    assign["core"] = []
    for f in files:
        for u, p in units.items():
            if f.startswith(p):
                assign[u].append(f)
                break
        else:
            assign["core"].append(f)

    manifest, archives = [], []
    for u, members in assign.items():
        if not members:
            sys.exit(f"unit {u} is empty")
        name = f"{PREFIX}-{u}.tar.zst"
        path = os.path.join(out, name)
        listing = os.path.join(out, f".{u}.list")
        with open(listing, "wb") as fh:
            fh.write(b"\0".join(m.encode() for m in members) + b"\0")
        tar = subprocess.Popen(
            ["tar", "--create", "--format=gnu", "--sort=name", "--owner=0", "--group=0",
             "--numeric-owner", "--file", "-", "--directory", parent,
             "--no-recursion", "--null", "--files-from", listing],
            stdout=subprocess.PIPE)
        subprocess.run(["zstd", "-19", "--long=27", "-T0", "-q", "-f", "-o", path],
                       stdin=tar.stdout, check=True)
        tar.stdout.close()
        if tar.wait() != 0:
            sys.exit(f"tar failed for {u}")
        os.remove(listing)

        unpacked = 0
        for m in members:
            size = os.path.getsize(os.path.join(parent, m))
            sha, _md5 = file_hashes(os.path.join(parent, m))
            unpacked += size
            manifest.append((name, m, size, sha))
        size = os.path.getsize(path)
        if size >= LIMIT:
            sys.exit(f"{name} is {size} bytes, over GitHub's 2 GiB asset limit")
        sha, md5 = file_hashes(path)
        prefix = units.get(u, f"{TOP}/ (markers, masks, metadata, taxonomy, mrca_red, radii, split/*/red, split/class_level/tree_mapping.tsv)")
        archives.append((name, size, sha, md5, len(members), unpacked, prefix))
        print(f"{name}\t{size}\t{len(members)} files\t{unpacked} bytes unpacked", flush=True)

    with open(os.path.join(out, "MANIFEST.tsv"), "w") as fh:
        fh.write("archive\tpath\tbytes\tsha256\n")
        for r in manifest:
            fh.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(out, "ARCHIVES.tsv"), "w") as fh:
        fh.write("archive\tbytes\tsha256\tmd5\tfiles\tunpacked_bytes\tcontents\n")
        for r in archives:
            fh.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(out, "SHA256SUMS"), "w") as fh:
        for r in archives:
            fh.write(f"{r[2]}  {r[0]}\n")
    with open(os.path.join(out, "MD5SUMS"), "w") as fh:
        for r in archives:
            fh.write(f"{r[3]}  {r[0]}\n")
    with open(os.path.join(out, "FASTTREE_LOGS.tsv"), "w") as fh:
        fh.write("path\tbytes\tsha256\n")
        logs = [r for r in manifest if r[1].endswith("fasttree.log")]
        for r in logs:
            fh.write(f"{r[1]}\t{r[2]}\t{r[3]}\n")
    distinct = {r[3] for r in logs}
    print(f"fasttree.log files: {len(logs)}, distinct sha256: {len(distinct)}")
    print(f"total archive bytes: {sum(r[1] for r in archives)}; "
          f"unpacked bytes: {sum(r[5] for r in archives)}; files: {len(manifest)}")


if __name__ == "__main__":
    main()
