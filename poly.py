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

"""
Usage:
python poly.py <image_dir> <poly_json> (num_points=3)
"""

__author__ = 'Brandyn A. White <bwhite@cs.umd.edu>'
__version__ = '0.1'
__license__ = 'GPL V3'

import cv
import glob
import json
import sys


def mouse_event_probe(event, x, y, flags, param):
    events = {cv.CV_EVENT_MOUSEMOVE: 'CV_EVENT_MOUSEMOVE',
              cv.CV_EVENT_LBUTTONDOWN: 'CV_EVENT_LBUTTONDOWN',
              cv.CV_EVENT_RBUTTONDOWN: 'CV_EVENT_RBUTTONDOWN',
              cv.CV_EVENT_MBUTTONDOWN: 'CV_EVENT_MBUTTONDOWN',
              cv.CV_EVENT_LBUTTONUP: 'CV_EVENT_LBUTTONUP',
              cv.CV_EVENT_RBUTTONUP: 'CV_EVENT_RBUTTONUP',
              cv.CV_EVENT_MBUTTONUP: 'CV_EVENT_MBUTTONUP',
              cv.CV_EVENT_LBUTTONDBLCLK: 'CV_EVENT_LBUTTONDBLCLK',
              cv.CV_EVENT_RBUTTONDBLCLK: 'CV_EVENT_RBUTTONDBLCLK',
              cv.CV_EVENT_MBUTTONDBLCLK: 'CV_EVENT_MBUTTONDBLCLK'}
    print((event, events[event], (x, y), flags, param))


class PolyAnnotator(object):
    def __init__(self, image_dir, poly_json_fn, num_points=4):
        self.win_name = 'Poly'
        cv.NamedWindow(self.win_name)
        cv.SetMouseCallback(self.win_name, self.mouse_handler)
        self.image_dir = image_dir
        self.poly_json_fn = poly_json_fn
        self.image_list = glob.glob(image_dir + '/*')
        self.image_index = 0
        self.num_points = num_points
        self.points = []
        # Graphical Settings
        self.point_rad = 5
        self.point_color_first = (255, 255, 0)
        self.point_color_other = (255, 0, 0)
        self.poly_color = (0, 0, 255)
        try:
            with open(self.poly_json_fn, 'r') as fp:
                self.polys_accepted = json.load(fp)
        except IOError:
            self.polys_accepted = {}
        self.load_image()

    def load_image(self):
        if 0 <= self.image_index < len(self.image_list):
            fn = self.image_list[self.image_index]
            print(fn)
            self.img = cv.LoadImage(fn)
            self.points = []
            try:
                for points in self.polys_accepted[fn]:
                    points = [tuple(map(int, x)) for x in points]
                    for point_num, point in enumerate(points):
                        self.draw_circle(point, point_num)
                    self.draw_poly(points)
            except KeyError:
                pass
            self.img_orig = cv.CloneImage(self.img)
            self.refresh()

    def draw_circle(self, point, point_num):
        cv.Circle(self.img, point, self.point_rad, self.point_color(point_num))

    def draw_poly(self, points):
        cv.FillConvexPoly(self.img, points, self.poly_color)

    def point_color(self, num):
        if num == 0:
            return self.point_color_first
        return self.point_color_other

    def next_image(self):
        if self.image_index < len(self.image_list) - 1:
            self.image_index += 1
            self.load_image()

    def prev_image(self):
        if self.image_index > 0:
            self.image_index -= 1
            self.load_image()

    def display_commands(self):
        commands = '-> - Next Image\n' \
            '<- - Prev Image\n' \
            'a - Accept active points\n'
        print(commands)

    def refresh_clear(self):
        self.img = cv.CloneImage(self.img_orig)
        self.points = []
        self.refresh()

    def refresh(self):
        cv.ShowImage(self.win_name, self.img)

    def accept_points(self):
        fn = self.image_list[self.image_index]
        try:
            self.polys_accepted[fn].append(self.points)
        except KeyError:
            self.polys_accepted[fn] = [self.points]
        self.points = []
        self.img_orig = cv.CloneImage(self.img)
        with open(self.poly_json_fn, 'w') as fp:
            json.dump(self.polys_accepted, fp)

    def mouse_handler(self, event, x, y, flags, param):
        print((event, x, y, flags, param))
        if event == cv.CV_EVENT_LBUTTONDOWN:
            if len(self.points) < self.num_points:
                self.draw_circle((x, y), len(self.points))
                self.points.append((x, y))
                if len(self.points) == self.num_points:
                    self.draw_poly(self.points)
                self.refresh()
        elif event == cv.CV_EVENT_RBUTTONDOWN:
            self.refresh_clear()

    def run(self):
        self.display_commands()
        while 1:
            user_key = cv.WaitKey(7)
            # Accept points
            if user_key == 97 and len(self.points) == self.num_points:
                self.accept_points()
            elif user_key == 65361:
                self.prev_image()
            elif user_key == 65363:
                self.next_image()


def _main(image_dir, poly_json, num_points=3):
    PolyAnnotator(image_dir, poly_json, int(num_points)).run()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    _main(*sys.argv[1:])
