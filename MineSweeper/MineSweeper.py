from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QMainWindow,QToolBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, QThread
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtCore import Qt,pyqtSignal
import random
import numpy as np
import sys
import time
#class that definest the main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Defines the window propertis
        uic.loadUi('uis/Main_window.ui',self)
        self.setWindowTitle('Mine Sweeper')
        self.pushButtonFace.setFixedHeight(35)
        self.pushButtonFace.setFixedWidth(35)
        self.pushButtonFace.setIconSize(QSize(33, 33))
        #creates toolbar
        tool_bar=QToolBar()
        self.addToolBar(tool_bar) 
        #Creates a new gam option, used to start a new game
        new_game_action = QAction('New Game',self)
        new_game_action.setStatusTip('Start New Game')
        new_game_action.triggered.connect(self.reset_game)
        tool_bar.addAction(new_game_action)

        #adds the setttings option, used to make a dialog box in charge of the grid size appear
        settings_action=QAction('Settings',self)
        settings_action.setStatusTip("Change Game Settings")
        settings_action.triggered.connect(self.create_settings_dialog)
        tool_bar.addAction(settings_action)
        self.pushButtonFace.clicked.connect(self.reset_game)
        #sets default settings
        self.timer_thread=None
        self.grid_size=[10,10]
        self.number_of_mines=10
        #starts game
        self.reset_game()

    def closeEvent(self,event):
        #closes the settings window if it is open
        if hasattr(self, 'settings_dialog'):
            self.settings_dialog.close()

    def create_settings_dialog(self):
        #creates the settings dialog box
        self.settings_dialog=SettingsDialog(self)
        self.settings_dialog.show()

    def reset_game(self):
        #removes old boxed
        if self.timer_thread:
            self.timer_thread.stop()
        for i in reversed(range(self.gridLayoutGame.columnCount())):
            for j in reversed(range(self.gridLayoutGame.rowCount())):
                
                child_elem=self.gridLayoutGame.itemAtPosition(j,i)
                if child_elem:
                    child_elem.widget().setParent(None)
        #creates new boxes
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                sweep_button=SweeperButton(self,[i,j])
                self.gridLayoutGame.addWidget(sweep_button,j,i)
        #sets intial values
        self.time=0
        self.labelTime.setText('000')
        self.is_first_move=True
        self.pushButtonFace.setIcon(QIcon('imgs/300-3006803_windows-xp-minesweeper-face-hd-png-download.png'))
        self.flagged_map=np.zeros(self.grid_size)
        self.number_of_flags=self.number_of_mines
        
        self.labelFlags.setText(f"{'00' if self.number_of_flags<10 else ('0' if self.number_of_flags<100 else '')}{self.number_of_flags}")
        
    def start_game(self,avoid_pos):
        self.is_game_over=False
        
        self.timer_thread=TimerThread()
        self.timer_thread.timer_signal.connect(self.update_time)
        self.timer_thread.start()
        
        #designates mines
        poss_mines=np.arange(1, self.grid_size[0]*self.grid_size[1])
        x_arr=[]
        y_arr=[]
        for i in range(max(avoid_pos[0]-1,0),min(avoid_pos[0]+2,self.grid_size[0])):
            for j in range(max(avoid_pos[1]-1,0),min(avoid_pos[1]+2,self.grid_size[1])):
                x_arr+=[i]
                y_arr+=[j]
        drop_posses=np.ravel_multi_index(np.array([x_arr,y_arr]), self.grid_size)
        poss_mines=np.setdiff1d(poss_mines,drop_posses)
        self.mines_location=random.sample(list(poss_mines), self.number_of_mines)
        self.workoutMap()

    def update_time(self,time):
        self.labelTime.setText((f"{'00' if time<10 else ('0' if time<100 else '')}{time}")if  self.time<1000 else '999')
                
    
    def workoutMap(self):
        #calculates the values of each element on the map
        self.solution_map=np.zeros(self.grid_size,dtype=int)
        for loc in self.mines_location:
            xpos,ypos=np.unravel_index(loc, self.solution_map.shape)
            self.solution_map[xpos,ypos]=-1
            solution_map_subset=self.solution_map[max(xpos-1,0):min(xpos+2,self.solution_map.shape[0]),max(ypos-1,0):min(ypos+2,self.solution_map.shape[1])]
            solution_map_subset[solution_map_subset!=-1]+=1

    def btn_flagged(self,btn):
        if self.flagged_map[btn.mypos[0],btn.mypos[1]]==0:
            if self.number_of_flags>0:
                btn.setIcon(QIcon('imgs/flag.png'))
                self.flagged_map[btn.mypos[0],btn.mypos[1]]=1
                self.number_of_flags-=1
                if self.number_of_flags==0:
                    if np.all(self.solution_map[self.flagged_map==1]==-1):
                        self.game_win()

        else :
            btn.setIcon(QIcon(''))
            self.flagged_map[btn.mypos[0],btn.mypos[1]]=0
            self.number_of_flags+=1
        
        self.labelFlags.setText(f"{'00' if self.number_of_flags<10 else ('0' if self.number_of_flags<100 else '')}{self.number_of_flags}")
        #handles right hand click
        pass
    def game_over(self):
        #changes the board if the game is lost
        self.timer_thread.stop()
        self.is_game_over=True
        self.pushButtonFace.setIcon(QIcon('imgs/st,small,507x507-pad,600x600,f8f8f8.u2.png'))
        
        for i in reversed(range(self.gridLayoutGame.columnCount())):
            for j in reversed(range(self.gridLayoutGame.rowCount())):
                
                child_elem=self.gridLayoutGame.itemAtPosition(j,i)
                if child_elem:
                    if self.solution_map[i,j]==-1 :
                        if self.flagged_map[i,j]==0:
                            child_elem.widget().setIcon(QIcon('imgs/mine.png'))
                    elif self.solution_map[i,j]!=0:
                        child_elem.widget().setText(str(self.solution_map[i,j]))
                    child_elem.widget().setEnabled(False)

    def game_win(self):
        #changes the board if the game is won
        self.timer_thread.stop()
        self.is_game_over=True
        self.pushButtonFace.setIcon(QIcon('imgs/EFgibyUU8AA7zMc.png'))
        for i in reversed(range(self.gridLayoutGame.columnCount())):
            for j in reversed(range(self.gridLayoutGame.rowCount())):
                
                child_elem=self.gridLayoutGame.itemAtPosition(j,i)
                if child_elem:
                    if not self.solution_map[i,j] in [0,-1]:
                        child_elem.widget().setText(str(self.solution_map[i,j]))
                    child_elem.widget().setEnabled(False)


    def btn_click(self,btn):
        if self.is_first_move:
            self.start_game([btn.mypos[0],btn.mypos[1]])
            self.is_first_move=False
        #handles left hand click
        #ignotes function if already flagged
        if self.flagged_map[btn.mypos[0],btn.mypos[1]]==1:
            return
        if self.solution_map[btn.mypos[0],btn.mypos[1]]==-1:
            btn.setStyleSheet('background-color:red')
            self.game_over()
        elif self.solution_map[btn.mypos[0],btn.mypos[1]]==0:
            posses_to_check=[[btn.mypos[0],btn.mypos[1]]]
            checked_posses=[]
            while len(posses_to_check)!=0:
                curr_pos=posses_to_check[0]
                posses_to_check.pop(0)
                checked_posses+=[curr_pos]
                for i in range(max(curr_pos[0]-1,0),min(curr_pos[0]+2,self.solution_map.shape[0])):
                    for j in range(max(curr_pos[1]-1,0),min(curr_pos[1]+2,self.solution_map.shape[1])):
                        if not [i,j] in checked_posses and not [i,j] in posses_to_check:
                            if self.solution_map[i,j]==0:
                                posses_to_check+=[[i,j]]
                            else:
                                self.gridLayoutGame.itemAtPosition(j,i).widget().setText(str(self.solution_map[i,j]))
                                checked_posses+=[[i,j]]
                            if self.flagged_map[i,j]==1:
                                self.btn_flagged(self.gridLayoutGame.itemAtPosition(i,j).widget())
                            self.gridLayoutGame.itemAtPosition(j,i).widget().setEnabled(False)
                            
        else:
            btn.setText(str(self.solution_map[btn.mypos[0],btn.mypos[1]]))
        btn.setEnabled(False)

