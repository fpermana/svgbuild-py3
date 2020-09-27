# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from lxml import etree
import re
from .unit_converter import *


class SVG():
    def __init__(self):
        # Prepares the virtual svg drawing container.
        self.filename = None
        self.tree = None
        self.root = None
        self.ids = { }
        self.xs = 1.
        self.ys = 1.

    def survey(self):
        # Scan through the XML entities to ensure proper id attributes.
        # Inkscape files write a unique id for each element, and gives a
        # general "flipped Y" coordinate space inside a page of known size.
        # Non-Inkscape SVG files may not comply with these optional niceties.
        # We check that these features are available so Inkscape can render
        # and resolve rendering locations for every entity later on.

        viewBox = []
        if 'viewBox' in self.root.attrib:
            viewBox = self.root.attrib['viewBox'].split(' ')

        # ensure at least a default page size (arbitrarily, us letter)
        if 'width' not in self.root.attrib:
            self.root.attrib['width'] = '744.09448819'
        else:
            w = self.root.attrib['width']
            uw = re.search(r'[a-zA-Z]*$',w)
            if uw:
                w = re.sub(r'[a-zA-Z]', '', str(w))
                w = convert_unit(float(w), uw.group())
                self.root.attrib['width'] = str(w)

                if len(viewBox) == 4:
                    # viewBox[2] = str(w)
                    self.xs = float(viewBox[2]) / w

        if 'height' not in self.root.attrib:
            self.root.attrib['height'] = '1052.3622047'
        else:   
            h = self.root.attrib['height']
            uh = re.search(r'[a-zA-Z]*$',h)
            if uh:
                h = re.sub(r'[a-zA-Z]', '', str(h))
                h = convert_unit(float(h), uh.group())
                self.root.attrib['height'] = str(h)

                if len(viewBox) == 4:
                    # viewBox[3] = str(h)
                    self.ys = float(viewBox[3]) / h

        # if len(viewBox) == 4:
        #     self.root.attrib['viewBox'] = ' '.join(viewBox).strip()

        # scan all elements in tree
        elements = [ self.root ] + self.root.findall(".//*")
        self.ids = { }
        for element in elements:
            if 'id' in element.attrib:
                self.ids[element.attrib['id']] = element
        # if any have no id at all, give them a new unique id
        unique = 0
        for element in elements:
            if not 'id' in element.attrib:
                id = 'uniq%d' % unique
                while id in self.ids:
                    unique += 1
                    id = 'uniq%d' % unique
                element.attrib['id'] = id
                self.ids[id] = element
        #print 'Surveyed %d elements.' % len(self.ids.keys())
        return len(list(self.ids.keys()))

    def read(self, filename):
        '''Requests the XML data be read from a file.'''
        self.filename = filename
        self.tree = etree.parse(filename)
        self.root = self.tree.getroot()
        return self.survey()
    