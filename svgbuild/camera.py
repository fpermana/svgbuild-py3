# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from lxml import etree
from .inkscape import Inkscape
from .utils import *
from .interpolations import *
from .vectors import *
import time
import os, sys
import shutil
import re
import math
# from PIL import Image, ImageDraw, ImageColor

class Camera():
    options = {}
    layout = {}

    locked = False
    time = 0
    area = [ 0., 0., 1., 1. ]
    temp = ''

    width = 0.
    height = 0.

    def __init__(self):
        self.options = {}
        self.layout = {}

        self.locked = False
        self.time = 0
        self.area = [ 0., 0., 1., 1. ]
        self.temp = ''

        self.width = 0.
        self.height = 0.

    def setOptions(self, options):
        # Construct a virtual camera.
        self.locked = False
        self.time = 0
        self.area = [ 0., 0., 1., 1. ]
        self.temp = options['folder'] + '/' + options['temp']
        
        w = options['width']
        # uw = re.search(r'[a-zA-Z]*$',str(w))
        # if uw:
        #     w = re.sub(r'[a-zA-Z]', '', str(w))
        #     w = self.convertToPixel(uw.group(), float(w))

        h = options['height']
        # uh = re.search(r'[a-zA-Z]*$',str(h))
        # if uh:
        #     h = re.sub(r'[a-zA-Z]', '', str(h))
        #     h = self.convertToPixel(uh.group(), float(h))
        
        self.width = float(w)
        self.height = float(h)
        self.options = options
        
    # def convertToPixel(self, unit, value):
    #     if unit == "mm":
    #         return value * 3.7795275591
    #     elif unit == "cm":
    #         return value * 10 * 3.7795275591
    #     elif unit == "in":
    #         return value * 96
    #     elif unit == "pt":
    #         return value / 3 * 4
    #     return value
        
    def _write(self, svg):
        # Save a scratch prepared copy of the xml to be used by Inkscape
        svg_string = etree.tostring(svg.root, pretty_print=True)

        file = open(self.temp, 'w')
        sys_info = sys.version_info
        if sys_info.major == 3:
            svg_string = svg_string.decode('utf-8')

        file.write(svg_string)
        file.close()

