from threading import *
import sys
import numpy as np
import xlrd
import time
import multiprocessing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QTableWidgetItem
from tkinter import filedialog as fd
from threading import *
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

NUM_RUNZ = 1000  # How many times you want the program to run
CONCURRENT_PROCS = 4  # processes running concurrently
ITERATIONS = 20  # Number of iterations for the genetic algorithm (single run)
ENHANCED_POPSIZE = 4  # Number of enhanced solutions included in the initial population
good = 320  # The scores that distinguishes a good solution to be reused in later runs
initPopSize = 8  # initial population size
mutation_chance = 30  # percentz
choices = []  # gonna store the three choices of each student here
tpDr = []  # Store for each project: Number of project, the topic, and the supervisor
first_row = []
a = []

finalArray = []
finalFitness = 0
finalTime = 0
finalGroup = 0

RunB = False

###### read the .xls file and store all of the groups choices#######
book = xlrd.open_workbook("Students_Selections.xls")
sh = book.sheet_by_index(0)
for rx in range(1, sh.nrows):
    for cx in range(2, sh.ncols):
        a.append(sh.cell_value(rx, cx))
    choices.append(a)
    a = []

###### read the .xls file and store all of the topics and Drs of projects#######
top = xlrd.open_workbook("Topics_Drs.xls")
temp = top.sheet_by_index(0)
for rx in range(1, temp.nrows):
    for cx in range(0, temp.ncols):
        a.append(temp.cell_value(rx, cx))
    tpDr.append(a)
    a = []
# print(tpDr)

num_of_groups = len(choices)
num_of_projects = len(tpDr)


