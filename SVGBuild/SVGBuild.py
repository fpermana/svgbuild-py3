# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import time
import re
import urllib.parse

from .interpolations import *
from .vectors import *

from .SVG import SVG
from .Camera import Camera
from .Node import Node
from lxml import etree
from PIL import Image

class SVGBuild():    
    
    svg = SVG()
    options = { 'folder': 'movie',
            'name': 'movie',
            'temp': 'temp.svg',
            'from': 0,
            'until': 99999,
            'image': False,
            'path': False,
            'fullpath': False,
            'fillpath': False,
            'closepath': False,
            'top': False,
            'page': False,
            'combine': False,
            'color': '',
            'camera': False,
            # 'line' : '#000000',
            'line' : '',
            'frame' : '#FF0000',
            'text': False,
            'backward': False,
            'width': 640,
            'height': 480,
            'dally': 4,
            'dolly': 50,
            'hold': 100,
            'background': '#FFFFFF',
            'nobackground': False,
            'objectline': False,
            'objectcolor': False,
            'continue': False,
            'restart': False,
            'zoom': 6.,
            'xx': False
            }
            
    isRunning = False
    
    def __init__(self):
        super(SVGBuild, self).__init__()
        #self.camera = Camera(self.options)
        
    def setFilename(self, filename):
        self.filename = filename
        
    def setIsRunning(self,  isRunning):
        self.isRunning = isRunning
        
        if not isRunning:
            self.camera.setIsRunning(isRunning)
        
    def getOptions(self):
        return self.options
        
    def setSingleOption(self, key,  value):
        self.options[key] = value
        
    def getSingleOption(self, key):
        return self.options[key]
        
    def getPathOption(self):
        return self.getSingleOption('path')
        
    def getCameraOption(self):
        return self.getSingleOption('camera')
        
    def getPageOption(self):
        return self.getSingleOption('page')
    
    def startBuildUp(self):
        if self.options['width'] < 1 or self.options['height'] < 1:
            print('Invalid output pixel --height or --width specified.')
        if zero(self.options['zoom']) or self.options['zoom'] < 0:
            print('Zoom limiting value is invalid; must be positive.')
        if self.options['xx']:
            self.options['from'] = self.options['until'] = -1
        if self.options['fullpath']:
            self.options['path'] = True

        # overall preparations
        overall = time.time()

        folder_name = [ self.options['folder'], self.options['name'] ]
        
        if not os.path.exists(self.filename):
            print('SVG files were not found.')
        else:
            fileBaseName = os.path.splitext(os.path.basename(self.filename))

            if folder_name[0] == 'movie':
                self.options['folder'] = fileBaseName[0]
            self.options['name'] = fileBaseName[0]
            
            if self.options['page']:
                self.options['folder'] += '_page'
            if self.options['backward']:
                self.options['folder'] += '_backward'

            self.options['folder'] = os.path.dirname(self.filename) + '/' + self.options['folder']

            if not os.path.exists(self.options['folder']):
                os.mkdir(self.options['folder'])
            else:
                files = os.listdir(self.options['folder'])
                if self.options['continue']:
                    current = 0
                    for file in files:
                        if file.endswith('.png'):
                            number = re.sub(r'\.png$','',file)[-5:].lstrip('0')
                            if not number:
                                number = '0'

                            number = int(number)
                            if number > current:
                                current = number
                    self.options['from'] = 0 if (current < 3) else (current - 2)

                elif self.options['restart']:
                    for file in files:
                        if file.endswith('.png'):
                            os.remove(self.options['folder'] + '/' + file)
                    self.options['from'] = 0
                
            start = time.time()
            print('Starting buildup of %s...' % self.filename)
            
            try:
                self.svg = SVG()
                elementCount = self.svg.read(str(self.filename))

                if self.options['page']:
                    self.options['width'] = self.svg.root.attrib['width']
                    self.options['height'] = self.svg.root.attrib['height']

            except Exception as e:
                print('error')
                self.finished.emit()
                return
            
            if self.options['marker']:
                defs_element = self.svg.root.find('{http://www.w3.org/2000/svg}defs')
                if defs_element is not None:
                    markers = defs_element.findall('{http://www.w3.org/2000/svg}marker')
                
                    if len(markers) == 0:
                        self.addMarker(defs_element, self.options['marker'])
                    else:
                       self.marker = '%s' % markers[0].attrib['id']

            print('Surveyed %d elements.' % elementCount)
            
            self.camera = Camera(self.options)
            self.camera.printText.connect(self.printText)
