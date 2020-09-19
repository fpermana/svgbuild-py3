SVGBuild-py3
========

SVGBuild is an open source python script created by Ed Halley in 2008. Original script available at http://halley.cc/code/. It could be used to produce sequence of images from an [Inkscape's](https://inkscape.org/) SVG files.

These sequence of images later could be used to create a timelapse-like video using [FFMPEG](https://ffmpeg.org/) or similar tools.

This repository is modified version of the original one. I made some improvements such as removing external ImageMagick dependency, add several new options, and more.

I also made web app version and available here https://fpermana.id/svg-build.


Dependency
-----
* [Inkscape](https://inkscape.org/)
* [lxml](https://pypi.org/project/lxml/)
* [svg.path](https://pypi.org/project/svg.path/)
* [Pillow](https://pypi.org/project/Pillow/)


Usage
----- 

    main.py [options] filename.svg

Options available via

    main.py -h


Examples
-----

Below are several results with different options


    main.py --build-path --detail-path --path-node-count=2 --use-object-color --zoom=4 inkscape-island-of-creativity.svg
original file was downloaded from [inkscape-island-of-creativity.svg](https://inkscape.org/~bayubayu/%E2%98%85island-of-creativity)
to be updated
.....

    main.py --build-path --detail-path --circle-path --use-object-color --line-color="#FF0000" --page-view Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.svg

original file was downloaded from [Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.svg](https://inkscape.org/~ridjam/%E2%98%85freedom-machine)
to be updated
.....

FFMPEG
-----
    ffmpeg -nostdin -y -f image2 -i inkscape-island-of-creativity/inkscape-island-of-creativity%05d.png -vcodec libx264 -pix_fmt yuv420p  inkscape-island-of-creativity.mp4
    ffmpeg -nostdin -y -f image2 -i Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam_page/Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam%05d.png -vcodec libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.mp4

Results
-----
to be updated
.....


License
-------

The original script is licensed under Artistic License.
This repository is under a GNU GPLv3 License.
