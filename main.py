#!/usr/bin/env python3

from svgbuild.inkscape import Inkscape
from svgbuild.svgbuild import SVGBuild
import argparse

def main():
	Inkscape.init()

	if not Inkscape.installed:
		print("Inkscape is not installed")
		print("Please install inkscape and add to your environment variable")
		return 1;

	parser = argparse.ArgumentParser(description='SVGBuild command line interface')
	parser.add_argument('filename', help='svg file name')
	parser.add_argument('--folder', default='', help='output folder name')
	parser.add_argument('--name', default='', help='output prefix file name')
	parser.add_argument('--line-color', default='#000000', help='object line color')
	parser.add_argument('--use-object-line-color', default=False, action='store_true', help='use object\'s line color, this will override --line-color')
	parser.add_argument('--object-color', default='', help='custom object color while building path')
	parser.add_argument('--use-object-color', default=False, action='store_true', help='use object\'s color, this will override --object-color')
	parser.add_argument('--add-marker', default=False, help='add marker style')
	parser.add_argument('--marker-name', default='diamond', help='add marker style')
	parser.add_argument('--background-color', default='#FFFFFF', help='add background color')
	parser.add_argument('--no-background', default=False, action='store_true', help='save as transparent png')
	parser.add_argument('--build-path', default=False, action='store_true', help='build path')
	parser.add_argument('--detail-path', default=False, action='store_true', help='build detailed path')
	parser.add_argument('--path-node-count', default=0, type=int, help='build path per n node')
	parser.add_argument('--group-node', default=False, action='store_true', help='build path by node group command')
	parser.add_argument('--group-node-count', default=0, type=int, help='build path per n node group command')
	parser.add_argument('--circle-path', default=False, action='store_true', help='circular path')
	parser.add_argument('--close-path', default=False, action='store_true', help='closed path')
	parser.add_argument('--page-view', default=False, action='store_true', help='build page area')
	parser.add_argument('--bring-to-top', default=False, action='store_true', help='bring object to top')
	parser.add_argument('--backward', default=False, action='store_true', help='build from last object')
	parser.add_argument('--from', default=0, type=int, help='starting frame number')
	parser.add_argument('--until', default=99999, type=int, help='ending frame number')
	parser.add_argument('--zoom', default=6.0, type=float, help='zoom camera')
	parser.add_argument('--show-camera', default=False, action='store_true', help='show camera (only if --page-view)')
	parser.add_argument('--camera-frame', default='#FF0000', help='camera frame\'s color')
	parser.add_argument('--continue', default=False, action='store_true', help='continue previous build if exist')
	parser.add_argument('--restart', default=False, action='store_true', help='delete previous build if exist')
	options = parser.parse_args()
	aSvgbuild = SVGBuild()
	if aSvgbuild.setOptions(vars(options)):
		return aSvgbuild.start()

if __name__ == "__main__":
    main()