#            self.finished.emit()
#            return 0
            
            if self.camera.survey(self.svg):
                #print('ok')
                self.camera.move(self.svg.root.attrib['id'])
                self.build(self.svg, self.camera, self.svg.root, self.options)
                
                if self.isRunning:
                    print('Finishing...')
                    self.options['camera'] = False
                    self.camera.shoot(self.svg)
                    self.camera.hold(self.options['hold'])
                    self.camera.cleanup()
                else:
                    print('Canceled...')
            
            finish = time.time()
            hours = int((finish - start) / 60) / 60
            minutes = int((finish - start) / 60) % 60
            folder = self.options['folder']
            print('Finished %s to %s in %dh:%02dm.' % (self.filename, folder, hours, minutes))
            
        self.finished.emit()
        
    def build(self, svg, camera, entity, options):
        '''Recursively build up the given entity, by removing all its children
        and adding them back in one at a time, and shooting the progress with
        the given camera.
        '''
        
        if not self.isRunning: return

        id = entity.attrib['id']
        name = id
        label = 'http://www.inkscape.org/namespaces/inkscape}label'
        if label in entity.attrib:
            name = entity.attrib[label]
        print('%05d - Building up <%s id="%s"> (%s)...' % (camera.time, entity.tag, id, name))

        nobuild = set([ '{http://www.w3.org/2000/svg}defs',
                        '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview',
                        '{http://www.w3.org/2000/svg}metadata',
                        ])

        nochild = set([ '{http://www.w3.org/2000/svg}text',
                        ])

        backable = set([ '{http://www.w3.org/2000/svg}svg',
                         '{http://www.w3.org/2000/svg}g',
                        ])

        ripped = [ ]
        for child in entity.iterchildren():
            if child.tag in nobuild: continue
            if not child.attrib['id'] in camera.layout: continue
            if 'style' in child.attrib:
                if 'display:none' in child.attrib['style']:
                    continue
            ripped.append(child)
        for child in ripped:
            entity.remove(child)

        backward = False    
        
        '''build from the lowest object'''
        if entity.tag in backable and self.options['backward']:
            backward = True
        
        '''build from the top object'''
        if backward:
            print(' (Building children of entity %s backwards.)' % id)
            #print ' (Building children of entity %s backwards.)' % id
            ripped.reverse()

        for child in ripped:
            if not self.isRunning: return
            print(' Adding child <%s id="%s">...' % (child.tag, child.attrib['id']))
            #print ' Adding child <%s id="%s">...' % (child.tag, child.attrib['id'])
            
            if self.options['page']:
                if self.options['camera']:
                    camera.pan(svg, child.attrib['id'], margin=1.2)

                camera.shoot(svg)
            else:
                camera.pan(svg, child.attrib['id'], margin=1.2)

            if child.getchildren() and not child.tag in nochild:
                if backward:
                    entity.insert(0, child)
                else:
                    entity.append(child)

                self.build(svg, camera, child, options)
            else:
                if self.options['top']:
                    svg.root.append(child)
                else:
                    if backward:
                        entity.insert(0, child)
                    else:
                        entity.append(child)

                if self.options['path'] and re.search(r"\}path$", child.tag):
                    self.build_path(svg, camera, child, options)
                elif self.options['image'] and re.search(r"\}image$", child.tag):
                    self.build_image(svg, camera, child, options)
                elif self.options['text'] and re.search(r"\}text$", child.tag):
                    self.build_text(svg, camera, child, options)
                else:
                    camera.shoot(svg)

                if self.options['top']:
                    svg.root.remove(child)
                    if backward:
                        entity.insert(0, child)
                    else:
                        entity.append(child)

            camera.shoot(svg)
            camera.hold(self.options['dally'] - 1)

        camera.pan(svg, id)
        
    def build_image(self, svg, camera, entity, options):
        '''Special progressive drawing of an image element.
        The image will be included a few scanlines at a time until whole.'''
        
        if not self.isRunning: return
        
        href = '{http://www.w3.org/1999/xlink}href'
        if not href in entity.attrib: return
        img_url = urllib.parse.urlparse(entity.attrib[href])
        img = img_url.path
        if not os.path.exists(img):
            print(('Image file not found locally:', img))
            return
        # figure out original image's pixel size
        '''results = Utils.qx('%s %s' % (str(Settings.identify), img))
        m = re.search(r'(\d+)x(\d+)', results)
        if not m:
            print 'ImageMagick could not identify size of image; skipping.'
            return'''
        try:
            output_image = Image.open(img)
        except IOError as e:
            print(("error opening file :: %s" % img))
        size = output_image.size
        # for a handful of frames, replace image with a truncated temporary image
        tmp = self.options['folder'] + '/temp.png'
        frames = int(self.options['dally']) * 4
        for frame in range(frames):
            height = interpolations.linear(0, frames, frame, 1, size[1])
            box = (0, 0, size[0], height)
            area = output_image.crop(box)
            background = Image.new("RGBA", size)
            background.paste(area,box)
            background.save(tmp, 'PNG')
            
            if os.path.exists(tmp):
                entity.attrib[href] = tmp
                camera.shoot(svg)
                os.unlink(tmp)
        # replace the original image reference
        entity.attrib[href] = img
        camera.shoot(svg)

    def convertToAbsolutePath(self, d):
        '''convert relative path to absolute path'''
        nodes = []
        command = ""
        point = ""
        coordinateCount = 0
        showCommand = False
        
        points = d.strip().split(' ')

        node = None
        # convert from point to Node
        while points:
            if not self.isRunning: return
            
            point = points[0]
            
            node = Node()
            attrib = []
            if re.match(r'^[a-zA-Z]$', point):
                command = point
                showCommand = True
                coordinateCount = Node.getCoordinateCount(command)
                points.pop(0)
            elif command == "M" or command == "m":
                showCommand = False
        
            for j in range(0, coordinateCount):
                if len(points) > 0:
                    point = points.pop(0)
                    if ',' not in point and len(points) > 0 and command in 'cClLmMqQsStT':
                        attrib.append("%s,%s" % (point,points.pop(0)))
                    else:
                        attrib.append(point)


            node.command = command
            node.attrib = attrib
            node.showCommand = showCommand
            
            nodes.append(node)

        x = None
        y = None
        for node in nodes:
            if len(node.attrib) > 0:
                coordinate = node.attrib[-1]
                xy = coordinate.split(",")
                if x is None and y is None:
                    x = float(xy[0])
                    y = float(xy[1])
                elif node.command == "h":
                    x += float(xy[0])
                    node.attrib[-1] = str(x)
                elif node.command == "v":
                    y += float(xy[0])
                    node.attrib[-1] = str(y)
                elif node.command == "H":
                    x = float(xy[0])
                elif node.command == "V":
                    y = float(xy[0])
                elif node.command.islower():
                    for i in range(len(node.attrib)):
                        coordinate = node.attrib[i]
                        xy = coordinate.split(",")
                        if len(xy) == 2:
                            xy[0] = str(float(xy[0]) + x)
                            xy[1] = str(float(xy[1]) + y)
                            node.attrib[i] = ','.join(xy)
                            if i == (len(node.attrib)-1):
                                x = float(xy[0])
                                y = float(xy[1])
                elif node.command.isupper():
                    x = float(xy[0])
                    y = float(xy[1])

            node.command = node.command.upper()

        points = []
        for node in nodes:
            points.append(node.getValue())

        d = ' '.join(points).strip()

        return d

    def build_path(self, svg, camera, entity, options):
        '''Special progressive drawing of a path element.
        The path will be included one bezier element at a time until whole.'''
        if not 'd' in entity.attrib: return
        id = entity.attrib['id']
        name = id
        print(('%05d - Building up <%s id="%s"> (%s)...' % (camera.time, entity.tag, id, name)))
        # replace style with our own style
        style = ''
        if 'style' in entity.attrib:
            style = entity.attrib['style']
        width = (camera.area[3]-camera.area[1]) / float(camera.height)
        if self.options['page']:
            page_width = float(svg.root.attrib['width'])
            page_height = float(svg.root.attrib['height'])
            if page_width > page_height:
                width = page_width / page_height
            else:
                width = page_height / page_width
        
        style_dict = {}
        style_list = style.split(';')
        for s in style_list:
            w = s.split(':')
            if len(w) > 1:
                style_dict[w[0]] = w[1]
        
