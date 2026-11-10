#!/usr/bin/env python3
"""GTDB-Tk folder hashes for an unpacked GTDB-Tk R232 data directory.

sha1_dir is the algorithm from GTDB-Tk 2.8.0 (gtdbtk/tools.py): one SHA-1 over the contents of
every file below a folder, in sorted path order (file names are not hashed). REF_HASHES are the
R232 values from gtdbtk/config/common.py (get_REF_HASHES), which `gtdbtk check_install` compares.

Usage:
  gtdb_hashes.py compute DATA_DIR OUT.tsv      hash folders, fail on a REF_HASHES mismatch
  gtdb_hashes.py compare DATA_DIR EXPECTED.tsv recompute, fail if any differs from EXPECTED.tsv
DATA_DIR is the GTDB-Tk data directory (GTDBTK_DATA_PATH), e.g. .../release232.
"""
import hashlib
import os
import sys

# GTDB-Tk 2.8.0, gtdbtk/config/common.py, R232.
REF_HASHES = {
    "pplacer": "4e8ffa1133f10bde827bddb81413d06d62de341e",
    "masks": "84c7f7a17adc134db4161b15db10ae58389a90c1",
    "markers": "163f542c3f0a40f59df45d453aa235b39aa96e27",
    "radii": "546c1769ae19c946ba94b91482f32002a204f598",
    "msa": "8cf2ed4ea53f9201b127dbeed71bcc0fff27e204",
    "metadata": "1febdba7d2513a8f43c409423aee83ed99df7a78",
    "taxonomy": "c1e1766fa610229cb7cb45edc9a8fa0eafb44c96",
    "skani": "00afba7b7e89a27e4d9aa9b4ce176550b56af09e",
    "mrca_red": "10a0fc1ca4199ff33e6c2fc4bc933318962ab212",
}
EXCLUDED = {"msa", "skani"}


def sha1_dir(path):
    queue = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            queue.append(os.path.join(root, f))
    hasher = hashlib.sha1()
    for p in sorted(queue):
        with open(p, "rb") as fh:
            for buf in iter(lambda: fh.read(1 << 20), b""):
                hasher.update(buf)
    return hasher.hexdigest()


def folders(data):
    out = [k for k in REF_HASHES if k not in EXCLUDED]
    out += ["split", "split/backbone", "split/class_level"]
    for root, dirs, _files in os.walk(data):
        for d in dirs:
            if d.endswith(".refpkg"):
                out.append(os.path.relpath(os.path.join(root, d), data))
    seen, uniq = set(), []
    for f in out:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq


def compute(data):
    rows = []
    for f in folders(data):
        h = sha1_dir(os.path.join(data, f))
        ref = REF_HASHES.get(f, "")
        status = "no reference" if not ref else ("OK" if h == ref else "MISMATCH")
        rows.append((f, h, ref, status))
        print(f"{f}\t{h}\t{status}", flush=True)
    for f in sorted(EXCLUDED):
        rows.append((f, "", REF_HASHES[f], "excluded from mirror"))
    return rows


def main():
    mode, data, tsv = sys.argv[1:4]
    if mode == "compute":
        rows = compute(data)
        with open(tsv, "w") as fh:
            fh.write("folder\tsha1_dir\tgtdbtk_2.8.0_ref_hash\tstatus\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
        bad = [r for r in rows if r[3] == "MISMATCH"]
    elif mode == "compare":
        expected = {}
        with open(tsv) as fh:
            next(fh)
            for line in fh:
                f, h, ref, status = line.rstrip("\n").split("\t")
                if h:
                    expected[f] = (h, ref)
        bad = []
        for f, (h_exp, ref) in expected.items():
            h = sha1_dir(os.path.join(data, f))
            ok = h == h_exp and (not ref or h == ref)
            print(f"{f}\t{h}\t{'OK' if ok else 'MISMATCH (expected ' + h_exp + ')'}", flush=True)
            if not ok:
                bad.append(f)
    else:
        sys.exit(__doc__)
    if bad:
        sys.exit(f"hash mismatch: {bad}")


if __name__ == "__main__":
    main()
