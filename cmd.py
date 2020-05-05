# -*- coding: utf-8 -*-

import re
from os.path import expanduser
import argparse

from SVGBuild.SVGBuild import SVGBuild
from SVGBuild import Settings

class MainCMD():
    lineColorName = ""
    
    def __init__(self, options = [], parent = None):
        
        self.svgbuild = SVGBuild()
        self.svgbuild.printText.connect(self.printText)
        '''self.svgbuild.setSingleOption('line', 'red')
        self.svgbuild.setSingleOption('background', 'white')
        #filename = 'D:/vector/LowPolyForest02/LowPolyForest02.svg'
        filename = 'D:/a.svg'
        #filename = 'D:/vector/angelina_jolie_portrait/FreeVector-Angelina-Jolie-Portrait.svg'
        #filename = 'D:/vector/Hayley_williams_vector_popart_portrait/Hayley williams vector popart portrait.svg'
        #filename = 'D:/vector/Hayley_williams_vector_popart_portrait/Hayley.svg'
        #filename = 'D:/vector/FreeVector-Angelina-Jolie-Art/FreeVector-Angelina-Jolie-Art.svg'
        self.svgbuild.setFilename(filename)
        workingDirectory = re.sub(r'[^\/]*$', '', filename)
        foldername = "%s%s" % (workingDirectory, 'a')
        self.svgbuild.setSingleOption("folder",  foldername)
        self.svgbuild.setSingleOption('fullpath',  True)
        self.svgbuild.setSingleOption('marker', '')
        self.svgbuild.setSingleOption('objectline', True)
        self.svgbuild.setSingleOption('nobackground', False)
        self.svgbuild.setSingleOption('fillpath', False)
        self.svgbuild.setSingleOption('circlepath', False)
        self.svgbuild.setSingleOption('closepath', False)
        #self.svgbuild.setSingleOption('page',True)
        #self.svgbuild.setSingleOption('top',True)
        self.svgbuild.setSingleOption('backward',True)
        self.svgbuild.setSingleOption('path', True)'''
        #self.svgbuild.setSingleOption('from', 5877)
        #self.svgbuild.setSingleOption('until', 900)
        #print workingDirectory + ' ' + foldername
        """self.lineColorName = self.svgbuild.getSingleOption('line')
        self.svgbuild.printText.connect(self.appendText)"""

        for arg in vars(options):
            if arg == 'filename':
                filename = getattr(options, arg)
                # workingDirectory = re.sub(r'[^\/]*$', '', filename)
                # foldername = re.sub(r'\.[^\.]*$', '', filename)
                self.svgbuild.setFilename(filename)
                # self.svgbuild.setSingleOption("folder",  foldername)

                # print 'filename', filename
                # print 'foldername', foldername

            else:
                # print arg, getattr(options, arg)
                self.svgbuild.setSingleOption(arg,getattr(options, arg))
    
    def run(self):
        print("run")
        self.svgbuild.setIsRunning(True)
        self.svgbuild.startBuildUp()

    def printText(self, line):
        print(line)

    """@pyqtSignature("")
    def on_lineToolButton_clicked(self):
        lineColorDialog = QColorDialog(self)
        if lineColorDialog.exec_() == QDialog.Accepted:
            self.lineColorName = str(lineColorDialog.selectedColor().name())
            self.lineColorWidget.setStyleSheet("QWidget { background-color: %s }" % self.lineColorName)
            self.svgbuild.setSingleOption('line',  self.lineColorName)
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_backgroundToolButton_clicked(self):
        backgroundColorDialog = QColorDialog(self)
        if backgroundColorDialog.exec_() == QDialog.Accepted:
            backgroundColorName = str(backgroundColorDialog.selectedColor().name())
            self.backgroundColorWidget.setStyleSheet("QWidget { background-color: %s }" % backgroundColorName)
            self.svgbuild.setSingleOption('background',  backgroundColorName)
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_cameraFrameToolButton_clicked(self):
        frameColorDialog = QColorDialog(self)
        if frameColorDialog.exec_() == QDialog.Accepted:
            frameColorName = str(frameColorDialog.selectedColor().name())
            self.cameraFrameColorWidget.setStyleSheet("QWidget { background-color: %s }" % frameColorName)
            self.svgbuild.setSingleOption('frame',  frameColorName)
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_openFileLineEdit_returnPressed(self):
        self.selectFile()
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_openFilePushButton_clicked(self):
        self.selectFile()
        # TODO: not implemented yet
#        raise NotImplementedError
        
    def selectFile(self):
        #selectedFileName = QtGui.QFileDialog.getOpenFileName(self,"Open file",QtCore.QDir.currentPath(), "SVG files (*.svg);;All files (*.*)", QtCore.QString("SVG files (*.svg)"));
        selectedFileName = QFileDialog.getOpenFileName(self, "Open file", expanduser("~"), "SVG files (*.svg)", QString("SVG files (*.svg)"));
        if selectedFileName:
            foldername = QString(selectedFileName)
            foldername.remove(QRegExp("^.*/")).remove(QRegExp("\.[^\.]*$"))
            self.openFileLineEdit.setText(selectedFileName)
            self.folderNameLineEdit.setText(foldername)
    
    @pyqtSignature("")
    def on_buildPushButton_clicked(self):
        if self.buildPushButton.text() == "Build!":
            if not self.openFileLineEdit.text():
                print "no file selected"
            else:
                if not self.svgbuild.isRunning:
                    self.optionsGroupBox.setEnabled(False)
                    self.outputTextEdit.setText("")
                    self.svgbuild.setIsRunning(True)
                    self.svgbuild.setFilename(str(self.openFileLineEdit.text()))
                    workingDirectory = re.sub(r'[^\/]*$', '', str(self.openFileLineEdit.text()))
                    self.svgbuild.setSingleOption("folder",  "%s%s" % (workingDirectory, str(self.folderNameLineEdit.text())))
                    
                    self.svgbuild.setSingleOption('path',  self.buildPathCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('fullpath',  self.fullPathCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('fillpath',  self.fillPathCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('circlepath',  self.circlePathCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('closepath',  self.circlePathCheckBox.checkState() == Qt.Checked and self.closePathCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('text',  self.buildTextCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('image',  self.buildImageCheckBox.checkState() == Qt.Checked)
                    
                    self.svgbuild.setSingleOption('page', self.pageCheckBox.checkState() == Qt.Checked)
#                    self.svgbuild.setSingleOption('combine', self.combineCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('camera', self.cameraCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('backward', self.backwardCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('top', self.topCheckBox.checkState() == Qt.Checked)
                    
                    self.svgbuild.setSingleOption('from', self.fromSpinBox.value())
                    self.svgbuild.setSingleOption('until', self.untilSpinBox.value())
                    self.svgbuild.setSingleOption('height', self.heightSpinBox.value())
                    self.svgbuild.setSingleOption('width', self.widthSpinBox.value())
                    
                    #self.svgbuild.setSingleOption('marker', self.markerComboBox.itemData(self.markerComboBox.currentIndex()).toString())
                    self.svgbuild.setSingleOption('marker', str(self.markerComboBox.currentText().toLower()))
                    self.svgbuild.setSingleOption('objectline', self.objectLineCheckBox.checkState() == Qt.Checked)
                    self.svgbuild.setSingleOption('nobackground', self.transparentCheckBox.checkState() == Qt.Checked)
                    
                    #self.svgBuild.setSingleOption(key,  value)
                    
                    self.thread = QThread()
                    
                    self.buildPushButton.setText("Stop")
                    self.buildPushButton.clicked.connect(self.thread.quit)
                    
                    self.svgbuild.moveToThread(self.thread)
                    
                    self.thread.started.connect(self.svgbuild.startBuildUp)
                    self.svgbuild.finished.connect(self.finished)
                    #self.svgBuild.canceled.connect(self.thread.quit)
                    #self.svgBuild.canceled.connect(self.thread.terminate)
                    self.svgbuild.finished.connect(self.thread.quit)
                    self.thread.finished.connect(self.thread.deleteLater)
                    self.thread.destroyed.connect(self.resetThread)
                    
                    self.thread.start()
                
        else:
            self.optionsGroupBox.setEnabled(True)
            self.svgbuild.setIsRunning(False)
            self.buildPushButton.setText("Build!")
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionSetting_triggered(self):
        settingsDialog = SettingsDialog(self)
        if settingsDialog.exec_() == QDialog.Accepted:
            print 'ok'
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionExit_triggered(self):
        self.close()
        # TODO: not implemented yet
#        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionSVGBuild_Help_triggered(self):
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionAbout_triggered(self):
        aboutDialog = AboutDialog(self)
        if aboutDialog.exec_() == QDialog.Accepted:
            print 'ok'
        # TODO: not implemented yet
#        raise NotImplementedError

    def appendText(self, line):
        self.outputTextEdit.append(line)
        
    def finished(self):
        self.optionsGroupBox.setEnabled(True)
        self.svgbuild.setIsRunning(False)
        self.buildPushButton.setText("Build!")

    def resetThread(self):
        self.svgbuild.moveToThread(QApplication.instance().thread())
"""        


