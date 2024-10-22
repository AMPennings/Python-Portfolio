from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QLabel, QComboBox
)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QTextOption

from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject

import lorem
import random
from transformers import AutoModelForCausalLM, AutoTokenizer

import transformers 
import torch
import time


def cleanText(text:str) -> str:
    '''Removes non-typable characters from the text'''
    clean_text=''
    for chara in text:
        if 32<=ord(chara)<=126:
            clean_text+=chara
    return clean_text


class TextGenerator:
    '''A class used to generate normal text using the TinyLlama library'''
    def __init__(self):
        #loads the model
        self.model = "TinyLlama/TinyLlama_v1.1"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            torch_dtype=torch.float16,
            device_map="auto",
        )


    def generateText(self, prompt:str) -> str:
        '''
        Generates text from the prompt
        '''
        #concatenates prompt, as we don't really care about coherence of the text
        if len(prompt)>100:
            prompt=prompt[-100:]
        
        #generates the text
        sequences = self.pipeline(
            prompt,
            do_sample=True,
            top_k=10,
            num_return_sequences=1,
            repetition_penalty=1.5,
            eos_token_id=self.tokenizer.eos_token_id,
            max_length=500,
        )
        text=''
        for seq in sequences:
            text+=seq['generated_text']
        #removes the prompt from the text
        text=text[len(prompt):]
        #removes non typable characters, and returns
        return cleanText(text)



class CodeGenerator:
    def __init__(self):
        '''A class used to generate normal text using the small codegen library'''
        #loads the model
        self.tokenizer = AutoTokenizer.from_pretrained('Salesforce/codegen-350M-multi')
        self.model = AutoModelForCausalLM.from_pretrained('Salesforce/codegen-350M-multi')

    def generateText(self, prompt:str) ->str:
        '''
        Generates code from the prompt
        '''
        #concatenates prompt
        if len(prompt)>10:
            prompt=prompt[-10:]
        #generates text
        completion = self.model.generate(**self.tokenizer(prompt, return_tensors="pt"),min_length=15,max_length=50)
        text=self.tokenizer.decode(completion[0])
        #removes prompt from output
        text=text[len(prompt):]
        #removes non typable characters, and returns
        return cleanText(text)


class TextGeneratorWorker(QObject):
    '''
    A worker used to generate the text. 
    Args - genCode determines if the worker generates text or code
    '''
    textGenerated = pyqtSignal(str)  # Signal to emit the generated text
    
    def __init__(self):
        super().__init__()
        #get text generator
        self.prompt=''
        self.isRunning=True
        self.generateCode=False
    def start(self):
        self.textGen= TextGenerator() 
        self.codeGen= CodeGenerator() 
        self.run()

    def run(self):
        """
            Main method for the worker thread.
            if prompt is set, it will try to generate text from the
            prompt
        """
        while self.isRunning:
            #if a prompt exists start printing
            if self.prompt:
                #generates text/code if prompt exists
                if self.generateCode:
                    text=self.codeGen.generateText(self.prompt)
                    #if the requested text format changes whilst generation
                    #generate again
                    if not self.generateCode:
                        continue
                else:
                    text=self.textGen.generateText(self.prompt)
                    if self.generateCode:
                        continue
                # Emit the generated text back to the main thread
                self.textGenerated.emit(text)
                # Reset the prompt
                self.prompt = ''  
            #waits
            time.sleep(0.1)

    def stop(self):
        '''Stops the worker loop'''
        self.isRunning=False

