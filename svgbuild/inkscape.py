# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os, subprocess, platform, sys, re
from pkg_resources import parse_version

from .utils import *

class Inkscape():
	installed = False
	version = "0"
	cmd = []

	@staticmethod
	def init():

		c = ["inkscape", "-V"]
		if platform.system() == "Windows":
			c = ["inkscape.com", "-V"]

		# print(cmd)
		# print(platform.system())
		# print(platform.release())

		out = qx(c)

		# run = subprocess.Popen([Inkscape.cmd,"-z","-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		# (out, err) = run.communicate()
		# if run.returncode != 0:
		# 	return

		sysInfo = sys.version_info
			
		if sysInfo.major == 3:
			out = out.decode('utf-8')

		# inkscape = re.search('^Inkscape ([0-9\.]*).*\([^\)]*\)', out)
		inkscape = re.search('^Inkscape ([0-9\.]*)', out)
		if inkscape:
			Inkscape.version = inkscape.group(1)
			Inkscape.installed = True

			if parse_version(Inkscape.version) < parse_version('0.93'):
				Inkscape.cmd = ['inkscape', '-z']
			else:
				Inkscape.cmd = ['inkscape']

	@staticmethod
	def exportPngCmd(png):
		if parse_version(Inkscape.version) < parse_version('0.93'):
			return '--export-png=%s' % png
		else:
			return '--export-filename=%s' % png

	@staticmethod
	def exportPngCmdDict(png):
		if parse_version(Inkscape.version) < parse_version('0.93'):
			return {'--export-png': png}
		else:
			return {'--export-filename': png}
