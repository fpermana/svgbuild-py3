# -*- coding: utf-8 -*-
#!/usr/bin/env python3

class Node():
    command = ""
    attrib = []
    showCommand = False
        
    def getValue(self):
        value = ""
        if self.showCommand:
            value = '%s %s' % (self.command,  ' '.join(self.attrib))
        else:
            value = ' '.join(self.attrib)
            
        return value
        
    def getTarget(self):
        if Node.getCharacterCount(self.command) > 1:
            return self.attrib[-2:]
        return []
    
#    def getCharacterCount(self):
#        return getCharacterCount(command)
        
    @staticmethod
    def getCharacterCount(command):
        characterCount = 0
        if command == "m" or command == "M":
            characterCount = 2
        elif command == "z" or command == "Z":
            characterCount = 0
        elif command == "l" or command == "L":
            characterCount = 2
        elif command == "h" or command == "H":
            characterCount = 1
        elif command == "v" or command == "V":
            characterCount = 1
        elif command == "c" or command == "C":
            characterCount = 6
        elif command == "s" or command == "S":
            characterCount = 4
        elif command == "q" or command == "Q":
            characterCount = 4
        elif command == "t" or command == "T":
            characterCount = 2
        elif command == "a" or command == "A":
            characterCount = 7
        else:
            characterCount = 1
            
        return characterCount

    @staticmethod
    def getCoordinateCount(command):
        '''http://www.w3.org/TR/SVG11/paths.html'''
        coordinateCount = 0
        if command == "m" or command == "M":
            coordinateCount = 1
        elif command == "z" or command == "Z":
            coordinateCount = 0
        elif command == "l" or command == "L":
            coordinateCount = 1
        elif command == "h" or command == "H":
            coordinateCount = 1
        elif command == "v" or command == "V":
            coordinateCount = 1
        elif command == "c" or command == "C":
            coordinateCount = 3
        elif command == "s" or command == "S":
            coordinateCount = 2
        elif command == "q" or command == "Q":
            coordinateCount = 2
        elif command == "t" or command == "T":
            coordinateCount = 1
        elif command == "a" or command == "A":
            coordinateCount = 4
            
        return coordinateCount
