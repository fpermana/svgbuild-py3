SVGBuild-py3
========

SVGBuild is an open source Python script originally created by Ed Halley. Source code is available for download from here http://halley.cc/code/?python/svgbuild.py. [Python2](https://python.org/), [Inkscape](https://inkscape.org/), and [ImageMagick](https://imagemagick.org/) are needed to run that script. [FFmpeg](https://ffmpeg.org/), [avconv](https://libav.org/avconv.html) or similar tools could be used to create videos as final result.

This repository is modified version of the original one. I made some improvements such as removing external ImageMagick dependency, add several new options, optimize performance, etc.

Web app version also available here https://fpermana.id/svg-build.


Dependency
-----
* [Inkscape](https://inkscape.org/)
* [lxml](https://pypi.org/project/lxml/)
* [svg.path](https://pypi.org/project/svg.path/)


Usage
----- 

    main.py [options] filename.svg

Options available via

    main.py -h


Examples
-----

Below are several results with different options

    main.py --build-path --detail-path --path-node-count=2 --use-object-color --zoom=4 inkscape-island-of-creativity.svg
[![Freedom Machine](https://fpermana.id/images/play_inkscape-island-of-creativity.png "Island of Creativity")](https://fpermana.id/svg-build/island-of-creativity "Island of Creativity")
original file was downloaded from [inkscape-island-of-creativity.svg](https://inkscape.org/~bayubayu/%E2%98%85island-of-creativity)


    main.py --build-path --detail-path --circle-path --use-object-color --line-color="#FF0000" --page-view Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.svg

[![Freedom Machine](https://fpermana.id/images/play_Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.png "Freedom Machine")](https://fpermana.id/svg-build/freedom-machine "Freedom Machine")
original file was downloaded from [Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.svg](https://inkscape.org/~ridjam/%E2%98%85freedom-machine)

FFMPEG
-----

    ffmpeg -nostdin -y -f image2 -i inkscape-island-of-creativity/inkscape-island-of-creativity%05d.png -vcodec libx264 -pix_fmt yuv420p  inkscape-island-of-creativity.mp4
.

    ffmpeg -nostdin -y -f image2 -i Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam_page/Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam%05d.png -vcodec libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" Inkscape_0.92_About_Screen_by_Rizky_Djati_Munggaran_aka_ridjam.mp4

More Results
-----
More samples and results with different options available here https://fpermana.id/svg-build.

Desktop GUI (Deprecated)
-----
SVGBuild also available as desktop app that run on Linux and Windows here [https://github.com/fpermana/SVGBuild-GUI](https://github.com/fpermana/svgbuild-gui). It requires [PyQt4](https://wiki.python.org/moin/PyQt4) to run the script.


License
-------

The original script is licensed under Artistic License.
This repository is under a GNU GPLv3 License.
