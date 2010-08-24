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
python make_positive_chips.py <poly_json> <chip_dir> (poly_filter_json)
"""

__author__ = 'Brandyn A. White <bwhite@cs.umd.edu>'
__license__ = 'GPL V3'

import json
import sys
import time
import os

import cv
import numpy as np


def coord_h_w(coord):
    coord = np.array(coord)
    w = np.linalg.norm(coord[1] - coord[0])
    h = np.linalg.norm(coord[1] - coord[2])
    return h, w


def generate_coords(coord, height, width):
    coord = np.array(coord)
    out_coords = [coord[1]]
    diff = coord[2] - coord[1]
    diff = diff / np.linalg.norm(diff)
    angle = np.arctan2(diff[1], diff[0])
    pd2 = np.pi / 2.
    out_coords.append(coord[1] + width * np.array([np.cos(angle + pd2), np.sin(angle + pd2)]))
    out_coords.append(coord[1] + height * np.array([np.cos(angle), np.sin(angle)]))
    #print('Angle:[%s] Coord:[%s] OutCoords:[%s] H:[%s] W:[%s] Dw:[%s] Wh:[%s]' % (str(angle), str(coord), str(out_coords), str(height), str(width), str(np.linalg.norm(out_coords[0] - out_coords[1])), str(np.linalg.norm(out_coords[0] - out_coords[2]))))
    return out_coords


def main(poly_json, chip_dir, poly_filter_json=None):
    with open(poly_json, 'r') as fp:
        j = json.load(fp)
    try:
        os.mkdir(chip_dir)
    except OSError:
        pass
    cv.NamedWindow('win')
    # Compute median height and width
    heights, widths = [], []
    for img_fn, coords in j.items():
        for coord in coords:
            coord = map(tuple, coord)
            h, w = coord_h_w(coord)
            heights.append(h)
            widths.append(w)
    height = int(np.round(np.median(heights)))
    width = int(np.round(np.median(widths)))
    chip_height = height
    chip_width = width
    #print('height:[%f] width:[%f]' % (height, width))
    h = cv.CreateMat(2, 3, cv.CV_32F)
    chip_img = cv.CreateImage((chip_width, chip_height), cv.IPL_DEPTH_32F, 3)
    chip_img_out = cv.CreateImage((chip_width, chip_height), cv.IPL_DEPTH_8U, 3)
    chip_coords = [(0., 0.), (chip_width, 0.), (0., chip_height)]
    # Generate chips
    for img_fn, coords in j.items():
        img = cv.LoadImage(img_fn)
        orig_img = cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_32F, 3)
        cv.CvtScale(img, orig_img)
        for coord_ind, coord in enumerate(coords):
            coord = generate_coords(coord, height, width)
            coord = map(tuple, coord)
            cv.GetAffineTransform(coord, chip_coords, h)
            cv.WarpAffine(orig_img, chip_img, h)
            cv.CvtScale(chip_img, chip_img_out)
            # This is a display used for interactive removal
            k = -1
            if poly_filter_json:
                cv.ShowImage('win', chip_img_out)
            while poly_filter_json:
                k = cv.WaitKey(100)
                if k != -1:
                    print(k)
                    if k == 100 and poly_filter_json:
                        del j[img_fn][coord_ind]
                    break
            if k != 100:
                base_fn = os.path.basename(img_fn)
                coord_str = [','.join([str(y) for y in x]) for x in coord]
                coord_fn = '_'.join(coord_str)
                chip_fn_out = '%s/%s_%s' % (chip_dir, coord_fn, base_fn)
                #print(chip_fn_out)
                cv.SaveImage(chip_fn_out, chip_img_out)

    if poly_filter_json:
        with open(poly_filter_json, 'w') as fp:
            json.dump(j, fp)
    return chip_height, chip_width


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])