#        file = open('%d.svg' % (self.time), 'w')
#        file.write(etree.tostring(svg.root, pretty_print=True))
#        file.close()

    def survey(self, svg):
        # Learn the locations of all elements.
        if self.layout: return
        self._write(svg)

        # ask Inkscape for a survey of all ids
        cmd = Inkscape.cmd[:]
        cmd.extend([
            '--query-all',
            self.temp
            ])
        # print(cmd)
        result = qx(cmd)

        sys_info = sys.version_info
        if sys_info.major == 3:
            result = result.decode('utf-8')
        # print result
        result = result.split('\n')
        layout = self.layout
        w = svg.root.attrib['width']
        # uw = re.search(r'[a-zA-Z]*$',w)
        # if uw:
        #     w = re.sub(r'[a-zA-Z]', '', str(w))
        #     w = self.convertToPixel(uw.group(), float(w))
        #     svg.root.attrib['width'] = str(w)
        
        h = svg.root.attrib['height']
        # uh = re.search(r'[a-zA-Z]*$',h)
        # if uh:
        #     h = re.sub(r'[a-zA-Z]', '', str(h))
        #     h = self.convertToPixel(uh.group(), float(h))
        #     svg.root.attrib['height'] = str(h)
        
        page = [ float(w),
                 float(h) ]
        for line in result:
            fields = line.split(',')
            if len(fields) != 5: continue
            area = [ float(x) for x in fields[1:] ]
            area[2] += area[0]
            area[3] += area[1]
            layout[fields[0]] = self._flip(area, page)

        self.limit = max(page) / self.options['zoom']
        element_location_count = len(list(layout.keys()))
        print('Surveyed %d element locations.' % element_location_count)

        return element_location_count

    def _flip(self, area, page):
        # Helper to turn --query-all rects into rendering area rects.
        flipped = list(area[:])
        high = abs(area[3]-area[1])
        flipped[1] = page[1] - min(area[1],area[3]) - high
        flipped[3] = flipped[1] + high
        if flipped[2] < flipped[0]:
            flipped[0],flipped[2] = flipped[2],flipped[0]
        return flipped
        
    def locate(self, target):
        # Find a target (element id or area rect) and convert it
        # as necessary to return the area rect.
        
        area = None
        if isinstance(target, list):
            area = target
        elif target in self.layout:
            area = self.layout[target]
        return area
        
    def move(self, target):
        # Find a target (element id or area rect) and move camera to view it instantly.

        area = self.locate(target)
        if area:
            self.area = area
        return area

    def _addFrame(self, svg):

        if self.options['page_view'] and self.options['show_camera_frame']:
            frame = etree.SubElement(svg.root, '{http://www.w3.org/2000/svg}polygon', id ='frame9001')

            camera_width = abs(self.area[2]-self.area[0])
            camera_height = abs(self.area[3]-self.area[1])
            x = self.area[0]
            y = float(svg.root.attrib['height']) - camera_height - min(self.area[3],self.area[1])

            x = x * svg.xs
            y = y * svg.ys
            camera_width = camera_width * svg.xs
            camera_height = camera_height * svg.ys

            # frame_width = int(math.ceil((camera_width + camera_height) / (camera_height if camera_height > camera_width else camera_width)))
            # # frame_width = camera_width / camera_height * svg.xs
            # if camera_width > camera_height :
            #     frame_width = frame_width * svg.xs
            # else:
            #     frame_width = frame_width * svg.ys

            frame_width = (self.area[2]-self.area[0]) / float(self.width) * svg.xs
            h = (self.area[3]-self.area[1]) / float(self.height) * svg.ys
            if h > frame_width:
                frame_width = h

            frame.set('points', '%s,%s %s,%s %s,%s %s,%s' % (x, y, x+camera_width, y, x+camera_width, y+camera_height, x, y+camera_height))
            frame.set('style', 'fill-opacity: 0; stroke: %s; stroke-opacity: 1; stroke-width: %s;' % (self.options['camera_frame_color'], frame_width))

            return frame

        return None
    
    def _extent(self, target, fill=False):
        # Adjusts a target area to match the camera's proper aspect ratio.
        area = self.locate(target)
        if area[3] == area[1]:
            area[3] += 1
        high = float(area[3]-area[1])
        wide = float(area[2]-area[0])
        ratio = wide / high
        shape = self.width / self.height
        if (ratio > shape) == fill:
            mid = float(area[2]+area[0])/2.
            wide = high * shape
            area[0] = mid - wide/2.
            area[2] = mid + wide/2.
        else:
            mid = float(area[3]+area[1])/2.
            high = wide / shape
            area[3] = mid + high/2.
            area[1] = mid - high/2.
        return area

    def fill(self, target):
        # Adjust an area to ensure its center fills the camera's view.
        return self._extent(target, fill=True)

    def fit(self, target):
        # Adjust an area to ensure it fits within the camera's view.
        return self._extent(target, fill=False)
        
    def zoom(self, target, amount=1.0):
        # Given a target area rect, ensure the area is not too small.
        area = self.locate(target)
        if area[3] == area[1]:
            area[3] += 1
        high = float(area[3]-area[1])
        wide = float(area[2]-area[0])
        ratio = wide / high
        if high < self.limit:
            high = self.limit
            wide = high * ratio
        mid = float(area[2]+area[0])/2.
        wide *= amount
        area[0] = mid - wide/2.
        area[2] = mid + wide/2.
        mid = float(area[3]+area[1])/2.
        high *= amount
        area[3] = mid + high/2.
        area[1] = mid - high/2.
        return area
    
    def speed(self, before, after,  svg = None):
        # Given two rectangles, calculate how many frames of animation
        # to spend on a nice swoop from one to the other.
        # Number of frames is bounded.
        
        page = [ float(re.sub(r'[a-zA-Z]', '', svg.root.attrib['width'])),
                 float(re.sub(r'[a-zA-Z]', '', svg.root.attrib['height'])) ]
        before = V( (before[2]+before[0])/2.,
                    (before[3]+before[1])/2. )
        after = V( (after[2]+after[0])/2.,
                   (after[3]+after[1])/2. )
        dist = distance(before, after)
        ts = int(
                linear(
                    0,
                    max(page),
                    dist,
                    self.options['dally'],
                    self.options['dolly']
                )
            )
        ts = min(max(self.options['dally'], ts), self.options['dolly'])
        return ts
    
    def shoot(self, svg, marker='>'):
        # Render one image at the current camera position.
        # Includes two hacks (spill and convert -extent)
        # to fix imprecise image output sizes.
        # Also applies background color to avoid alpha movie problems.
        if self.options['from'] <= self.time <= self.options['until']:
            # time.sleep(0.250)
            # time.sleep(0.01)
            # self._write(svg)
            output = '%s/%s%05d.png' % (self.options['folder'],
                                        self.options['name'],
                                        self.time)

            cmd = Inkscape.cmd[:]
            cmd.append(Inkscape.exportPngCmd(output))

            area = None
            camera_file = None
            camera_image = None

            if self.options['page_view']:
                cmd.append('--export-area-page')
                # cmd.extend([
                #     '--export-area-page',
                #     '--export-width=%s' % self.options['width'],
                #     ])
            else:
                spill = (self.area[3]-self.area[1]) / 20.
                area = "%d:%d:%d:%d" % (self.area[0],
                                        self.area[1] - (spill/2),
                                        self.area[2],
                                        self.area[3] + (spill/2))
                cmd.append('--export-area=%s' % area)
                # cmd.extend([
                #     '--export-area=%s' % area,
                #     '--export-width=%s' % self.options['width'],
                #     ])

            cmd.append('--export-width=%s' % self.options['width'])
            
            frame = self._addFrame(svg)

            self._write(svg)

            if frame is not None:
                svg.root.remove(frame)

            # command = ' '.join( [ '"%s"' % str(Settings.inkscape), str(settings), '"%s"' % self.temp ])
            cmd.append(self.temp)
            # print command
            results = qx(cmd)

            # output_image = Image.open(output)
            # if self.options['page_view'] and self.options['show_camera_frame']:
            #     spill = (self.area[3]-self.area[1]) / 20.
            #     axis = int(self.area[0])

            #     if axis < 0:
            #         axis = 0

            #     ordinat = int(float(svg.root.attrib['height']) - self.area[3])
            #     if ordinat < 0:
            #         ordinat = 0

            #     camera_height = abs(int(self.area[1]-self.area[3]))
            #     camera_width = abs(int(self.area[0]-self.area[2]))
            #     frame_width = int(math.ceil((camera_width + camera_height) / (camera_height if camera_height > camera_width else camera_width)))
            #     # print axis, ordinat, frame_width

            #     axis1 = axis+camera_width
            #     w = float(svg.root.attrib['width'])
            #     if axis1 > w:
            #         axis1 = w

            #     ordinat1 = ordinat+camera_height
            #     h = float(svg.root.attrib['height'])
            #     if ordinat1 > h:
            #         ordinat1 = h

            #     frame_draw = ImageDraw.Draw(output_image)
            #     # frame_draw.line((axis, ordinat, axis+camera_width, ordinat), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     # frame_draw.line((axis, ordinat, axis, ordinat+camera_height), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     # frame_draw.line((axis, ordinat+camera_height, axis+camera_width, ordinat+camera_height), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     # frame_draw.line((axis+camera_width, ordinat, axis+camera_width, ordinat+camera_height), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     frame_draw.line((axis, ordinat, axis1, ordinat), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     frame_draw.line((axis, ordinat, axis, ordinat1), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     frame_draw.line((axis, ordinat1, axis1, ordinat1), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     frame_draw.line((axis1, ordinat, axis1, ordinat1), fill=ImageColor.getrgb(self.options['camera_frame_color']), width=frame_width)
            #     # frame_draw.ellipse((axis-1, ordinat-1, axis+1, ordinat+1))
            #     del frame_draw
            #     output_image.save(output, 'PNG', quality=100)

            # if not self.options['no_background']:
            #     background = Image.new("RGB", output_image.size, ImageColor.getrgb(self.options['background_color']))
            #     # background.paste(output_image, mask=output_image.split()[3]) # 3 is the alpha channel
            #     background.paste(output_image,(0,0),output_image)
            #     background.save(output, 'PNG', quality=100)
            
            print('  ' + marker + ' ' + output)
            #print '  ' + marker, output
        self.time += 1

    def hold(self, ts=1):
        # Make a number of duplicates of the most recent frame written.
        if ts <= 0: return
        before = "%s/%s%05d.png" % (str(self.options['folder']),
                                    str(self.options['name']),
                                    self.time-1)
        for i in range(ts):
            after = "%s/%s%05d.png" % (str(self.options['folder']),
                                       str(self.options['name']),
                                       self.time)
            if self.options['from'] <= self.time <= self.options['until']:
                shutil.copyfile(before, after)
                print('  = %s' % after)
            self.time += 1

    def pan(self, svg, target, ts=0, margin=1.0):
        # Shoot the intervening frames from the current camera area toward
        # a target camera area.  The camera speed eases into the motion and
        # eases to a stop, rather than lurching with a simple linear
        # interpolation, but the motion is in a direct path.
        
        before = self.area
        if isinstance(target, list):
            pass
        elif target in self.layout:
            target = self.zoom(self.fit(self.locate(target)), margin)
        else:
            return
        if not ts:
            ts = self.speed(before, target,  svg)
        a = V(before)
        b = V(before)
        c = V(target)
        d = V(target)
        for i in range(ts):
            tt = (i + 1) / float(ts)
            where = bezier( tt, a, b, c, d ).list()
            self.move(where)
            self.shoot(svg, marker='-')
            
    def cleanup(self):
        # Remove any temporary files required for rendering.
        if os.path.exists(self.temp):
            os.unlink(self.temp)
        
        for f in os.listdir(self.options['folder']):
            if re.search('camera[0-9]*\.png', f):
                os.remove(os.path.join(str(self.options['folder']), f))
