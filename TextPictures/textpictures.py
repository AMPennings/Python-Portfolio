from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QSpinBox, QTextEdit, QFileDialog, QHBoxLayout, QLabel
)
import sys
from PyQt5.QtGui import QClipboard, QImage, QColor, QTextCursor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QFont

import numpy as np


class TextManipulationApp(QWidget):
    '''
    Applications used to format a line of text to 
    look like an image
    '''
    def __init__(self):
        super().__init__()
        # Initialize UI elements
        self.initUI()  

        #inits the textedit
        self.text_edit_1.setText(
            '''Enter text here. \n Adjust repeat number, linebreaks and font size to get desired shape of text. \n Then load image and click run'''
        )

        # Image holder
        self.image = None

        # Window settings
        self.setWindowTitle("Text Formatting App")
        self.resize(800, 600)

    def initUI(self):
        """Initialize all UI elements and layout."""
        # Layout
        self.layout = QVBoxLayout()

        # Widgets
        self.text_edit_1 = QTextEdit()
        self.text_edit_2 = QTextEdit()
        self.text_edit_2.setReadOnly(True)
        self.text_edit_2.setStyleSheet("font-size: 1px;")
        font = QFont("Arial")
        self.text_edit_2.setFont(font)

        self.button = QPushButton('Load Image')
        self.copy_button = QPushButton('Copy Text')
        self.run_button = QPushButton('Run')

        # Spin boxes with labels
        self.repeat_label = QLabel('Repeat Count:')
        self.repeat_spinbox = QSpinBox()
        self.repeat_spinbox.setMinimum(1)
        self.repeat_spinbox.setMaximum(10000)
        self.repeat_spinbox.setValue(3)

        self.interval_label = QLabel('Line Break Interval:')
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(10000)
        self.interval_spinbox.setValue(40)

        self.font_size_label = QLabel('Font Size:')
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(1)
        self.font_size_spinbox.setMaximum(100)
        self.font_size_spinbox.setValue(5)

        self.lightness_factor_label = QLabel('Text Lightness Factor (%):')
        self.lightness_factor_spinbox = QSpinBox()
        self.lightness_factor_spinbox.setMinimum(1)
        self.lightness_factor_spinbox.setMaximum(1000)
        self.lightness_factor_spinbox.setValue(80)

        self.saturation_factor_label = QLabel('Text Saturation Factor (%):')
        self.saturation_factor_spinbox = QSpinBox()
        self.saturation_factor_spinbox.setMinimum(1)
        self.saturation_factor_spinbox.setMaximum(1000)
        self.saturation_factor_spinbox.setValue(130)

        self.lightness_offset_label = QLabel('Text Lightness Offset:')
        self.lightness_offset_spinbox = QSpinBox()
        self.lightness_offset_spinbox.setMinimum(-255)
        self.lightness_offset_spinbox.setMaximum(255)
        self.lightness_offset_spinbox.setValue(0)

        self.saturation_offset_label = QLabel('Text Saturation Offset:')
        self.saturation_offset_spinbox = QSpinBox()
        self.saturation_offset_spinbox.setMinimum(-255)
        self.saturation_offset_spinbox.setMaximum(255)
        self.saturation_offset_spinbox.setValue(0)

        self.lightness_factor_bgd_label = QLabel('BGD Lightness Factor (%):')
        self.lightness_factor_spinbox_bgd = QSpinBox()
        self.lightness_factor_spinbox_bgd.setMinimum(1)
        self.lightness_factor_spinbox_bgd.setMaximum(1000)
        self.lightness_factor_spinbox_bgd.setValue(120)

        self.saturation_factor_bgd_label = QLabel('BGD Saturation Factor (%):')
        self.saturation_factor_spinbox_bgd = QSpinBox()
        self.saturation_factor_spinbox_bgd.setMinimum(1)
        self.saturation_factor_spinbox_bgd.setMaximum(1000)
        self.saturation_factor_spinbox_bgd.setValue(70)

        self.lightness_offset_bgd_label = QLabel('BGD Lightness Offset:')
        self.lightness_offset_spinbox_bgd = QSpinBox()
        self.lightness_offset_spinbox_bgd.setMinimum(-255)
        self.lightness_offset_spinbox_bgd.setMaximum(255)
        self.lightness_offset_spinbox_bgd.setValue(0)

        self.saturation_offset_bgd_label = QLabel('BGD Saturation Offset:')
        self.saturation_offset_spinbox_bgd = QSpinBox()
        self.saturation_offset_spinbox_bgd.setMinimum(-255)
        self.saturation_offset_spinbox_bgd.setMaximum(255)
        self.saturation_offset_spinbox_bgd.setValue(0)

        # Layouts for spin boxes and labels
        spinbox_layout_1 = QHBoxLayout()
        spinbox_layout_1.addWidget(self.repeat_label)
        spinbox_layout_1.addWidget(self.repeat_spinbox)
        spinbox_layout_1.addWidget(self.interval_label)
        spinbox_layout_1.addWidget(self.interval_spinbox)
        spinbox_layout_1.addWidget(self.font_size_label)
        spinbox_layout_1.addWidget(self.font_size_spinbox)

        spinbox_layout_2 = QHBoxLayout()
        spinbox_layout_2.addWidget(self.lightness_factor_label)
        spinbox_layout_2.addWidget(self.lightness_factor_spinbox)
        spinbox_layout_2.addWidget(self.saturation_factor_label)
        spinbox_layout_2.addWidget(self.saturation_factor_spinbox)
        spinbox_layout_2.addWidget(self.lightness_offset_label)
        spinbox_layout_2.addWidget(self.lightness_offset_spinbox)
        spinbox_layout_2.addWidget(self.saturation_offset_label)
        spinbox_layout_2.addWidget(self.saturation_offset_spinbox)

        spinbox_layout_3 = QHBoxLayout()
        spinbox_layout_3.addWidget(self.lightness_factor_bgd_label)
        spinbox_layout_3.addWidget(self.lightness_factor_spinbox_bgd)
        spinbox_layout_3.addWidget(self.saturation_factor_bgd_label)
        spinbox_layout_3.addWidget(self.saturation_factor_spinbox_bgd)
        spinbox_layout_3.addWidget(self.lightness_offset_bgd_label)
        spinbox_layout_3.addWidget(self.lightness_offset_spinbox_bgd)
        spinbox_layout_3.addWidget(self.saturation_offset_bgd_label)
        spinbox_layout_3.addWidget(self.saturation_offset_spinbox_bgd)

        # Add Widgets to Layout
        self.layout.addWidget(self.text_edit_1)
        self.layout.addLayout(spinbox_layout_1)
        self.layout.addLayout(spinbox_layout_2)
        self.layout.addLayout(spinbox_layout_3)

        btnlayout = QHBoxLayout()
        btnlayout.addWidget(self.button)
        btnlayout.addWidget(self.copy_button)
        btnlayout.addWidget(self.run_button)
        self.layout.addLayout(btnlayout)

        self.image_label = QLabel('Image Dimensions: Not loaded')
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.text_edit_2)
        self.setLayout(self.layout)

        # Connect Buttons
        self.button.clicked.connect(self.loadImage)
        self.copy_button.clicked.connect(self.copyTextWithFormatting)
        self.run_button.clicked.connect(self.processTextWithImage)

        # Update the second text edit when the first or spinboxes change
        self.text_edit_1.textChanged.connect(self.updateText)
        self.repeat_spinbox.valueChanged.connect(self.updateText)
        self.interval_spinbox.valueChanged.connect(self.updateText)
        self.font_size_spinbox.valueChanged.connect(self.updateText)

    def loadImage(self):
        """Load an image using a file dialog and update image information."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if file_path:
            self.image = QImage(file_path)
            if self.image.isNull():
                self.image_label.setText("Failed to load image.")
            else:
                self.image_label.setText(f"Image Dimensions: {self.image.width()}x{self.image.height()}")

    def updateText(self):
        """Update the formatted text display based on the input and settings."""
        try:
            result_text=self.getOutputText()
            #styles text (N.b have to keep styling consistant for this to work)
            font_size = self.font_size_spinbox.value()
            html_text =  '<span style="font-size: {}px; font-family: Arial;">{}</span>'.format(font_size, result_text.replace("\n", "<br>"))
            #sets html
            self.text_edit_2.setHtml(html_text)
        except Exception as e:
            print(e)

    def getOutputText(self) -> str:
        '''
        Generates the text that should appear in the output textEdit
        '''
        #gets the input text
        input_text = self.text_edit_1.toPlainText()
        #modifies it to have the desired size
        repeat_count = self.repeat_spinbox.value()
        interval = self.interval_spinbox.value()
        repeated_text = (input_text+' ') * int(repeat_count)
        #moves /n to linebreaks
        repeated_text = repeated_text.replace('\n', '')
        result_text = '\n'.join(repeated_text[i:i + interval] for i in range(0, len(repeated_text), interval))
        #makes text upper case
        result_text = result_text.upper()
        
        return result_text
    
    def processTextWithImage(self):
        """
        Process the text overlay with image data, adjusting the appearance.
        Should be connected to the run button
        """
        #if not an image return
        if not self.image:
            print("No image loaded.")
            return
        #ensures text is up to date
        self.updateText()

        #disables all buttons whilst running
        for w in self.findChildren(QPushButton):
            w.setEnabled(False)

        #get max width
        max_text_width=self.getTextMaxWidth()
        

        #calculate the ratio between text and image   
        scale = self.image.width() / max_text_width if max_text_width > 0 else 1
        
        #wraps the text to make all lines the same length
        self.wrapText(max_text_width)

        #updates the text to look like the image
        self.colorText(scale)

        #reenables buttons
        for w in self.findChildren(QPushButton):
            w.setEnabled(True)

    def colorText(self, scale):
        '''
        Formats the text to look like the desired image
        '''
        #gets initial cursor position
        cursor = QTextCursor(self.text_edit_2.document())
        cursor.setPosition(0)
        rect = self.text_edit_2.cursorRect(cursor)
        init_pos=(rect.x(),rect.y())
        
        #gets colors from the spinboxes
        lightness_factor = self.lightness_factor_spinbox.value() / 100
        saturation_factor = self.saturation_factor_spinbox.value() / 100
        lightness_offset = self.lightness_offset_spinbox.value()
        saturation_offset = self.saturation_offset_spinbox.value()

        lightness_factor_bgd = self.lightness_factor_spinbox_bgd.value() / 100
        saturation_factor_bgd = self.saturation_factor_spinbox_bgd.value() / 100
        lightness_offset_bgd = self.lightness_offset_spinbox_bgd.value()
        saturation_offset_bgd = self.saturation_offset_spinbox_bgd.value()
        
        #moves cursor through the image updating the color
        #of the text and background to match the image
        count = 0
        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.NextCharacter)
            rect = self.text_edit_2.cursorRect(cursor)
            #calculates cursors effective position in the image
            x = int((rect.x() -init_pos[0])* scale)
            y = int((rect.y() -init_pos[1])* scale)
            if 0 <= x < self.image.width() and 0 <= y < self.image.height():
                #gets image color
                pixel_color = self.image.pixelColor(x, y)
                #calculates text colors
                text_color = self._adjustSaturation(pixel_color, lightness_factor, saturation_factor, lightness_offset, saturation_offset)
                background_color = self._adjustSaturation(pixel_color, lightness_factor_bgd, saturation_factor_bgd, lightness_offset_bgd, saturation_offset_bgd)
                #formats the text accordingly
                cursor.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(self._getColorFormat(text_color, background_color))
            #move to next character
            cursor.movePosition(QTextCursor.NextCharacter)
            count += 1
            #stops GUI from Freezing
            if count % 100 == 0:
                QApplication.processEvents()
        

    def getTextMaxWidth(self) -> int:
        '''
        Gets the max width of the text in the output textedit
        '''
        max_text_width = 0
        cursor = QTextCursor(self.text_edit_2.document())
        #get initial position of cursor in text edit
        cursor.setPosition(0)
        rect = self.text_edit_2.cursorRect(cursor)
        init_pos=(rect.x(),rect.y())
        
        #scroll the cursor through the text to find
        #the max width of the paragraph
        while not cursor.atEnd():
            cursor.movePosition(QTextCursor.EndOfLine)
            rect = self.text_edit_2.cursorRect(cursor)
            max_text_width = max(max_text_width, rect.x()-init_pos[0])
            cursor.movePosition(QTextCursor.NextCharacter)
        return max_text_width
    
    def wrapText(self,max_width:int):
        '''
        Adjusts the width of the text to match the input
        max_width
        '''
        cursor = QTextCursor(self.text_edit_2.document())
        cursor.setPosition(0)
        
        # Get the text that needs to be rewrapped
        text = self.getOutputText()
        #remove linebreaks as they will be added
        text=text.replace('\n', '')
        # Clear the QTextEdit for re-entering the text
        self.text_edit_2.clear()

        # Runs through the text forcing linebreaks where needed
        current_line = ""
        for char in text:
            # Add the character to the current line
            font_size = self.font_size_spinbox.value()
            html_text = '<span style="font-size: '+str(font_size)+'px; font-family: Arial; white-space: pre;">'+('&nbsp;' if char==' ' else char.upper())+'</span>'
            
            current_line += html_text

            # Temporarily set the text to measure its width
            cursor.insertHtml(html_text)
            rect = self.text_edit_2.cursorRect(cursor)
            line_width = rect.x()

            # Check if the width exceeds the maximum line width
            if line_width > max_width:
                # Remove the last character
                current_line = current_line[:-1]
                cursor.deletePreviousChar()

                # Start a new line with the last character
                cursor.insertText('\n')
                current_line = char
                cursor.insertText(current_line)


    def _getColorFormat(self, color: QColor, background_color: QColor) -> QTextCharFormat:
        """Create a text format with specified foreground and background colors."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setBackground(QColor(background_color))
        return fmt

    def _adjustSaturation(self, color: QColor, lightness_factor: float = 0.7, saturation_factor: float = 1.5, lightness_offset: int = 0, saturation_offset: int = 0) -> QColor:
        """Adjust the saturation and value of a color."""
        hsl = color.toHsl()
        new_value = int(np.clip(hsl.lightness() * lightness_factor + lightness_offset, 0, 255))
        new_saturation = int(np.clip(hsl.saturation() * saturation_factor + saturation_offset, 0, 255))
        hsl.setHsl(hsl.hue(), new_saturation, new_value)
        return hsl

    def copyTextWithFormatting(self):
        """Copy the formatted text to the clipboard."""
        clipboard = QApplication.clipboard()
        text = self.text_edit_2.toHtml()
        start_index = text.find('<span')
        end_index = text.rfind('</span>')
        text = text[start_index:end_index + len('</span>')]
        text = text.replace(';">', '; white-space: pre; font-family: Arial;">')
        clipboard.setText(text, QClipboard.Clipboard)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextManipulationApp()
    window.show()
    sys.exit(app.exec_())
