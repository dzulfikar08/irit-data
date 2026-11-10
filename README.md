# irit-data

Data mirrors for [irit](https://github.com/dzulfikar08/irit): unpacked subsets of public reference
data, with credit and licences. Each mirror is a GitHub release in this repository. The files are
the publisher's own, repackaged so that a laptop can fetch only the part it needs.

These mirrors are **unofficial**. They are not made or endorsed by the original publishers. If a
file here differs from the publisher's, the publisher's copy is right: please
[open an issue](https://github.com/dzulfikar08/irit-data/issues).

| Release | What | Licence |
|---|---|---|
| [`gtdbtk-r232-placement-v1`](https://github.com/dzulfikar08/irit-data/releases/tag/gtdbtk-r232-placement-v1) | GTDB R232: the GTDB-Tk reference data that placement and classification need | CC BY-SA 4.0 |

## GTDB-Tk R232 placement data

### What it is

GTDB publishes the GTDB-Tk reference data for release 232 as a single 60.8 GB gzip archive that
unpacks to 100.5 GB. Most of that is the skani ANI database (85.2 GB). Placing genomes in the GTDB
trees uses about 7.4 GB of it. This release holds that 7.4 GB, unmodified, split into archives you
can download one by one.

- **Source:** [`gtdbtk_r232_data.tar.gz`](https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/gtdbtk_r232_data.tar.gz)
  from [GTDB's downloads](https://data.gtdb.ecogenomic.org/releases/release232/232.0/auxillary_files/gtdbtk_package/full_package/),
  60,806,405,195 bytes, MD5 `25a59e0352b1fd150c589f56559767d4` (GTDB's `MD5SUM.txt`). The build
  checks the MD5 while it streams the archive and stops if it differs.
- **Unmodified:** every file is byte-for-byte the one in GTDB's archive. Only the packaging
  changed: `.tar.zst` instead of one `.tar.gz`. `MANIFEST.tsv` lists the SHA-256 of every file, and
  `FOLDER_HASHES.tsv` has the folder hashes that `gtdbtk check_install` computes. For every folder
  that GTDB-Tk 2.8.0 checks and this release includes, they equal GTDB-Tk's own reference hashes.
- **How it was built and checked:** [`.github/workflows/gtdbtk-r232-placement.yml`](.github/workflows/gtdbtk-r232-placement.yml),
  on GitHub-hosted runners. A second, fresh runner downloads every asset, checks all hashes,
  unpacks, and classifies GTDB's test genome with GTDB-Tk 2.8.0 from these files alone. The release
  notes link the run.

### What is included

| Archive | Folder (under `release232/`) | Needed for |
|---|---|---|
| `gtdbtk-r232-core.tar.zst` | `markers/`, `masks/`, `metadata/`, `taxonomy/`, `mrca_red/`, `radii/`, `split/*/red/`, `split/class_level/tree_mapping.tsv` | always |
| `gtdbtk-r232-split-backbone.tar.zst` | `split/backbone/` | bacteria (default split mode) |
| `gtdbtk-r232-split-class-level-1` … `-8.tar.zst` | `split/class_level/pplacer/gtdbtk.package.N.refpkg/` | bacteria (default split mode) |
| `gtdbtk-r232-pplacer-ar53.tar.zst` | `pplacer/gtdb_r232_ar53.refpkg/` | archaea |
| `gtdbtk-r232-pplacer-bac120-full-tree.tar.zst` | `pplacer/gtdb_r232_bac120.refpkg/` | bacteria with `--full_tree` |

Sizes and hashes: the release notes, `ARCHIVES.tsv` and `SHA256SUMS`.

Every reference package (`*.refpkg`) carries its own `gtdb_r232_bac120_fasttree.log` or
`..._ar53_fasttree.log` (about 518 MB each). It is the FastTree log that the refpkg's
`CONTENTS.json` lists as `tree_stats`; pplacer (and gPlace) read the substitution-model
parameters from it, so it is required. `FASTTREE_LOGS.tsv` lists their hashes. Each archive keeps
its own copy, so any archive works on its own.

### What is excluded, and why

| Folder | Size | Used for | Effect of leaving it out |
|---|---:|---|---|
| `skani/` | 85.2 GB | the ANI species screen in `classify` and `ani_rep` | no species names: classification stops at genus (`s__` stays empty) |
| `msa/` | 7.9 GB | `align` without `--skip_gtdb_refs`, de novo trees | run `gtdbtk align --skip_gtdb_refs` |

Getting either folder still means streaming GTDB's full archive, for example
`curl -fsSL URL | tar -xz release232/skani`.

### How to use it

Download everything (about the size in the release notes), check it, and unpack it into one
directory:

```sh
mkdir -p ~/gtdbtk-r232 && cd ~/gtdbtk-r232
gh release download gtdbtk-r232-placement-v1 -R dzulfikar08/irit-data
sha256sum -c SHA256SUMS
for f in *.tar.zst; do zstd -dc "$f" | tar -x; done
export GTDBTK_DATA_PATH=$PWD/release232
```

Without `gh`, download each asset with
`curl -fLO https://github.com/dzulfikar08/irit-data/releases/download/gtdbtk-r232-placement-v1/<name>`
(names are in `SHA256SUMS`). With GNU tar 1.31 or later, `tar --zstd -xf <name>` also works. You
may skip `pplacer-bac120-full-tree` unless you use `--full_tree`.

`gtdbtk check_install` will report `msa` and `skani` as mismatched, because they are missing; the
other folders should be `OK`.

**Classifying without the skani database.** GTDB-Tk 2.8.0's `classify` always runs the ANI screen,
and has no option to skip it. [`scripts/classify_no_ani.py`](scripts/classify_no_ani.py) runs
`gtdbtk classify` with the screen turned off (`skip_ani_screen`, the flag `classify_wf` sets after
its own ANI step):

```sh
gtdbtk identify --genome_dir genomes -x fna --out_dir run/identify --cpus 4
gtdbtk align --identify_dir run/identify --out_dir run/align --skip_gtdb_refs --cpus 4
python classify_no_ani.py classify --genome_dir genomes -x fna \
  --align_dir run/align --out_dir run/classify --cpus 4
```

Every genome is then placed in the tree, and classified to genus at most. The method and its
results are described in irit's
[GTDB R232 placement test](https://github.com/dzulfikar08/irit/blob/main/docs/research/gtdb-placement-test.md).

**Memory.** pplacer needs far more RAM for these trees than a laptop has (see the GTDB-Tk
documentation). [gPlace](https://github.com/cmc-aau/gPlace) 0.1.1 placed genomes on all R232 trees
under an 8.5 GiB cap in the test above.
[`scripts/pplacer-gplace-shim.sh`](scripts/pplacer-gplace-shim.sh), installed first on `PATH` as
`pplacer`, makes GTDB-Tk call gPlace instead. gPlace describes itself as work in progress: compare
with pplacer before you publish results.

### Credit, citation and licence

The data is from the **Genome Taxonomy Database (GTDB)**, by Donovan H. Parks, Maria Chuvochina,
Pierre-Alain Chaumeil, Christian Rinke, Philip Hugenholtz and the GTDB team
([gtdb.ecogenomic.org](https://gtdb.ecogenomic.org)). If you use it, cite GTDB and GTDB-Tk as they
ask on [their about page](https://gtdb.ecogenomic.org/about), for example:

- Parks, D.H., et al. (2025). GTDB release 10: a complete and systematic taxonomy for 715 230
  bacterial and 17 245 archaeal genomes. *Nucleic Acids Research*, gkaf1040.
  https://doi.org/10.1093/nar/gkaf1040
- Chaumeil, P.-A., et al. (2022). GTDB-Tk v2: memory friendly classification with the genome
  taxonomy database. *Bioinformatics*, 38(23), 5315–5316.
  https://doi.org/10.1093/bioinformatics/btac672

GTDB data is licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International licence](https://creativecommons.org/licenses/by-sa/4.0/)
(see [GTDB's licences page](https://gtdb.ecogenomic.org/licenses)). The data in this repository's
releases is shared under the same licence; its legal code is in [`LICENSE`](LICENSE). Changes
made: the files were taken out of GTDB's archive and repackaged into several archives; no file was
changed, and the `skani/` and `msa/` folders were left out. GTDB-Tk itself is GPL-3.0 and is not
redistributed here.

The scripts in [`scripts/`](scripts/) and the workflow are also offered under CC BY-SA 4.0 to keep
one licence in the repository. `scripts/gtdb_hashes.py` reimplements GTDB-Tk's `sha1_dir` and
copies its R232 reference hashes.

### Links

GTDB-Tk issues and discussions about laptop-sized GTDB-Tk data may link here. Questions about the
data itself belong with GTDB ([forum](https://forum.gtdb.ecogenomic.org)); questions about this
mirror go to [this repository's issues](https://github.com/dzulfikar08/irit-data/issues).