def main():
    import sys
   
    settings = Settings.Settings()
    settings.restoreSettings()

    parser = argparse.ArgumentParser(description='SVGBuild command line interface')
    parser.add_argument('filename', help='svg file name')
    parser.add_argument('--folder', default='movie', help='folder name')
    parser.add_argument('--line', default='', help='line color')
    parser.add_argument('--color', default='', help='object color')
    parser.add_argument('--background', default='white', help='background color')
    parser.add_argument('--marker', default='', help='add marker style')
    parser.add_argument('--objectline', default=False, action='store_true', help='use object\'s line own property')
    parser.add_argument('--objectcolor', default=False, action='store_true', help='use object\'s color own property')
    parser.add_argument('--nobackground', default=False, action='store_true', help='save as transparent png')
    parser.add_argument('--path', default=False, action='store_true', help='build path')
    parser.add_argument('--fullpath', default=False, action='store_true', help='create path point by point')
    parser.add_argument('--fillpath', default=False, action='store_true', help='fill color object while build point by point')
    parser.add_argument('--circlepath', default=False, action='store_true', help='circular path')
    parser.add_argument('--closepath', default=False, action='store_true', help='closed path')
    parser.add_argument('--page', default=False, action='store_true', help='build page area')
    parser.add_argument('--top', default=False, action='store_true', help='bring object to top')
    parser.add_argument('--backward', default=False, action='store_true', help='build from last object')
    parser.add_argument('--from', default=0, type=int, help='starting frame number')
    parser.add_argument('--until', default=99999, type=int, help='ending frame number')
    parser.add_argument('--zoom', default=6.0, type=float, help='zoom camera')
    parser.add_argument('--continue', default=False, action='store_true', help='continue previous build if exist')
    parser.add_argument('--restart', default=False, action='store_true', help='delete previous build if exist')
    options = parser.parse_args()

    wnd = MainCMD(options)
    wnd.run();

if __name__ == '__main__':
    main()