#        print ';'.join("%s:%r" % (key,val) for (key,val) in style_dict.iteritems())
        
        hl = {
              'opacity': '1', 
              'overflow': 'visible', 
              'fill-opacity': '0',
              'fill-rule': 'nonzero',
              'stroke-linecap': 'round',
              'stroke-linejoin': 'round',
              'marker': 'none',
              'marker-start': 'none',
              'marker-mid': 'none',
              'marker-end': 'none',
              'stroke-miterlimit': '4',
              'stroke-dasharray': 'none',
              'stroke-dashoffset': '0',
              'stroke-opacity': '1',
              'visibility': 'visible',
              'display': 'inline',
              'enable-background': 'accumulate', 
              'stroke-width': '%f' % width
              }
              
        if self.options['objectline']:
            if 'line' in style_dict:
                hl['stroke'] = style_dict['line']
            elif self.options['line']:
#                hl['stroke'] = '#000000'
                hl['stroke'] = self.options['line']
        elif self.options['line']:
            hl['stroke'] = self.options['line']

        if self.options['marker']:
#            hl.append('marker-end:url(#%s)' % self.marker)
            hl['marker-end'] = 'url(#%s)' % self.marker
            #~ hl.append('marker-start:url(#Arrow1Lstart)')
            #~ hl[12] = 'marker-end:url(#SquareL)'