class TypingApp(QWidget):
    '''Gui used to help practice touch typing skills'''
    def __init__(self):
        super().__init__()
        #generate a random initial prompt
        self.int_prompt=''
        for _ in range(4):
            random_ascii_value = random.randint(97,122)
            random_character = chr(random_ascii_value)
            
            self.int_prompt+=random_character
        
        self.loaded_text=False
        self.displayed_text=[]
        
        #creates the UI
        self.initUI()

        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.elapsed_seconds = 0

        self.text_worker=None
        self.thread=None
        #starts setup of worker after the code has loaded
        QTimer.singleShot(1,self.setupWorker)
        
    def initUI(self):
        # Control buttons
        self.play_button = QPushButton("Play")
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.togglePlay)
        self.play_button.setEnabled(False)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.resetStatistics)
        self.reset_button.setEnabled(False)
        
        self.gen_mode = QComboBox()
        self.gen_mode.addItems(['Generate Text', 'Generate Code'])
        self.gen_mode.currentIndexChanged.connect(self.resetStatistics)
        self.gen_mode.setEnabled(False)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.reset_button)
        controls_layout.addWidget(self.gen_mode)

        # Statistics display
        self.time_display = QLineEdit("0:00:00")
        self.words_display = QLineEdit("0")
        self.errors_display = QLineEdit("0")
        self.wpm_display = QLineEdit("0.0")

        for line_edit in [self.time_display, self.words_display, self.errors_display, self.wpm_display]:
            line_edit.setReadOnly(True)

        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("Time:"))
        stats_layout.addWidget(self.time_display)
        stats_layout.addWidget(QLabel("Words:"))
        stats_layout.addWidget(self.words_display)
        stats_layout.addWidget(QLabel("Errors:"))
        stats_layout.addWidget(self.errors_display)
        stats_layout.addWidget(QLabel("WPM:"))
        stats_layout.addWidget(self.wpm_display)

        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont('Arial', 16))  # Adjust font size for readability
        self.text_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_display.setCursorWidth(2)
        self.text_display.setAcceptRichText(False)

        self.text_display.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.text_display.setText("Currently Loading Models. Please Wait..")
        layout = QVBoxLayout()
        layout.addLayout(controls_layout)
        layout.addLayout(stats_layout)
        layout.addWidget(self.text_display)

        self.setLayout(layout)
        self.setWindowTitle("Typing Practice App")
        self.setGeometry(100, 100, 800, 400)

    def setupWorker(self):
        """
        Setup the background worker for generating text in a thread,
        and sends an initial text request to the worker
        """
        self.text_worker = TextGeneratorWorker()
        self.thread = QThread()
        self.text_worker.moveToThread(self.thread)
        self.text_worker.textGenerated.connect(self.handleTextGen)
        self.thread.started.connect(self.text_worker.start)
        self.thread.start()
        #request text generation once worker has loaded
        self.requestText()

    def underlineCharacter(self,underline:bool):
        """
        Underline the current character in the textEdit.
        If bool is false, will remove it instead
        """
        #gets the cursor and moves it into position
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, self.current_position)

        # Create a character format for underlining
        format = QTextCharFormat()
        format.setFontUnderline(underline)

        # Select the current character and apply the format
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(format)

    def requestText(self):
        '''
        Sends a request to the worker thread to generate text, provided
        that there isn't already a backlog of text.
        '''
        if len(self.displayed_text)<10:
            self.text_worker.generateCode = self.gen_mode.currentIndex()==1
            self.text_worker.prompt =  self.int_prompt if not len(self.displayed_text) else '\n'.join(self.displayed_text)
            
    def handleTextGen(self,text:str):
        '''
        Handles the text generate from the worker
        '''
        #adds the input text to the backlog
        text_rows=text.split('\n')
        text_rows = [row for row in text_rows if row!='']
        self.displayed_text+=text_rows
        #requests text again to help create a backlog
        self.requestText()
        #if text hasn't been loaded yet, enable all the buttons
        #and initialise the  statistics
        if not self.loaded_text:
            self.play_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.gen_mode.setEnabled(True)
        
            self.loaded_text=True
            # Typing tracking variables
            self.current_position = 0
            self.current_line_number=0
            self.current_line = self.displayed_text[self.current_line_number]
            self.total_words = 0
            self.total_char = 0
            self.total_errors = 0
            self.row_count=0
            self.prev_column=-1
            self.character_error_count = {}
            self.has_made_typo = False  # New flag to track typo status for the current character
            self.loadText()    
            self.clearFormats()
        


    def loadText(self):
        """Load initial text into the text display."""
        self.requestText()
        self.text_display.clear()
        for i, line in enumerate(self.displayed_text):
            self.text_display.append(line)
        self.moveCursorToLine()

    
    def moveCursorToLine(self):
        """Move the cursor to the start of the active line."""
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.text_display.setTextCursor(cursor)
        #scroll to top of the text
        self.text_display.verticalScrollBar().setValue(0)

    def keyPressEvent(self, event):
        """Handle key events for typing."""
        if not self.play_button.isChecked():
            return

        key = event.text()

        # Handle the space key explicitly if it's pressed
        if event.key() == Qt.Key_Space:
            key = " "
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            key = "\n"
        # Ignore non-character keys like Shift, Ctrl, etc.
        if not key:
            return
        
        #if not at the end of a line, check the current key
        if self.current_position < len(self.current_line):
            
            expected_char = self.current_line[self.current_position]
            if key == expected_char:
                #if at the end of the line, move the text
                if key == '\n':
                    self.moveLines()
                else:
                    #If correct and not end of line, update styling
                    self.underlineCharacter(False)
                    if not self.has_made_typo:
                        self.markCorrect(self.current_position)
                    #update statistics
                    self.has_made_typo=False
                    self.total_char+=1
                    self.total_words=self.total_char//5
                    self.updateStats()
                    #move position
                    self.current_position += 1
                    
                # Move to the next character
                
                self.moveToCurrPos()
            else:
                #if error mark as and error and update stats
                self.markIncorrect(self.current_position)
                if not self.has_made_typo:
                    self.incrementErrorCount(expected_char)
                
                self.has_made_typo = True
        #elif if at the end of a line, abnd enter was pressed move to next line
        elif key == '\n':
            self.moveLines()
            self.moveToCurrPos()
        
    def moveLines(self):
        '''
        Removes the first line in the text, clears the textEdit and reloads it
        '''
        self.current_line_number+=1
        self.current_position=0
        self.current_line = ''
        while not self.current_line:
            self.displayed_text.pop(0)
            self.current_line = self.displayed_text[0]
        
        #update the TextEdit
        self.clearFormats()
        self.loadText()

    def markIncorrect(self, position:int):
        """
        Mark the character at the given position as incorrect.
        """
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, position)

        # Format the incorrect character
        format = QTextCharFormat()
        format.setForeground(QColor("red"))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(format)

    def incrementErrorCount(self, char:str):
        """Increment the error count for a given character."""
        #Don't penalise user at end of a line
        if self.current_position < len(self.current_line):
            #increments the dict used for keeping track of error statistics
            if char not in self.character_error_count:
                self.character_error_count[char] = 0
            self.character_error_count[char] += 1

            # increase error count and update the stats
            self.total_errors += 1
            self.updateStats()
    
    def markCorrect(self, position:int):
        """Mark the character at the given position as correct."""
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, position)

        # Format the correct character
        format = QTextCharFormat()
        format.setForeground(QColor("green"))
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(format)

    def clearFormats(self):
        """Remove all formatting from the QTextEdit."""
        # Select the entire content of the QTextEdit
        cursor = self.text_display.textCursor()
        cursor.select(QTextCursor.Document)  
        
        # Create a default QTextCharFormat with no special formatting
        default_format = QTextCharFormat()
        
        # Apply the default format to the selected content
        cursor.setCharFormat(default_format)
        cursor.clearSelection()  # Deselect the text

    def moveToCurrPos(self):
        """Move the cursor to the current typing position in the active line."""
        cursor = self.text_display.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, self.current_position)
        y_pos=self.text_display.cursorRect().y()
        self.text_display.verticalScrollBar().setValue(y_pos+self.text_display.verticalScrollBar().value())
        if cursor.columnNumber() < self.prev_column:
            self.row_count+=1
            # self.text_display.verticalScrollBar().setValue(self.row_count*16)
        self.prev_column=cursor.columnNumber()
        
        self.text_display.setTextCursor(cursor)
        self.underlineCharacter(True)
        
    def togglePlay(self):
        '''
        Starts the application, meant to be connected to play button
        '''
        if self.play_button.isChecked():
            #starts timer
            self.timer.start(1000)
            #update UI
            self.play_button.setText("Pause")
            self.reset_button.setEnabled(False)
            self.gen_mode.setEnabled(False)
            #remove focus s.t space doesn't intefer with play button
            self.play_button.clearFocus()

        else:
            #stops timer
            self.timer.stop()
            #updates UI
            self.play_button.setText("Play")
            self.reset_button.setEnabled(True)
            self.gen_mode.setEnabled(True)

    def resetStatistics(self):
        '''
        Resets the Gui
        '''
        #clears textEdit
        self.displayed_text=[]
        self.text_display.clear()
        self.clearFormats()
        #create new random prompt
        self.int_prompt=''
        for _ in range(4):
            random_ascii_value = random.randint(97,122)
            random_character = chr(random_ascii_value)
            
            self.int_prompt+=random_character
        #disabling the GUI
        self.play_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.gen_mode.setEnabled(False)
        #requests the new text
        self.text_display.setText('Loading New Text...')
        self.loaded_text=False
        self.requestText()
        #Clears all teh statistics
        self.elapsed_seconds = 0
        self.total_words = 0
        self.total_errors = 0
        self.character_error_count.clear()
        self.current_position = 0
        self.updateStats()

    def updateStats(self):
        '''
        Updates the UI to display the current statistics
        '''
        self.time_display.setText(self.formatTime(self.elapsed_seconds))
        self.words_display.setText(str(self.total_words))
        self.errors_display.setText(str(self.total_errors))
        wpm = (self.total_words / (self.elapsed_seconds / 60)) if self.elapsed_seconds > 0 else 0
        self.wpm_display.setText(f"{wpm:.2f}")

    def updateTime(self):
        '''
        Updates The time counter
        '''
        self.elapsed_seconds += 1
        self.updateStats()

    def formatTime(self, seconds:int):
        '''
        Transfers the time from a number of seconds to a 
        format also indicating the number of minutes
        '''
        minutes = seconds  // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def resizeEvent(self, event):
        """Handle widget resizing."""
        # Call the base class implementation (optional but recommended)
        super().resizeEvent(event)
        y_pos=self.text_display.cursorRect().y()
        
        self.text_display.verticalScrollBar().setValue(y_pos+self.text_display.verticalScrollBar().value())

if __name__ == "__main__":
    #starts application
    app = QApplication([])
    window = TypingApp()
    window.show()
    app.exec_()
