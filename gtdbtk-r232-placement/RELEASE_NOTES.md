**Unofficial convenience mirror.** These are unmodified files from GTDB release 232's GTDB-Tk
reference package: the subset that GTDB-Tk needs to place genomes in the GTDB trees and classify
them. They are repackaged as `.tar.zst` archives (each under GitHub's 2 GiB limit) so you can fetch
only the 7.4 GB (unpacked) that placement needs instead of streaming GTDB's 60.8 GB archive. This mirror is not made or endorsed by the
GTDB team.

- **Source:** [`gtdbtk_r232_data.tar.gz`](https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r232_data.tar.gz)
  (60,806,405,195 bytes, MD5 `25a59e0352b1fd150c589f56559767d4`, checked against GTDB's
  `MD5SUM.txt` while streaming).
- **Included:** `split/` (backbone and the 8 class-level packages), `pplacer/` (full bacterial
  tree and ar53), `markers/`, `masks/`, `metadata/`, `taxonomy/`, `mrca_red/`, `radii/`. Paths are
  kept under `release232/`.
- **Excluded:** `skani/` (the 85.2 GB ANI database) and `msa/` (7.9 GB of reference alignments).
  Without `skani/`, classification stops at genus: the species field stays `s__`. Without `msa/`,
  run `gtdbtk align` with `--skip_gtdb_refs` (de novo trees need it too).
- **Licence:** GTDB data is licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  ([GTDB licences](https://gtdb.ecogenomic.org/licenses)); this mirror is under the same licence.
  Credit: Parks, D.H., et al. and the GTDB team ([gtdb.ecogenomic.org](https://gtdb.ecogenomic.org)).
  The only change is the repackaging.

Usage, the ANI-screen workaround and citations:
[README](https://github.com/dzulfikar08/irit-data/blob/main/README.md).

Files: `SHA256SUMS` and `MD5SUMS` (archives), `MANIFEST.tsv` (every file: archive, path, bytes,
SHA-256), `ARCHIVES.tsv` (per archive: size, hashes, file count, unpacked bytes),
`FOLDER_HASHES.tsv` (GTDB-Tk folder hashes), `FASTTREE_LOGS.tsv`.
