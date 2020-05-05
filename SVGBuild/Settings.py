# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys, os

class Settings():
    
    inkscape = ''
    temporary = ''
    
    #def __init__(self):
    #    super(Settings, self).__init__("Zero SIX",  "svgbuild")
    
    def restoreSettings(self):
        if os.name == 'nt':
            # only for latest inkscape > 0.48
            # add inkscape and imagemagick installation folder to path
            #self.inkscape = self.value("inkscape", r'C:\Program Files\Inkscape\inkscape.com').toString()
            #self.temporary = self.value("temporary", r't:\TEMP\_svg').toString()
            self.inkscape = r'C:\Program Files\Inkscape\inkscape.com'
            self.temporary = r't:\TEMP\_svg'
#            self.identify = self.value("identify", r'identify.exe').toString()
#            self.convert = self.value("convert", r'convert.exe').toString()
            #self.lineColor = self.value("lineColor", r'black').toString()
            #self.backgroundColor = self.value("backgroundColor", r'white').toString()
            #self.foldername = self.value("foldername", r'moview').toString()
            #self.zoom = self.value("zoom", r'6').toString()
        else:
            #~ inkscape = r'"/Applications/Art Tools/Inkscape.app/Contents/Resources/bin/inkscape"'
            #self.inkscape = self.value("inkscape", r'/usr/bin/inkscape').toString()
            #self.temporary = self.value("temporary", r'/tmp/_svg').toString()
            self.inkscape = r'/usr/bin/inkscape'
            self.temporary = r'/tmp/_svg'
            #self.lineColor = self.value("lineColor", r'black').toString()
            #self.backgroundColor = self.value("backgroundColor", r'white').toString()
            #self.foldername = self.value("foldername", r'movie').toString()
            #self.zoom = self.value("zoom", r'6').toString()
        
        Settings.inkscape = self.inkscape
        Settings.temporary = self.temporary
        #Settings.lineColor = self.lineColor
        #Settings.backgroundColor = self.backgroundColor
        #Settings.foldername = self.foldername
        #Settings.zoom = self.zoom
            
    #def saveSettings(self):
    #    setValue("inkscape", self.inkscape)
    #    setValue("temporary", self.temporary)
        