class SweeperButton(QPushButton):
    '''This is just default widget for all my sweeper buttons'''
    def __init__(self,parent,mypos):
        super().__init__()
        self.mypos=mypos
        self.parent=parent
        self.setText('')
        self.setFixedWidth(22)
        self.setFixedHeight(22)
        self.setIconSize(QSize(20, 20))
        
        self.clicked.connect(lambda: self.parent.btn_click(self))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Execute your separate function here
            self.parent.btn_flagged(self)
            
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() ==  Qt.MouseButton.RightButton:
            # Execute your separate function here
            print("Right-click action triggered")
        else:
            super().mouseReleaseEvent(event)

class SettingsDialog(QWidget):
    '''A Dialog box that allows the user to change the grid size of the image, takes 
    the input of the parent window.'''
    def __init__(self,parent):
        #initalises the settings dialog
        super().__init__()
        self.parent=parent
        self.setWindowTitle("Settings")
        uic.loadUi('uis/settings_dialog.ui',self)
        self.spinBoxColNum.setValue(self.parent.grid_size[0])
        self.spinBoxRowNum.setValue(self.parent.grid_size[1])
        self.spinBoxColNum.valueChanged.connect(self.set_max_mine_count)
        self.spinBoxRowNum.valueChanged.connect(self.set_max_mine_count)
        self.spinBoxMineNum.setValue(self.parent.number_of_mines)
        self.pushButtonApply.clicked.connect(self.set_grid_size)
        self.set_max_mine_count()
    def set_max_mine_count(self):
        #ensures that there are less mines than there are squares
        self.spinBoxMineNum.setMaximum(self.spinBoxColNum.value()*self.spinBoxRowNum.value()-9)
    
    def set_grid_size(self):
        #sets the parents grid size for when the grid is applied
        self.parent.grid_size=[self.spinBoxColNum.value(),self.spinBoxRowNum.value()]
        self.parent.number_of_mines=self.spinBoxMineNum.value()
        self.parent.reset_game()
        self.close()

class TimerThread(QThread):
    timer_signal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.time=0
        self.is_running=True

    def run(self):
        count=1
        while self.is_running:
            time.sleep(.05)
            if count>=20:
                self.time+=1
                self.timer_signal.emit(self.time)
                count=0
            else:
                count+=1

    def stop(self):
        self.is_running=False
        self.terminate()
#starts application
app=QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec()