#        else:
#            hl.append('marker-end:none')
            #~ hl.append('marker-start:none')
            
        if self.options['fillpath']:
#            hl.append('marker-end:url(#%s)' % self.marker)
            hl['fill-opacity'] = '1'
            
        if self.options['objectcolor']:
            if 'fill' in style_dict:
                hl['fill'] = style_dict['fill']
            elif self.options['color']:
                hl['fill'] = self.options['color']
        elif self.options['color']:
            hl['fill'] = self.options['color']
        '''hl = [
        'opacity:1', 'overflow:visible',
        'fill:none',
        'fill-opacity:0.',
        'fill-rule:nonzero',
        'stroke:%s' % self.options['line'],
        'stroke-width:%f' % width,
        'stroke-linecap:round', 'stroke-linejoin:round',
        'marker:none',
        'marker-start:none',
        'marker-mid:none',
        #~ 'marker-end:none',
        'stroke-miterlimit:4', 'stroke-dasharray:none',
        'stroke-dashoffset:0', 'stroke-opacity:1',
        'visibility:visible', 'display:inline',
        'enable-background:accumulate' 
        ]'''
        
        
#        hairline = ';'.join(hl)
        hairline = ';'.join("%s:%s" % (key,val) for (key,val) in list(hl.items()))
        # print hairline

        entity.attrib['style'] = hairline

        # scan the control points
        # points = entity.attrib['d'].split(' ')
        # print entity.attrib['d']
        ori_d = entity.attrib['d']
        # print ori_d
        # TODO: case for 10e-6, 2.52e-4, etc
        # es = re.findall(r'[0-9-]*e[0-9-]*', ori_d)
        # es = list(dict.fromkeys(es))
        # es = list(set(es))
        # for e in es:
            # nums = e.split('e')
            # print nums, (float(nums[0]) * (10 ^ ))
            # format(math.pow(float(nums[0]),int(nums[1])), "10.2f")
            # 2.52 * 10 ^ -4
        # d = re.sub(r'([lLmM])([0-9-]*) ([0-9-]*)', r'\1 \2,\3', entity.attrib['d'])
        d = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1 \2', ori_d)
        d = re.sub(r'([a-zA-Z])([0-9-])', r'\1 \2', d)
        d = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', d)
        # print d

        if self.options['circlepath']:
            d = self.convertToAbsolutePath(d)

        paths = d.replace('z', 'z#').replace('Z', 'Z#').split('#')
        for pathIndex, path in enumerate(paths):
            if len(path) == 0:
                continue

            nodes = []
            command = ""
            point = ""
            coordinateCount = 0
            showCommand = False
            
            points = path.strip().split(' ')
            pointsCount = len(points)

            node = None
            # convert from point to Node
            while points:
                if not self.isRunning: return
                
                point = points[0]
                
                node = Node()
                attrib = []
                if re.match(r'^[a-zA-Z]$', point):
                    command = point
                    showCommand = True
                    coordinateCount = Node.getCoordinateCount(command)
                    points.pop(0)
                elif command == "M" or command == "m":
                    showCommand = False
            
                for j in range(0, coordinateCount):
                    if len(points) > 0:
                        point = points.pop(0)
                        if ',' not in point and len(points) > 0 and command in 'cClLmMqQsStT':
                            attrib.append("%s,%s" % (point,points.pop(0)))
                        else:
                            attrib.append(point)


                node.command = command
                node.attrib = attrib
                node.showCommand = showCommand
                
                nodes.append(node)

            leftPath = []
            rightPath = []
            built = []

            while nodes:
                if not self.isRunning: return

                if not self.options['fullpath']:
                    while nodes:
                        node = nodes.pop(0)
                        built.append(node.getValue())
                elif self.options['circlepath']:
                    if len(nodes) > 0:
                        node = nodes.pop(0)
                        leftPath.append(node)
                    if len(nodes) > 0:
                        node = nodes.pop()
                        rightPath.insert(0, node)

                    built = []
                    for node in leftPath:
                        built.append(node.getValue())
                    for node in rightPath:
                        built.append(node.getValue())
                else:
                    node = nodes.pop(0)
                    built.append(node.getValue())

                if self.camera.time < self.options['from'] or self.camera.time > self.options['until']:
                    self.camera.time += 1
                    continue

                d = ' '.join(built).strip()

                # for p in range(pathIndex-1,-1,-1):
                    # d = paths[p] + ' ' + d
                previousPaths = paths[0:pathIndex]
                d = ' '.join(previousPaths).strip() + ' ' + d

                if self.options['closepath'] and not (d.endswith('z') or d.endswith('Z')):
                    d = d + ' z'
                entity.attrib['d'] = d
                camera.shoot(svg)
                
        # put the original d and style back
        entity.attrib['d'] = ori_d
        entity.attrib['style'] = style
        camera.shoot(svg)

    def build_text(self, svg, camera, entity, options):
        '''Special progressive drawing of a text or tspan contents.
        The text will appear one letter at a time until whole.'''
        text = entity.text
        entity.text = ''
        # if we have children, recurse to build their .text now
        if entity.getchildren():
            children = [ ]
            for child in entity.iterchildren():
                if child.text:
                    children.append(child)
            for child in children:
                entity.remove(child)
            for child in children:
                entity.append(child)
                build_text(svg, camera, child, options)
        # come back to build our own direct text
        if not text: return
        for l in range(1, len(text)):
            if not self.isRunning: return
            entity.text = text[:l]
            camera.shoot(svg)
        entity.text = text
        camera.shoot(svg)
        
    def addMarker(self,  element, name='diamond'):
        if name == 'diamond':
            marker_element = etree.SubElement(element, 'marker', id = 'EmptyDiamondL')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'EmptyDiamondL')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            # marker_element.set('markerWidth','1')
            # marker_element.set('markerHeight','1')
            marker_element.set('id', 'EmptyDiamondL')

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='mark0001')
            marker_path.set('d', "M 0,-7.0710768 L -7.0710894,0 L 0,7.0710589 L 7.0710462,0 L 0,-7.0710768 z ")
            marker_path.set('style', "fill-rule:evenodd;fill:#FFFFFF;stroke:#000000;stroke-width:1.0pt")
            marker_path.set('transform', "scale(0.8)")

            self.marker = '%s' % marker_element.attrib['id']
        
        elif name == 'scissor':
            marker_element = etree.SubElement(element, 'marker', id = 'Scissors')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'Scissors')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            marker_element.set('id', 'Scissors')

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='schere')
            marker_path.set('d', "M 9.0898857,-3.6061018 C 8.1198849,-4.7769976 6.3697607,-4.7358294 5.0623558,-4.2327734 L -3.1500488,-1.1548705 C -5.5383421,-2.4615840 -7.8983361,-2.0874077 -7.8983361,-2.7236578 C -7.8983361,-3.2209742 -7.4416699,-3.1119800 -7.5100293,-4.4068519 C -7.5756648,-5.6501286 -8.8736064,-6.5699315 -10.100428,-6.4884954 C -11.327699,-6.4958500 -12.599867,-5.5553341 -12.610769,-4.2584343 C -12.702194,-2.9520479 -11.603560,-1.7387447 -10.304005,-1.6532027 C -8.7816644,-1.4265411 -6.0857470,-2.3487593 -4.8210600,-0.082342643 C -5.7633447,1.6559151 -7.4350844,1.6607341 -8.9465707,1.5737277 C -10.201445,1.5014928 -11.708664,1.8611256 -12.307219,3.0945882 C -12.885586,4.2766744 -12.318421,5.9591904 -10.990470,6.3210002 C -9.6502788,6.8128279 -7.8098011,6.1912892 -7.4910978,4.6502760 C -7.2454393,3.4624530 -8.0864637,2.9043186 -7.7636052,2.4731223 C -7.5199917,2.1477623 -5.9728246,2.3362771 -3.2164999,1.0982979 L 5.6763468,4.2330688 C 6.8000164,4.5467672 8.1730685,4.5362646 9.1684433,3.4313614 L -0.051640930,-0.053722219 L 9.0898857,-3.6061018 z M -9.2179159,-5.5066058 C -7.9233569,-4.7838060 -8.0290767,-2.8230356 -9.3743431,-2.4433169 C -10.590861,-2.0196559 -12.145370,-3.2022863 -11.757521,-4.5207817 C -11.530373,-5.6026336 -10.104134,-6.0014137 -9.2179159,-5.5066058 z M -9.1616516,2.5107591 C -7.8108215,3.0096239 -8.0402087,5.2951947 -9.4138723,5.6023681 C -10.324932,5.9187072 -11.627422,5.4635705 -11.719569,4.3902287 C -11.897178,3.0851737 -10.363484,1.9060805 -9.1616516,2.5107591 z ")
            marker_path.set('style', "fill:#000000;")
            #marker_path.set('transform', "scale(0.8)")

            self.marker = '%s' % marker_element.attrib['id']
            
        elif name == 'triangle':
            marker_element = etree.SubElement(element, 'marker', id = 'EmptyTriangleOutL')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'EmptyTriangleOutL')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            marker_element.set('id', 'EmptyTriangleOutL')

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='mark0002')
            marker_path.set('d', "M 5.77,0.0 L -2.88,5.0 L -2.88,-5.0 L 5.77,0.0 z ")
            marker_path.set('style', "fill-rule:evenodd;fill:#FFFFFF;stroke:#000000;stroke-width:1.0pt")
            marker_path.set('transform', "scale(0.8) translate(-6,0)")

            self.marker = '%s' % marker_element.attrib['id']

        elif name == 'dot':
            marker_element = etree.SubElement(element, 'marker', id = 'dot')
            marker_element.set('viewBox', '0 0 10 10')
            marker_element.set('refY', '5.0')
            marker_element.set('refX', '5.0')
            marker_element.set('markerWidth', '5')
            marker_element.set('markerHeight', '5')
            marker_element.set('id', 'dot')


            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}circle', id ='mark0002')
            marker_path.set('cx', '5')
            marker_path.set('cy', '5')
            marker_path.set('r', '5')
            marker_path.set('fill', 'red')

            self.marker = '%s' % marker_element.attrib['id']
        else:
            self.marker = 'none'
            
