#!/usr/bin/python

from lxml import etree
#from PyQt4 import QtCore

#class SVG(QtCore.QObject):
class SVG():
    def __init__(self):
        #super(SVG, self).__init__()
        '''Prepares the virtual svg drawing container.'''
        self.filename = None
        self.tree = None
        self.root = None
        self.ids = { }

    def survey(self):
        '''Scan through the XML entities to ensure proper id attributes.
        Inkscape files write a unique id for each element, and gives a
        general "flipped Y" coordinate space inside a page of known size.
        Non-Inkscape SVG files may not comply with these optional niceties.
        We check that these features are available so Inkscape can render
        and resolve rendering locations for every entity later on.
        '''
        # ensure at least a default page size (arbitrarily, us letter)
        if 'width' not in self.root.attrib:
            self.root.attrib['width'] = '744.09448819'
        if 'height' not in self.root.attrib:
            self.root.attrib['height'] = '1052.3622047'
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
