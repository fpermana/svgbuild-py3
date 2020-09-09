# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import time
import re

from .svg import SVG
from .camera import Camera
from .node import Node
from lxml import etree
import decimal

class SVGBuild():
    
    svg = None
    camera = None
    filename = ""
    options = {
            'no_background': False,
            'background_color': '#FFFFFF',

            'show_camera': False,
            'camera_frame' : '#FF0000',

            'build_path': False,
            'circle_path': False,
            'close_path': False,
            'fill_path': False,
            'full_path': False,
            'object_color': '#FFFFFF',
            'use_object_color': False,
            'line_color' : '#000000',
            'use_object_line_color': False,

            # 'combine': False,
            
            'dally': 4,
            'dolly': 50,
            'hold': 100,

            'add_marker': False,
            'marker_name': '',

            'folder': '',
            'name': '',
            'temp': 'temp.svg',

            'backward': False,
            'page_view': False,

            'continue': False,
            'restart': False,

            'build_image': False,
            'build_text': False,
            'bring_to_top': False,

            'from': 0,
            'until': 99999,

            'height': 480,
            'width': 640,

            'xx': False,
            'zoom': 6.,
            }
    def __init__(self, camera = None):
        if not camera:
            self.camera = Camera()
        else:
            self.camera = camera
        
    def setOptions(self, options):
        for arg in options:
            if arg == 'filename':
                self.filename = str(options[arg])

            else:
                self.options[arg] = options[arg]

        ok = False

        if not os.path.exists(self.filename):
            print('SVG files were not found.')
        elif self.options['width'] < 1 or self.options['height'] < 1:
            print('Invalid output pixel --height or --width specified.')
        elif self.options['zoom'] < 1:
            print('Zoom limiting value is invalid; must be positive.')
        else:
            if not os.path.isabs(self.filename):
                self.filename = os.path.abspath(self.filename)

            fileBaseName = os.path.splitext(os.path.basename(self.filename))

            if self.options['folder'] == '':
                self.options['folder'] = fileBaseName[0]
            else:
                self.options['folder'] = re.sub(r'\/+$', '', self.options['folder'])

            if self.options['name'] == '':
                self.options['name'] = fileBaseName[0]
            
            if self.options['page_view']:
                self.options['folder'] += '_page'
            if self.options['backward']:
                self.options['folder'] += '_backward'

            if not os.path.isabs(self.options['folder']):
                self.options['folder'] = os.path.dirname(self.filename) + '/' + self.options['folder']

            if os.path.exists(self.options['folder']):
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
                print(self.options)
            ok = True

        return ok

    def start(self):
        start = time.time()
        print('Starting buildup of %s...' % self.filename)

        if not os.path.exists(self.options['folder']):
            os.mkdir(self.options['folder'])
        if not os.path.exists(self.options['folder']):
            print('Cannot create folder %s...' % self.options['folder'])
            return False

        try:
            self.svg = SVG()
            elementCount = self.svg.read(self.filename)
            print('Surveyed %d elements.' % elementCount)

            if self.options['page_view']:
                self.options['width'] = self.svg.root.attrib['width']
                self.options['height'] = self.svg.root.attrib['height']

            if self.options['add_marker']:
                defs_element = self.svg.root.find('{http://www.w3.org/2000/svg}defs')
                if defs_element is not None:
                    markers = defs_element.findall('{http://www.w3.org/2000/svg}marker')

                    marker_name = ""
                    if len(markers) == 0:
                        marker_name = self.addMarker(defs_element, self.options['marker_name'])
                    else:
                        for marker in markers:
                            if 'id' in marker:
                                marker_name = '%s' % markers[0].attrib['id']
                                break

                    if marker_name == "":
                        self.options['add_marker'] = False
                    else:
                        self.options['marker_name'] = marker_name

            self.camera.setOptions(self.options)

            if self.camera.survey(self.svg):
                self.camera.move(self.svg.root.attrib['id'])
                self.build(self.svg, self.svg.root)
                
                if not self.options['page_view']:
                    location = self.camera.locate(self.svg.root.attrib['id'])
                    page_width = float(self.svg.root.attrib['width'])
                    page_height = float(self.svg.root.attrib['height'])
                    if location[0] < 0 or location[1] < 0 or location[2] > page_width or location[3] > page_height:
                        print('Panning...')
                        page = [0,0,page_width,page_height]
                        target = self.camera.zoom(self.camera.fit(self.camera.locate(page)))
                        self.camera.pan(self.svg, target)

                        if not self.options['no_background']:
                            rect1 = etree.SubElement(self.svg.root, '{http://www.w3.org/2000/svg}rect', id ='rect1001')
                            rect1.set('height', str(page_height+100))
                            rect1.set('width', str(page_width))
                            rect1.set('x', str(0-page_width))
                            rect1.set('y', '-50')
                            rect1.set('style', 'fill:%s;' % self.options['background_color'])

                            rect2 = etree.SubElement(self.svg.root, '{http://www.w3.org/2000/svg}rect', id ='rect1002')
                            rect2.set('height', str(page_height+100))
                            rect2.set('width', str(page_width))
                            rect2.set('x', str(page_width))
                            rect1.set('y', '-50')
                            rect2.set('style', 'fill:%s;' % self.options['background_color'])

                            rect3 = etree.SubElement(self.svg.root, '{http://www.w3.org/2000/svg}rect', id ='rect1003')
                            rect3.set('height', str(page_height))
                            rect3.set('width', str(page_width+100))
                            rect3.set('x', '-50')
                            rect3.set('y', str(0-page_height))
                            rect3.set('style', 'fill:%s;' % self.options['background_color'])

                            rect4 = etree.SubElement(self.svg.root, '{http://www.w3.org/2000/svg}rect', id ='rect1004')
                            rect4.set('height', str(page_height))
                            rect4.set('width', str(page_width+100))
                            rect3.set('x', '-50')
                            rect4.set('y', str(page_height))
                            rect4.set('style', 'fill:%s;' % self.options['background_color'])
                
                print('Finishing...')
                self.options['show_camera'] = False
                self.camera.shoot(self.svg)
                self.camera.hold(self.options['hold'])
                self.camera.cleanup()
            
            finish = time.time()
            hours = int((finish - start) / 60) / 60
            minutes = int((finish - start) / 60) % 60
            folder = self.options['folder']
            print('Finished %s to %s in %dh:%02dm.' % (self.filename, folder, hours, minutes))

        except Exception as e:
            print(e)
            return False

        return True

    def build(self, svg, entity):
        # Recursively build up the given entity, by removing all its children
        # and adding them back in one at a time, and shooting the progress with
        # the given camera.
        id = entity.attrib['id']
        name = id
        label = 'http://www.inkscape.org/namespaces/inkscape}label'
        if label in entity.attrib:
            name = entity.attrib[label]

        print('%05d - Building up <%s id="%s"> (%s)...' % (self.camera.time, entity.tag, id, name))

        nobuild = set([
            '{http://www.w3.org/2000/svg}defs',
            '{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview',
            '{http://www.w3.org/2000/svg}metadata',
            ])

        nochild = set([
            '{http://www.w3.org/2000/svg}text',
            ])

        backable = set([
            '{http://www.w3.org/2000/svg}svg',
            '{http://www.w3.org/2000/svg}g',
            ])

        ripped = [ ]
        for child in entity.iterchildren():
            if child.tag in nobuild: continue
            if not child.attrib['id'] in self.camera.layout: continue
            if 'style' in child.attrib:
                if 'display:none' in child.attrib['style']:
                    continue
            ripped.append(child)
        for child in ripped:
            entity.remove(child)

        backward = False

        # build from the bottom object
        if entity.tag in backable and self.options['backward']:
            backward = True

        if backward:
            print(' (Building children of entity %s backwards.)' % id)
            ripped.reverse()

        for child in ripped:
            print(' Adding child <%s id="%s">...' % (child.tag, child.attrib['id']))

            if self.options['page_view']:
                if self.options['show_camera']:
                    self.camera.pan(svg, child.attrib['id'], margin=1.2)

                self.camera.shoot(svg)
            else:
                self.camera.pan(svg, child.attrib['id'], margin=1.2)

            if child.getchildren() and not child.tag in nochild:
                if backward:
                    entity.insert(0, child)
                else:
                    entity.append(child)

                self.build(svg, child)
            else:
                if self.options['bring_to_top']:
                    svg.root.append(child)
                else:
                    if backward:
                        entity.insert(0, child)
                    else:
                        entity.append(child)

                if self.options['build_path'] and re.search(r"\}path$", child.tag):
                    self.build_path(svg, child)
                elif self.options['build_image'] and re.search(r"\}image$", child.tag):
                    self.build_image(svg, child)
                elif self.options['build_text'] and re.search(r"\}text$", child.tag):
                    self.build_text(svg, child)
                else:
                    self.camera.shoot(svg)

                if self.options['bring_to_top']:
                    svg.root.remove(child)
                    if backward:
                        entity.insert(0, child)
                    else:
                        entity.append(child)

            self.camera.shoot(svg)
            self.camera.hold(self.options['dally'] - 1)

        self.camera.pan(svg, id)
        
    def build_image(self, svg, entity):
        # Special progressive drawing of an image element.
        # The image will be included a few scanlines at a time until whole.
        
        href = '{http://www.w3.org/1999/xlink}href'
        if not href in entity.attrib: return
        img_url = urllib.parse.urlparse(entity.attrib[href])
        img = img_url.path
        if not os.path.exists(img):
            print(('Image file not found locally:', img))
            return

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
                self.camera.shoot(svg)
                os.unlink(tmp)
        # replace the original image reference
        entity.attrib[href] = img
        self.camera.shoot(svg)

    def convertToAbsolutePath(self, d):
        # convert relative path to absolute path
        nodes = []
        command = ""
        point = ""
        coordinateCount = 0
        showCommand = False
        
        points = d.strip().split(' ')

        node = None
        # convert from point to Node
        while points:
            
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
                    if ',' not in point and len(points) > 0 and command in 'aA' and (j == 0 or j==coordinateCount-1):
                        n = points.pop(0)
                        if ',' in n:
                            attrib.append(point)
                            attrib.append(n)
                        else:
                            attrib.append("%s,%s" % (point,n))
                    elif ',' not in point and len(points) > 0 and command in 'cClLmMqQsStT':
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

    def build_path(self, svg, entity):
        # Special progressive drawing of a path element.
        # The path will be included one bezier element at a time until whole.
        if not 'd' in entity.attrib: return
        id = entity.attrib['id']
        name = id
        print(('%05d - Building up <%s id="%s"> (%s)...' % (self.camera.time, entity.tag, id, name)))
        # replace style with our own style
        style = ''
        if 'style' in entity.attrib:
            style = entity.attrib['style']
        width = (self.camera.area[3]-self.camera.area[1]) / float(self.camera.height)
        if self.options['page_view']:
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
              
        if self.options['use_object_line_color']:
            if 'line' in style_dict:
                hl['stroke'] = style_dict['line']
            elif self.options['line_color']:
