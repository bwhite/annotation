#!/usr/bin/env python
# (C) Copyright 2010 Brandyn A. White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generate small images (chips).

Given an optional filtered path, it will allow you to interactively remove
samples by pressing the 'd' key

Usage:
python make_positive_chips.py <pos_json> <neg_json>
"""

__author__ = 'Brandyn A. White <bwhite@cs.umd.edu>'
__license__ = 'GPL V3'

import os
import sys
import glob
import shutil
import random

import make_positive_chips
import make_negative_chips


def main(pos_json, neg_json, per_class_train=300):
    ds = ['chips', 'chips/trainchipspos', 'chips/testchipspos', 'chips/trainchipsneg', 'chips/testchipsneg']
    for d in ds:
        try:
            os.mkdir(d)
        except OSError:
            pass
    chip_height, chip_width = make_positive_chips.main(pos_json, 'chips/chipspos')
    make_negative_chips.main(neg_json, 'chips/chipsneg', chip_height, chip_width)
    # Partition the chips into pos/neg
    chips_pos = glob.glob('chips/chipspos/*')
    random.shuffle(chips_pos)
    chips_neg = glob.glob('chips/chipsneg/*')
    random.shuffle(chips_neg)
    for chip_fn in chips_pos[:per_class_train]:
        shutil.move(chip_fn, 'chips/trainchipspos/')
    for chip_fn in chips_pos[per_class_train:]:
        shutil.move(chip_fn, 'chips/testchipspos/')
    for chip_fn in chips_neg[:per_class_train]:
        shutil.move(chip_fn, 'chips/trainchipsneg/')
    for chip_fn in chips_neg[per_class_train:]:
        shutil.move(chip_fn, 'chips/testchipsneg/')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
