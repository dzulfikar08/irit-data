# `gtdbtk classify` with skip_ani_screen=True, for a data directory without skani/.
# GTDB-Tk 2.8.0's classify always runs the skani ANI screen and has no option to skip it;
# classify_wf sets this same flag itself after its own ANI step. Without the screen, genomes are
# placed in the tree and classified down to genus at most (the species field stays "s__").
# Usage: python classify_no_ani.py classify --genome_dir ... --align_dir ... --out_dir ...
import sys

import gtdbtk.main as m

_orig = m.OptionsParser.classify


def classify(self, options, *a, **k):
    options.skip_ani_screen = True
    return _orig(self, options, *a, **k)


m.OptionsParser.classify = classify

from gtdbtk.__main__ import main  # noqa: E402

sys.argv = ["gtdbtk"] + sys.argv[1:]
main()