#                hl['stroke'] = '#000000'
                hl['stroke'] = self.options['line_color']
        elif self.options['line_color']:
            hl['stroke'] = self.options['line_color']

        if self.options['add_marker']:
#            hl.append('marker-end:url(#%s)' % self.marker)
            hl['marker-end'] = 'url(#%s)' % self.options['marker_name']
            #~ hl.append('marker-start:url(#Arrow1Lstart)')
            #~ hl[12] = 'marker-end:url(#SquareL)'
#        else:
#            hl.append('marker-end:none')
            #~ hl.append('marker-start:none')
            
        if self.options['fill_path']:
#            hl.append('marker-end:url(#%s)' % self.marker)
            hl['fill-opacity'] = '1'
            
        if self.options['use_object_color']:
            if 'fill' in style_dict:
                hl['fill'] = style_dict['fill']
            elif self.options['object_color']:
                hl['fill'] = self.options['object_color']
        elif self.options['object_color']:
            hl['fill'] = self.options['object_color']
        # hl = [
        # 'opacity:1', 'overflow:visible',
        # 'fill:none',
        # 'fill-opacity:0.',
        # 'fill-rule:nonzero',
        # 'stroke:%s' % self.options['line'],
        # 'stroke-width:%f' % width,
        # 'stroke-linecap:round', 'stroke-linejoin:round',
        # 'marker:none',
        # 'marker-start:none',
        # 'marker-mid:none',
        # # 'marker-end:none',
        # 'stroke-miterlimit:4', 'stroke-dasharray:none',
        # 'stroke-dashoffset:0', 'stroke-opacity:1',
        # 'visibility:visible', 'display:inline',
        # 'enable-background:accumulate' 
        # ]
        
        hairline = ';'.join("%s:%s" % (key,val) for (key,val) in list(hl.items()))
        # print hairline

        entity.attrib['style'] = hairline

        # scan the control points
        # points = entity.attrib['d'].split(' ')
        # print entity.attrib['d']
        ori_d = entity.attrib['d']

        # case for 10e-6, 2.52e-4, etc
        d = ori_d
        if 'e' in ori_d or 'E' in ori_d:
            matches = re.findall(r'[0-9\.-]*[eE][0-9-]*', d)
            for match in matches:
                dec = str(decimal.Decimal(match))
                d = d.replace(match, dec)

        d = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1 \2', d)
        d = re.sub(r'([a-zA-Z])([0-9-])', r'\1 \2', d)
        d = re.sub(r'([0-9])([a-zA-Z])', r'\1 \2', d)
        # print(d)

        if self.options['circle_path']:
            d = self.convertToAbsolutePath(d)

        paths = d.replace('z', 'z#').replace('Z', 'Z#').split('#')
        if self.options['backward']:
            paths.reverse()

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
                if not self.options['full_path']:
                    while nodes:
                        node = nodes.pop(0)
                        built.append(node.getValue())
                elif self.options['circle_path']:
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

                if self.options['close_path'] and not (d.endswith('z') or d.endswith('Z')):
                    d = d + ' z'
                entity.attrib['d'] = d
                self.camera.shoot(svg)
                
        # put the original d and style back
        entity.attrib['d'] = ori_d
        entity.attrib['style'] = style
        self.camera.shoot(svg)

    def build_text(self, svg, entity):
        # Special progressive drawing of a text or tspan contents.
        # The text will appear one letter at a time until whole.
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
                build_text(svg, child)
        # come back to build our own direct text
        if not text: return
        for l in range(1, len(text)):
            entity.text = text[:l]
            self.camera.shoot(svg)
        entity.text = text
        self.camera.shoot(svg)
        
    def addMarker(self,  element, name='diamond'):
        marker = ""
        if name == 'diamond':
            marker_element = etree.SubElement(element, 'marker', id = 'diamond')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'EmptyDiamondL')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            # marker_element.set('markerWidth','1')
            # marker_element.set('markerHeight','1')
            marker_element.set('id', name)

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='mark0001')
            marker_path.set('d', "M 0,-7.0710768 L -7.0710894,0 L 0,7.0710589 L 7.0710462,0 L 0,-7.0710768 z ")
            marker_path.set('style', "fill-rule:evenodd;fill:#FFFFFF;stroke:#000000;stroke-width:1.0pt")
            marker_path.set('transform', "scale(0.8)")

            marker = '%s' % marker_element.attrib['id']
        
        elif name == 'scissor':
            marker_element = etree.SubElement(element, 'marker', id = 'Scissors')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'Scissors')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            marker_element.set('id', name)

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='schere')
            marker_path.set('d', "M 9.0898857,-3.6061018 C 8.1198849,-4.7769976 6.3697607,-4.7358294 5.0623558,-4.2327734 L -3.1500488,-1.1548705 C -5.5383421,-2.4615840 -7.8983361,-2.0874077 -7.8983361,-2.7236578 C -7.8983361,-3.2209742 -7.4416699,-3.1119800 -7.5100293,-4.4068519 C -7.5756648,-5.6501286 -8.8736064,-6.5699315 -10.100428,-6.4884954 C -11.327699,-6.4958500 -12.599867,-5.5553341 -12.610769,-4.2584343 C -12.702194,-2.9520479 -11.603560,-1.7387447 -10.304005,-1.6532027 C -8.7816644,-1.4265411 -6.0857470,-2.3487593 -4.8210600,-0.082342643 C -5.7633447,1.6559151 -7.4350844,1.6607341 -8.9465707,1.5737277 C -10.201445,1.5014928 -11.708664,1.8611256 -12.307219,3.0945882 C -12.885586,4.2766744 -12.318421,5.9591904 -10.990470,6.3210002 C -9.6502788,6.8128279 -7.8098011,6.1912892 -7.4910978,4.6502760 C -7.2454393,3.4624530 -8.0864637,2.9043186 -7.7636052,2.4731223 C -7.5199917,2.1477623 -5.9728246,2.3362771 -3.2164999,1.0982979 L 5.6763468,4.2330688 C 6.8000164,4.5467672 8.1730685,4.5362646 9.1684433,3.4313614 L -0.051640930,-0.053722219 L 9.0898857,-3.6061018 z M -9.2179159,-5.5066058 C -7.9233569,-4.7838060 -8.0290767,-2.8230356 -9.3743431,-2.4433169 C -10.590861,-2.0196559 -12.145370,-3.2022863 -11.757521,-4.5207817 C -11.530373,-5.6026336 -10.104134,-6.0014137 -9.2179159,-5.5066058 z M -9.1616516,2.5107591 C -7.8108215,3.0096239 -8.0402087,5.2951947 -9.4138723,5.6023681 C -10.324932,5.9187072 -11.627422,5.4635705 -11.719569,4.3902287 C -11.897178,3.0851737 -10.363484,1.9060805 -9.1616516,2.5107591 z ")
            marker_path.set('style', "fill:#000000;")
            #marker_path.set('transform', "scale(0.8)")

            marker = '%s' % marker_element.attrib['id']
            
        elif name == 'triangle':
            marker_element = etree.SubElement(element, 'marker', id = 'EmptyTriangleOutL')
            marker_element.set('{http://www.inkscape.org/namespaces/inkscape}stockid', 'EmptyTriangleOutL')
            marker_element.set('refY', '0.0')
            marker_element.set('style', 'overflow:visible')
            marker_element.set('refX', '0.0')
            marker_element.set('orient', 'auto')
            marker_element.set('id', name)

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}path', id ='mark0002')
            marker_path.set('d', "M 5.77,0.0 L -2.88,5.0 L -2.88,-5.0 L 5.77,0.0 z ")
            marker_path.set('style', "fill-rule:evenodd;fill:#FFFFFF;stroke:#000000;stroke-width:1.0pt")
            marker_path.set('transform', "scale(0.8) translate(-6,0)")

            marker = '%s' % marker_element.attrib['id']

        elif name == 'dot':
            marker_element = etree.SubElement(element, 'marker', id = 'dot')
            marker_element.set('viewBox', '0 0 10 10')
            marker_element.set('refY', '5.0')
            marker_element.set('refX', '5.0')
            marker_element.set('markerWidth', '5')
            marker_element.set('markerHeight', '5')
            marker_element.set('id', name)

            marker_path = etree.SubElement(marker_element, '{http://www.w3.org/2000/svg}circle', id ='mark0002')
            marker_path.set('cx', '5')
            marker_path.set('cy', '5')
            marker_path.set('r', '5')
            marker_path.set('fill', 'red')

            marker = '%s' % marker_element.attrib['id']
        else:
            marker = ''

        return marker
            
