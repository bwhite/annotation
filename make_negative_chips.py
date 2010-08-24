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

"""Generate small images (chips) randomly given 4 points per region.

Usage:
python make_negative_chips.py <poly_json> <chip_dir> <chip_height> <chip_width>
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


def generate_coords(coord, angle, height, width):
    out_coords = [coord]
    coord = np.array(coord)
    pd2 = np.pi / 2.
    out_coords.append(coord + width * np.array([np.cos(angle + pd2), np.sin(angle + pd2)]))
    out_coords.append(coord + height * np.array([np.cos(angle), np.sin(angle)]))
    return out_coords

def random_coords(c, border, num_coords):
    """Generates a random pixel some distance from the edge as a border.

    Assumes c contains 4 (x, y) points, in the configuration
    (top left, top right, bottom right, bottom left)
    """
    min_x = int(max(c[0][0], c[3][0]))
    max_x = int(min(c[1][0], c[2][0]))
    min_y = int(max(c[0][1], c[1][1]))
    max_y = int(min(c[2][1], c[3][1]))
    border = int(border)
    # Check assumptions
    checks = False
    checks |= min_x > c[1][0]
    checks |= min_x > c[2][0]
    checks |= min_y > c[2][1]
    checks |= min_y > c[3][1]
    checks |= max_x < c[0][0]
    checks |= max_x < c[3][0]
    checks |= max_y < c[0][1]
    checks |= max_y < c[1][1]
    min_x += border
    max_x -= border
    min_y += border
    max_y -= border
    checks |= min_x > max_x
    checks |= min_y > max_y
    if not checks:
        for x in range(num_coords):
            yield [np.random.randint(min_x, max_x), np.random.randint(min_y, max_y)]

def draw_poly(img, points, poly_color):
    cv.FillConvexPoly(img, tuple([tuple(map(int, x)) for x in points]), poly_color)

def main(poly_json, chip_dir, chip_height, chip_width):
    chip_height = int(chip_height)
    chip_width = int(chip_width)
    with open(poly_json, 'r') as fp:
        j = json.load(fp)
    try:
        os.mkdir(chip_dir)
    except OSError:
        pass
    h = cv.CreateMat(2, 3, cv.CV_32F)
    chip_img = cv.CreateImage((chip_width, chip_height), cv.IPL_DEPTH_32F, 3)
    chip_img_out = cv.CreateImage((chip_width, chip_height), cv.IPL_DEPTH_8U, 3)
    chip_coords = [(0., 0.), (chip_width, 0.), (0., chip_height)]
    # Generate chips
    for img_fn, coords in j.items():
        img = cv.LoadImage(img_fn)
        orig_img = cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_32F, 3)
        cv.CvtScale(img, orig_img)
        for coord_ind, coord_4gon in enumerate(coords):
            rnd_coords = random_coords(coord_4gon, int(max(chip_width, chip_height)), 500)
            for coord in rnd_coords:
                coord = generate_coords(coord, 2 * np.pi * np.random.random(), chip_height, chip_width)
                coord = map(tuple, coord)
                cv.GetAffineTransform(coord, chip_coords, h)
                cv.WarpAffine(orig_img, chip_img, h)
                cv.CvtScale(chip_img, chip_img_out)
                base_fn = os.path.basename(img_fn)
                coord_str = [','.join([str(y) for y in x]) for x in coord]
                coord_fn = '_'.join(coord_str)
                chip_fn_out = '%s/%s_%s' % (chip_dir, coord_fn, base_fn)
                cv.SaveImage(chip_fn_out, chip_img_out)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])