# create solution starting at a random position in the student groups' list iterate through the list, assigning the first choice of each group to
# it. If not available, assign second and then third choice. if all are taken, randomly assign a projet that hasn't been assigned yet
def initSample(choices, shift):
    flag = False
    arr = np.zeros(num_of_groups)

    for i in range(shift, len(choices)):
        flag = False
        if choices[i][0] not in arr:  # assign first choice
            arr[i] = choices[i][0]

        elif choices[i][1] not in arr:  # assign second choice
            arr[i] = choices[i][1]

        elif choices[i][2] not in arr:  # assign third choice
            arr[i] = choices[i][2]


        else:
            for m in range(0, len(tpDr)):  # topic
                if (tpDr[int(choices[i][0]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][0]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break

    # after filling the array, we replace the projects num. = 0, with available projects randomly
    for i in range(len(arr)):
        if arr[i] == 0:
            while True:
                randy = np.random.randint(num_of_projects)
                if randy not in arr:
                    # print("Randy not in arr = ", randy)
                    arr[i] = randy
                    break

    for i in range(shift):  # again to iterate through the elements that come before the position of the shift
        flag = False
        if choices[i][0] not in arr:  # assign first choice
            arr[i] = choices[i][0]

        elif choices[i][1] not in arr:  # assign second choice
            arr[i] = choices[i][1]

        elif choices[i][2] not in arr:  # assign third choice
            arr[i] = choices[i][2]


        else:
            for m in range(0, len(tpDr)):  # topic
                if (tpDr[int(choices[i][0]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][0]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in arr):  # topic
                    arr[i] = tpDr[m][0]
                    break

        # after filling the array, we replace the projects num. = 0, with available projects randomly
        for i in range(len(arr)):
            if arr[i] == 0:
                while True:
                    randy = np.random.randint(num_of_projects)
                    if randy not in arr:
                        # print("Randy not in arr = ", randy)
                        arr[i] = randy
                        break
    return arr


# scores of fitness function : F.C=5, S.C=4, T.C=3, B.topic=2, B.Dr=1
def fitness(choices, arr):  # self-explanatory
    score = fitness2(choices,arr)
    for i in range(num_of_groups):
        if arr[i] == choices[i][0]:
            # print("I = ",i ,"Array = ", arr[i], "F C = ",choices[i][0])
            score += 9
        elif arr[i] == choices[i][1]:
            # print("I = ",i ,"Array = ", arr[i], "S C = ", choices[i][1])
            score += 8
        elif arr[i] == choices[i][2]:
            score += 7
        else:
            for m in range(0, len(tpDr)):
                if tpDr[int(choices[i][0]-1)][1] == tpDr[m][1] and arr[i] == tpDr[m][0]:
                    score += 6
                if tpDr[int(choices[i][1]-1)][1] == tpDr[m][1] and arr[i] == tpDr[m][0]:
                    score += 5
                if tpDr[int(choices[i][2]-1)][1] == tpDr[m][1] and arr[i] == tpDr[m][0]:
                    score += 4
                if (tpDr[int(choices[i][0]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 3
                if (tpDr[int(choices[i][1]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 2
                if (tpDr[int(choices[i][2]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 1
    return score


# scores of fitness function : F.C=5, S.C=4, T.C=3, B.topic=2, B.Dr=1
def fitness2(choices, arr):  # self-explanatory
    score = 0
    for i in range(num_of_groups):
        if arr[i] == choices[i][0]:
            # print("I = ",i ,"Array = ", arr[i], "F C = ",choices[i][0])
            score += 1
        elif arr[i] == choices[i][1]:
            # print("I = ",i ,"Array = ", arr[i], "S C = ", choices[i][1])
            score += 1
        elif arr[i] == choices[i][2]:
            score += 1
        else:
            for m in range(0, len(tpDr)):
                if tpDr[int(choices[i][0]-1)][1] == tpDr[m][1] and arr[i] == tpDr[m][0]:
                    score += 1
                    break
                if tpDr[int(choices[i][1]-1)][1] == tpDr[m][1] and arr[i] == tpDr[m][0]:
                    score += 1
                    break
                if (tpDr[int(choices[i][2]-1)][1] == tpDr[m][1]) and (tpDr[m][0] == arr[i]):
                    score += 1
                    break
                if (tpDr[int(choices[i][0]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 1
                    break
                if (tpDr[int(choices[i][1]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 1
                    break
                if (tpDr[int(choices[i][2]-1)][2] == tpDr[m][2]) and (tpDr[m][0] == arr[i]):
                    score += 1
                    break
    return score


def random_selection(choices, population):
    ### This function should return a random solution, with the more fit solutions having a higher chance of being selected
    ### Generate a random number for every solution in the population and multiply it by the fitness function of that solution
    ### Compare the resulting number to every other solution in population and select the greatest one
    maxx = 0
    a = []
    for i in population:
        randy = np.random.randint(100) / 100
        if fitness(choices, i) * randy > maxx:
            maxx = fitness(choices, i) * randy
            a = i
    return a


def mutate(z):  ### given a solution z, select two random groups and swap their projects.
    # if np.random.randint(100)<10:
    randy1 = np.random.randint(num_of_groups - 1)
    randy2 = np.random.randint(num_of_groups - 1)
    temp = z[randy1]
    z[randy1] = z[randy2]
    z[randy2] = temp
    return z


def reproduce(x, y):  # randomly mix different portions of different solutions together
    # When projects collide, assign a different project to group using the same method used in initSample()
    randy = np.random.randint(len(x))
    child = np.concatenate([x[0:randy], y[randy:]])
    x = x[0:randy]
    for i in range(randy, len(child)):
        flag = False
        if child[i] in x:
            child[i] = 0
            if choices[i][0] not in child:
                child[i] = choices[i][0]

            elif choices[i][1] not in child:
                child[i] = choices[i][1]

            elif choices[i][2] not in child:
                child[i] = choices[i][2]

        else:
             for m in range(0, len(tpDr)):  # topic
                if (tpDr[int(choices[i][0]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][1] == tpDr[m][1]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][0]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][1]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break
                if (tpDr[int(choices[i][2]-1)][2] == tpDr[m][2]) and (tpDr[m][0] not in child):  # topic
                    child[i] = tpDr[m][0]
                    break

        # after filling the array, we replace the projects num. = 0, with available projects randomly
    for i in range(len(child)):
        if child[i] == 0:
            while True:
                randy = np.random.randint(num_of_projects)
                if randy not in child:
                    # print("Randy not in arr = ", randy)
                    child[i] = randy
                    break
    return child


def genetic(population, send_end):
    # print(a)
    # print("**********")
    # for i in population:
    #     print(fitness(choices,i))
    # print("********************************")

    for z in range(ITERATIONS):
        ### Iterate six times () it takes exponentially more time to execute whenever you increase this number
        # Just follow the genetic algorithm in the book
        new_pop = np.zeros((len(population), num_of_groups))
        for j in range(len(population)):
            x = random_selection(choices, population)
            y = random_selection(choices, population)
            child = reproduce(x, y)
            if np.random.randint(100) < mutation_chance:  ####small random chance of mutation
                child = mutate(child)
            new_pop[j] = child
        # population=new_pop
        # population=np.append(population,new_pop,axis=0)
        #     print(new_pop)
        #########################################################################################################
        # Improvement: the new value of population for the next iteration should contain the best values of both
        # population and newpop
        #########################################################################################################
        for i in range(len(population - 1)):
            for j in range(0, len(population) - 1):
                if (fitness(choices, population[j]) > fitness(choices, population[j + 1])):
                    population[[j, j + 1]] = population[[j + 1, j]]
                if (fitness(choices, new_pop[j]) < fitness(choices, new_pop[j + 1])):
                    new_pop[[j, j + 1]] = new_pop[[j + 1, j]]

        for i in range(len(population)):
            if fitness(choices, new_pop[i]) > fitness(choices, population[i]):
                population[i] = new_pop[i]
        ###################################################################################################################
        # Check how far the algorithm has progressed when it reaches z=4. If the fittest solution is less than
        # 190 discard this run. Many runs of this algorithms will have reached far more than 140 by the time z=4
        # so there is no use in continuing. This helps save time and CPU useage
        ####################################################################################################################
        if z == 4:
            maxx = 0
            a = []
            for i in population:  ### find the fittest solution in the population and print it
                if fitness(choices, i) > maxx:
                    maxx = fitness(choices, i)
                    a = i
            if maxx < 290:
                break
    ### find the fittest solution in the population
    maxx = 0
    a = []
    for i in population:
        if fitness(choices, i) > maxx:
            maxx = fitness(choices, i)
            a = i

            # Send solution through pipe to the parent process
    send_end.send(a)
    exit(0)


################################################################################################################
################################################################################################################
class Worker(QObject):
    finished = pyqtSignal()  # give worker class a finished signal

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.continue_run = True  # provide a bool run condition for the class

    def do_work(self):
        i = 1
        while self.continue_run:  # give the loop a stoppable condition
            print(i)
            QThread.sleep(1)
            i = i + 1
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop(self):
        self.continue_run = False  # set the run condition to false on stop


class Ui_MainWindow(object):
    stop_signal = pyqtSignal()  # make a stop signal to communicate with the worker in another thread
    stopFlag = False
    runFlag = False
    good = 320  # The scores that distinguishes a good solution to be reused in later runs
    MAX_TIME = 500  # Don't take any longer than MAX_TIME seconds

    members = []
    b = []
    ###### read the .xls file and store all of the groups choices#######
    book = xlrd.open_workbook("Students_Selections.xls")
    sh = book.sheet_by_index(0)
    for rx in range(1, sh.nrows):
        for cx in range(1, 2):
            b.append(sh.cell_value(rx, cx))
        members.append(b)
        b = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(735, 564)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, -10, 581, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 340, 731, 201))
        self.label.setStyleSheet("background-image : url(Graduation .jpg)")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/newPrefix/Graduation .jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(340, 80, 341, 241))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget.verticalHeader().setVisible(False)

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 130, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(40, 230, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(40, 180, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(190, 140, 81, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(190, 240, 81, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(190, 190, 81, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(430, 320, 81, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(350, 50, 71, 31))
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(510, 320, 81, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")

        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(350, 30, 101, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(460, 30, 41, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(580, 50, 81, 31))
        self.label_9.setObjectName("label_9")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 735, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("AI Project#1", "AI Project#1"))
        self.label_2.setText(_translate("AI Project#1", "Birzeit Graduation Projects Distribution Program"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("AI Project#1", "Group No."))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("AI Project#1", "Group Members"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("AI Project#1", "Taken Project "))
        self.label_3.setText(_translate("AI Project#1", "Fitness:"))
        self.label_4.setText(_translate("AI Project#1", "Satisfied Groups:"))
        self.label_5.setText(_translate("AI Project#1", "Time:"))
        self.pushButton.setText(_translate("AI Project#1", "Run"))
        self.pushButton_2.setText(_translate("AI Project#1", "Stop"))

        # Thread:
        self.thread = QThread()
        self.worker = Worker()
        # self.stop_signal.connect(self.worker.stop)  # connect stop signal to worker stop method
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)  # connect the workers finished signal to stop thread
        self.worker.finished.connect(self.worker.deleteLater)  # connect the workers finished signal to clean up worker
        self.thread.finished.connect(self.thread.deleteLater)  # connect threads finished signal to clean up thread
        self.thread.started.connect(self.worker.do_work)
        self.thread.finished.connect(self.worker.stop)


        # Run Button action:
        self.pushButton.clicked.connect(self.thread1)
        # Stop Button action:

        self.pushButton_2.clicked.connect(self.stop_thread)

    def stop_thread(self):
        if self.runFlag == True:
            self.stopFlag = True
            self.runFlag = False
            self.label_9.setText("Wait a second...")

        # self.stop_signal.emit()  # emit the finished signal on stop
        # exit()

    def thread1(self):
        self.runFlag = True
        self.stopFlag = False
        self.good = 320
        t1 = Thread(target=self.OpenClick)
        t1.start()

    def OpenClick(self):
        self.label_6.setText("Searching... ")

        # check the time at the start of the program
        beg = time.time()
        ####### To use multiprocesses, we must store Each PID in this list ##########
        process_list = []
        ####### Keep a list of good solutions to include in future runs in the initial population############
        solution_list = np.zeros((ENHANCED_POPSIZE, num_of_groups))
        #print("Awkwardly waiting")
        # Every time we receive a solution with better fitness than before, we store that fitness in maxx
        maxx = 0
        cnt2 = 0
        # And we store the solution in best
        best = []
        # Create Pipe for the children to send the main process their most fit solutions
        recv_end, send_end = multiprocessing.Pipe(False)
        for i in range(NUM_RUNZ + 1):  # How many times you want the program to run
            self.label_6.setText("Searching. ")
            cnt = 0
            ###Initilize a population with the size that is predefined (initial population size)
            population = np.zeros((initPopSize, num_of_groups))
            while cnt < initPopSize:
                a = initSample(choices, np.random.randint(num_of_groups))
                population[cnt] = a
                cnt += 1
            self.label_6.setText("Searching.. ")
            # If there are more than CONCURRENT_PROCS processes running concurrently
            if len(process_list) >= CONCURRENT_PROCS:  # or True:
                self.label_6.setText("Searching... ")
                # wait for the oldest process in the list to finish (if it hasn't already)
                process_list.pop(0).join()
                self.label_6.setText("Searching. ")
                # Receive a solution from pipe
                solution = recv_end.recv()
                self.label_6.setText("Searching.. ")
                # Check if it's better than previous ones
                sol_fit = fitness(choices, solution)
                # If the solution is fit enough -> add it to the solution_list
                # Increase our standards of a good solution afterwards (good+=1)
                if sol_fit >= self.good and not any(np.array_equal(x, solution) for x in solution_list):
                    self.label_6.setText("Searching... ")
                    solution_list[cnt2 % ENHANCED_POPSIZE] = solution
                    cnt2 += 1
                    self.good += 1
                if cnt2 > ENHANCED_POPSIZE - 1:
                    self.label_6.setText("Searching. ")
                    loop = ENHANCED_POPSIZE - 1
                else:
                    self.label_6.setText("Searching. ")
                    loop = cnt2

                #self.label_6.setText(" ")
                # Include the good solutions found so far in the initial population of the next run
                for l in range(loop):
                    population[l] = solution_list[np.random.randint(loop)]
                # Print fitness and solution of the run that has last ended
                #print("Fitness = ", sol_fit)

                self.label_7.setText("Current Fitness =")
                self.label_8.setText(str(sol_fit))

                self.label_6.setText("Searching.. ")
                #print(solution)
                # Keep updating the best solution and its fitness
                if sol_fit > maxx:
                    best = solution
                    maxx = sol_fit
                #print("Fitness2 = ", fitness2(choices, solution))
                # end program condition
                self.label_6.setText("Searching... ")
                # print("stopFlag ", self.stopFlag)
                if maxx > 400 or time.time() - beg > self.MAX_TIME or self.stopFlag:
                    break
            self.label_6.setText(" ")
            # create process to run the algorith, and give the sending end of the pipe
            p = multiprocessing.Process(target=genetic, args=[population, send_end])
            p.start()
            # Add it to list of running processes
            process_list.append(p)

        count = 1
        finalArray = best
        # print("The best distribution of projects is:")
        # for i in range(len(best)):
        #     print("Group ", count, " took Project: ", best[i])
        #     count += 1
        # print(best)

        finalFitness = maxx
        # print("Fitness: ", maxx)
        finalGroup = fitness2(choices, best)
        # print("Number of groups that took projects based on our criteria:", finalGroup)

        # Kill rermaining processes
        for process in process_list:
            process.kill()
        # show how long program took to run
        finalTime = round(abs(beg - time.time()), 2)
        # print("Time=", finalTime)

        # the lables we need to fill it
        self.tableWidget.setRowCount(len(finalArray))

        # Set the table values
        for i in range(len(finalArray)):  # rows
            j = 0
            w = 1
            x = 2
            self.tableWidget.setItem(i, j, QTableWidgetItem(str(i + 1)))  # first col
            target = {39: None, 91: None, 93: None}
            newMem = (str(self.members[i]).translate(target))
            self.tableWidget.setItem(i, w, QTableWidgetItem(str(newMem)))  # second col
            self.tableWidget.setItem(i, x, QTableWidgetItem(str(int(finalArray[i]))))  # third col

        self.label_6.setText("")
        self.label_7.setText("")
        self.label_8.setText("")
        self.label_9.setText("")
        self.lineEdit.setText(str(finalFitness))  # fitness
        self.lineEdit_2.setText(str(finalGroup))  # gorups
        self.lineEdit_3.setText(str(finalTime))  # time


if __name__ == '__main__':
    mypro = QtWidgets.QApplication(sys.argv)
    mywin = QtWidgets.QMainWindow()
    thisui = Ui_MainWindow()
    thisui.setupUi(mywin)
    mywin.show()
    sys.exit(mypro.exec_())
