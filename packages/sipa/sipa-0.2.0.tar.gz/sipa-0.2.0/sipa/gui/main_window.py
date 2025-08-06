"""
Main application window for SIPA.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QShortcut
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
from PyQt5.QtCore import Qt
from cv2 import imwrite

from .ui_main_window import Ui_MainWindow
from ..core import Colors, Filters, Histogram, Rotate, Aritmatich


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Main application window with image processing functionality.
    """
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Initialize variables
        self.imageOrgPixmap = None
        self.imageVPixmap = None
        self.imageOrgArray = None
        self.imageGrayArray = None
        self.imageVArray = None
        self.secondImage = None
        self.imageVersions = []
        self.imageIndex = len(self.imageVersions) - 1

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect all button and menu signals to their handlers."""
        # File operations
        self.pushButton_select.clicked.connect(self.select_image)
        self.actionSave.triggered.connect(self.saveImage)
        self.actionClear.triggered.connect(self.clearLabel)
        self.actionSelect_new_image.triggered.connect(self.new_image)
        
        # Undo/Redo
        self.actionUndo.triggered.connect(self.unDo)
        self.actionRedo.triggered.connect(self.reDo)
        
        # Color operations
        self.pushButton_gray.clicked.connect(self.convertGray)
        self.pushButton_binary.clicked.connect(self.convertBinary)
        self.pushButton_thresh.clicked.connect(self.single_thresh)
        self.pushButton_thresh_2.clicked.connect(self.double_thresh)
        self.pushButton_transformation.clicked.connect(self.transformation)
        self.pushButton_contrast.clicked.connect(self.increaseContrast)
        
        # Geometric operations
        self.pushButton_rotate.clicked.connect(self.rotation)
        self.pushButton_crop.clicked.connect(self.crop)
        self.pushButton_zoom.clicked.connect(self.zoom)
        
        # Filters
        self.pushButton_mean.clicked.connect(self.applyMean)
        self.pushButton_median.clicked.connect(self.applyMedian)
        self.pushButton_saltpepper.clicked.connect(self.applySaltpepper)
        self.pushButton_unsharp.clicked.connect(self.applyUnsharp)
        self.pushButton_prewitt.clicked.connect(self.applyPrewitt)
        
        # Arithmetic operations
        self.pushButton_add.clicked.connect(self.addP)
        self.pushButton_divide.clicked.connect(self.divideP)
        
        # Morphological operations
        self.pushButton_Merode.clicked.connect(self.eroding)
        self.pushButton_Mdilate.clicked.connect(self.dilating)
        self.pushButton_Mopen.clicked.connect(self.opening)
        self.pushButton_Mclose.clicked.connect(self.closing)
        
        # Histogram operations
        self.pushButton_histGray.clicked.connect(self.showHistGray)
        self.pushButton_histR.clicked.connect(self.showHistRed)
        self.pushButton_histG.clicked.connect(self.showHistGreen)
        self.pushButton_histB.clicked.connect(self.showHistBlue)
        self.pushButton_histEq.clicked.connect(self.equalize)
        self.pushButton_histStrech.clicked.connect(self.streching)

        # Keyboard shortcuts
        self.redoShortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redoShortcut.activated.connect(self.reDo)
        self.undoShortcut = QShortcut(QKeySequence.Undo, self)
        self.undoShortcut.activated.connect(self.unDo)
        self.saveShortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.saveShortcut.activated.connect(self.saveImage)

    def new_image(self):
        """Clear the current image and select a new one."""
        self.clearLabel()
        self.select_image()

    def select_image(self):
        """Open file dialog to select and load an image."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose an image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename:
            pixmap = QPixmap(filename)
            self.imageOrgPixmap = pixmap
            self.imageOrgArray = self.convert(pixmap=pixmap)
            self.imageVersions.append(self.imageOrgArray)
            self.update()
            self.pushButton_select.hide()
            self.displayImage(pixmap)

    def convert(self, pixmap=None, arrays=None):
        """
        Convert between QPixmap and numpy array formats.
        
        Args:
            pixmap: QPixmap to convert to numpy array
            arrays: numpy array to convert to QPixmap
            
        Returns:
            Converted format (numpy array or QPixmap)
        """
        if pixmap is not None:
            image = pixmap.toImage()
            byte_array = image.bits().asstring(image.byteCount())
            width, height = image.width(), image.height()
            channels = 4  
            image_array = np.frombuffer(byte_array, dtype=np.uint8).reshape((height, width, channels))
            image_array = image_array[:,:,:3]
            return np.array(image_array)
        else:
            if len(arrays.shape) == 3:
                format = QImage.Format_RGB888
                channels = 3
            else:
                format = QImage.Format_Grayscale8
                channels = 1

            height, width = arrays.shape[:2]
            bytes_per_line = channels * width
            qimage = QImage(arrays.data, width, height, bytes_per_line, format).rgbSwapped()
            return QPixmap.fromImage(qimage)

    def displayImage(self, pixmap):
        """Display image in the GUI label."""
        if not pixmap.isNull():
            pixmap_size = pixmap.size()
            groupbox_size = self.groupBox.size()

            if not (pixmap_size.width() <= groupbox_size.width() and 
                   pixmap_size.height() <= groupbox_size.height()):
                pixmap = pixmap.scaled(groupbox_size, Qt.KeepAspectRatio)
                
            self.label_image.setPixmap(pixmap)
            self.label_image.setFixedSize(pixmap.size())
            self.label_image.setAlignment(Qt.AlignCenter)
        else:
            QMessageBox.information(self, "Error", "Invalid file")

    def saveImage(self):
        """Save the current processed image."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save file", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if filename:
            if len(self.imageVArray.shape) == 3:
                plt.imsave(filename, self.imageVArray)
            else: 
                rgb_image = np.stack((self.imageVArray,) * 3, axis=-1)
                plt.imsave(filename, rgb_image)

    def clearLabel(self):
        """Clear the image display and reset state."""
        self.label_image.clear()
        self.pushButton_select.show()
        self.imageVersions.clear()
        self.label_image.setFixedSize(self.groupBox.size())

    def unDo(self):
        """Undo the last operation."""
        if self.imageIndex > 0:
            self.imageIndex -= 1
            self.imageVArray = self.imageVersions[self.imageIndex]
            self.displayImage(pixmap=self.convert(arrays=self.imageVArray))
        else:
            self.messageBox("There is no image to undo.")

    def reDo(self):
        """Redo the last undone operation."""
        if self.imageIndex < (len(self.imageVersions)-1):
            self.imageIndex += 1
            self.imageVArray = self.imageVersions[self.imageIndex]
            self.displayImage(pixmap=self.convert(arrays=self.imageVArray))
        else:
            self.messageBox("There is no image to redo.")

    def update(self):
        """Update the current image state."""
        self.imageIndex = len(self.imageVersions) - 1
        self.imageVArray = self.imageVersions[self.imageIndex]

    # Color operations
    def convertGray(self):
        """Convert image to grayscale."""
        img = self.imageVArray
        if self.check():
            return
        img = Colors.convert_to_gray(img)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageGrayArray = img
        self.imageVersions.append(img)
        self.update()

    def convertBinary(self):
        """Convert grayscale image to binary."""
        img = self.imageGrayArray
        if self.check(isgray=True, isempyt=True, isint=True, input=self.lineEdit_binary.text()):
            return
        img = Colors.convert_to_binary(img, int(self.lineEdit_binary.text()))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def single_thresh(self):
        """Apply single threshold."""
        img = self.imageGrayArray
        if self.check(isgray=True, isempyt=True, isint=True, input=self.lineEdit_thresh.text()):
            return
        img = Colors.single_threshold(img, int(self.lineEdit_thresh.text()))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def double_thresh(self):
        """Apply double threshold."""
        img = self.imageGrayArray
        values = self.lineEdit_thresh_2.text().split(",")
        if self.check(isgray=True, isempyt=True, islist=True, lenght=3, input=values):
            return
        img = Colors.double_threshold(img, int(values[0]), int(values[1]), int(values[2]))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def transformation(self):
        """Apply RGB transformation."""
        img = self.imageOrgArray
        values = self.lineEdit_transformation.text().split(",")
        if self.check(isempyt=True, islist=True, input=values, lenght=3):
            return
        img = Colors.rgb_transformation(img, b=int(values[2]), g=int(values[1]), r=int(values[0]))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def increaseContrast(self):
        """Increase image contrast."""
        img = self.imageVArray
        if self.check(isempyt=True, input=self.lineEdit_contrast.text(), isfloat=True):
            return
        value = float(self.lineEdit_contrast.text())
        img = Colors.increase_contrast(img, value)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    # Geometric operations
    def rotation(self):
        """Rotate image 90 degrees."""
        img = self.imageVArray
        if self.check():
            return
        img = Rotate.rotate_image(img)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def crop(self):
        """Crop image to specified rectangle."""
        img = self.imageVArray
        values = self.lineEdit_crop.text().split(",")
        if (self.check(isempyt=True, input=self.lineEdit_crop.text(), islist=True, lenght=4) or
            any(self.check(input=val, isint=True) for val in values)):
            return
        img = Rotate.crop(img, int(values[0]), int(values[1]), int(values[2]), int(values[3]))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def zoom(self):
        """Zoom image by specified factor."""
        img = self.imageVArray
        if self.check(isempyt=True, input=self.lineEdit_zoom.text(), isfloat=True):
            return
        value = self.lineEdit_zoom.text()
        img = Rotate.zoom(img, float(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    # Filter operations
    def applyMean(self):
        """Apply mean filter."""
        img = self.imageVArray
        if self.check(isempyt=True, input=self.lineEdit_mean.text(), isint=True):
            return
        value = self.lineEdit_mean.text()
        img = Filters.mean_filter(img, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def applyMedian(self):
        """Apply median filter."""
        img = self.imageVArray
        if self.check(isempyt=True, input=self.lineEdit_median.text(), isint=True):
            return
        value = self.lineEdit_median.text()
        img = Filters.median_filter(img, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()
        
    def applySaltpepper(self):
        """Add salt and pepper noise."""
        img = self.imageVArray
        if self.check(isempyt=True, input=self.lineEdit_saltpepper.text(), isint=True):
            return
        value = self.lineEdit_saltpepper.text()
        img = Filters.salt_pepper(img, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()
    
    def applyUnsharp(self):
        """Apply unsharp masking."""
        img = self.imageVArray
        values = self.lineEdit_unsharp.text().split(",")
        if (self.check(isempyt=True, input=self.lineEdit_unsharp.text(), islist=True) or
            self.check(input=values[0], isint=True) or 
            self.check(input=values[1], isfloat=True)):
            return
        img = Filters.unsharp_mask(img, float(values[0]), float(values[1]))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def applyPrewitt(self):
        """Apply Prewitt edge detection."""
        img = self.imageVArray
        if self.check(isgray=True):
            return
        img = Filters.detect_edge_prewitt(img)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()       

    # Arithmetic operations
    def addP(self):
        """Add two images with weights."""
        values = self.lineEdit_add.text().split(",")
        if (self.check(input=values, islist=True, lenght=2) or
            self.check(input=values[0], isfloat=True) or 
            self.check(input=values[1], isfloat=True)):
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose an image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename:
            pixmap = QPixmap(filename)            
            self.secondImage = self.convert(pixmap=pixmap)
            
        img = self.imageVArray
        img = Aritmatich.add_weighted(img, float(values[0]), self.secondImage, float(values[1]))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def divideP(self):
        """Divide two images."""
        if self.check():
            return
            
        filename, _ = QFileDialog.getOpenFileName(
            self, "Choose an image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename:
            pixmap = QPixmap(filename)            
            self.secondImage = self.convert(pixmap=pixmap)
        
        img = self.imageVArray
        img = Aritmatich.divide(img, self.secondImage)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    # Morphological operations
    def eroding(self):
        """Apply morphological erosion."""
        img = self.imageVArray
        if self.check(isempyt=True, isgray=True, input=self.lineEdit_Merode.text(), isint=True):
            return
        value = self.lineEdit_Merode.text()
        img = Histogram.erode(self.imageVArray, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def dilating(self):
        """Apply morphological dilation."""
        img = self.imageVArray
        if self.check(isempyt=True, isgray=True, input=self.lineEdit_Mdilate.text(), isint=True):
            return
        value = self.lineEdit_Mdilate.text()
        img = Histogram.dilate(self.imageVArray, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def opening(self):
        """Apply morphological opening."""
        img = self.imageVArray
        if self.check(isempyt=True, isgray=True, input=self.lineEdit_Mopen.text(), isint=True):
            return
        value = self.lineEdit_Mopen.text()
        img = Histogram.opening(self.imageVArray, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def closing(self):
        """Apply morphological closing."""
        img = self.imageVArray
        if self.check(isempyt=True, isgray=True, input=self.lineEdit_Mclose.text(), isint=True):
            return
        value = self.lineEdit_Mclose.text()
        img = Histogram.closing(self.imageVArray, int(value))
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    # Histogram operations
    def equalize(self):
        """Apply histogram equalization."""
        img = self.imageVArray
        if self.check(isgray=True):
            return
        img = Histogram.histogram_equalization(img)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def streching(self):
        """Apply histogram stretching."""
        img = self.imageVArray
        if self.check(isgray=True):
            return
        img = Histogram.histogram_stretching(img)
        self.displayImage(pixmap=self.convert(arrays=img))
        self.imageVersions.append(img)
        self.update()

    def showHistGray(self):
        """Show grayscale histogram."""
        img = self.imageVArray
        if self.check(isgray=True):
            return
        value = Histogram.calculate_gray_histogram(img)
        self.plot_histogram(value, "black")
        
    def showHistRed(self):
        """Show red channel histogram."""
        img = self.imageVArray
        if self.check():
            return
        value = Histogram.calculate_rgb_histogram(img)[0]
        self.plot_histogram(value, "red")
        
    def showHistGreen(self):
        """Show green channel histogram."""
        img = self.imageVArray
        if self.check():
            return
        value = Histogram.calculate_rgb_histogram(img)[1]
        self.plot_histogram(value, "green")
        
    def showHistBlue(self):
        """Show blue channel histogram."""
        img = self.imageVArray
        if self.check():
            return
        value = Histogram.calculate_rgb_histogram(img)[2]
        self.plot_histogram(value, "blue")

    def plot_histogram(self, histogram, color):
        """Plot histogram using matplotlib."""
        plt.figure()
        plt.bar(range(256), histogram, width=1.0, color=color)
        plt.title(f"{color.capitalize()} Histogram")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.show()

    def check(self, isgray=False, isempyt=False, input=None, 
              islist=False, isint=False, isfloat=False, lenght: int = 0):
        """
        Validate input parameters and image state.
        
        Returns:
            bool: True if validation fails, False if passes
        """
        if len(self.imageVersions) == 0 and self.imageOrgArray is None:
            return self.messageBox("You have to select an image...")
            
        if isgray and self.imageGrayArray is None:
            return self.messageBox("You have to convert image to gray scale...")
            
        if isempyt and input == "":
            return self.messageBox("You have to input a value...")
            
        if islist and lenght != 0 and len(input) != lenght:
            return self.messageBox(f"You have to write {lenght} integer parameters like how it is shown...")
            
        if isfloat:
            try: 
                float(input) 
            except: 
                return self.messageBox("You have to write float type value...")
                
        if isint:
            try: 
                int(input) 
            except: 
                return self.messageBox("You have to write integer type value...")

        return False
    
    def messageBox(self, message):
        """Show warning message box."""
        QMessageBox.warning(self, "WARNING", message)
        return True


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
