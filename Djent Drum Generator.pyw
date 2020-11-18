import random
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import *
from midiutil.MidiFile import MIDIFile
import math

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Djent Drum Generator")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.font = QFont("Consolas", 15)
        self.default = "./programdata/settings/default"
        self.midimap = "./programdata/settings/midimap"
        self.mididirectory = "./programdata/midi/"

        self.drummidinotes = []
        self.midinotelengths = []
        self.percentages = []
        self.notevalues = []
        self.percentlabels = []
        self.intlabels = []

        defaultin = open(self.default, 'r')
        for i in range(0, 7):
            self.notevalues.append(int(defaultin.readline()))
        defaultin.close()

        midimapin = open(self.midimap, 'r')
        for i in range(0, 3):
            self.drummidinotes.append(int(midimapin.readline()))
        midimapin.close()

        for i in range(0, len(self.notevalues)):
            for j in range(0, self.notevalues[i]):
                if i == 0:
                    self.midinotelengths.append(0)
                elif i == 1:
                    self.midinotelengths.append(-1)
                else:
                    self.midinotelengths.append(1.0 / (2 ** (i - 2)))

        for i in range(0, 7):
            self.percentages.append(0)
        self.updatepercentages()

        self.keypad()        

        self.palette = self.palette()
        self.palette.setColor(QPalette.Window, QColor(30, 30, 30))
        self.palette.setColor(QPalette.Button, QColor(51, 51, 55))
        self.palette.setColor(QPalette.WindowText, QColor(218, 218, 218))
        self.palette.setColor(QPalette.Base, QColor(154, 154, 154))
        self.palette.setColor(QPalette.Text, QColor(30, 30, 30))
        self.palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setPalette(self.palette)

        self.show()
        
    def keypad(self):
        container = QtWidgets.QWidget()
        container.setLayout(QtWidgets.QGridLayout())
        notelabels = []
        noteincrement = []
        notedecrement = []

        normalnotes = QtWidgets.QLabel("Normal Notes")
        rests = QtWidgets.QLabel("Rests")
        normalnotes.setFont(self.font)
        rests.setFont(self.font)
        container.layout().addWidget(normalnotes, 0, 0)
        container.layout().addWidget(rests, 1, 0)

        subdiv = QtWidgets.QLabel("Note Subdivisions")
        subdiv.setFont(self.font)
        subdiv.setAlignment(Qt.AlignCenter)
        container.layout().addWidget(subdiv, 2, 0, 1, 4)

        for i in range(0, 5):
            notelabels.append(QtWidgets.QLabel("1/" + str(2 ** i)))
            notelabels[i].setFont(self.font)
            container.layout().addWidget(notelabels[i], i + 3, 0)

        for i in range(0, 7):
            if i == 0:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(0, 0)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(0, 0)))
            elif i == 1:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(1, -1)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(1, -1)))
            elif i == 2:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(2, 1)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(2, 1)))
            elif i == 3:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(3, .5)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(3, .5)))
            elif i == 4:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(4, .25)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(4, .25)))
            elif i == 5:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(5, .125)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(5, .125)))
            elif i == 6:
                notedecrement.append(QtWidgets.QPushButton("<", clicked = lambda:self.notedec(6, .0625)))
                noteincrement.append(QtWidgets.QPushButton(">", clicked = lambda:self.noteinc(6, .0625)))
            notedecrement[i].setFont(self.font)
            noteincrement[i].setFont(self.font)
            self.intlabels.append(QtWidgets.QLabel(str(self.notevalues[i])))
            self.intlabels[i].setFont(self.font)

            if i < 2:
                container.layout().addWidget(notedecrement[i], i, 1, 1, 1)
                container.layout().addWidget(noteincrement[i], i, 3, 1, 1)
                container.layout().addWidget(self.intlabels[i], i, 2, 1, 1)
            else:
                container.layout().addWidget(notedecrement[i], i + 1, 1, 1, 1)
                container.layout().addWidget(noteincrement[i], i + 1, 3, 1, 1)
                container.layout().addWidget(self.intlabels[i], i + 1, 2, 1, 1)

        self.drumbutton = QtWidgets.QPushButton("Set drums", clicked = lambda:self.setdrums())
        kicklabel = QtWidgets.QLabel("Kick")
        snarelabel = QtWidgets.QLabel("Snare")
        cymballabel = QtWidgets.QLabel("Cymbal")
        self.drumbutton.setFont(self.font)
        kicklabel.setFont(self.font)
        snarelabel.setFont(self.font)
        cymballabel.setFont(self.font)
        container.layout().addWidget(kicklabel, 8, 0)
        container.layout().addWidget(snarelabel, 9, 0)
        container.layout().addWidget(cymballabel, 10, 0)
        container.layout().addWidget(self.drumbutton, 8, 4)

        self.kick = QtWidgets.QLineEdit()
        self.snare = QtWidgets.QLineEdit()
        self.cymbal = QtWidgets.QLineEdit()
        self.kick.setText(str(self.drummidinotes[0]))
        self.snare.setText(str(self.drummidinotes[1]))
        self.cymbal.setText(str(self.drummidinotes[2]))
        self.kick.setFont(self.font)
        self.snare.setFont(self.font)
        self.cymbal.setFont(self.font)
        container.layout().addWidget(self.kick, 8, 1, 1, 3)
        container.layout().addWidget(self.snare, 9, 1, 1, 3)
        container.layout().addWidget(self.cymbal, 10, 1, 1, 3)

        savebutton = QtWidgets.QPushButton("Save as default", clicked = lambda:self.savesettings())
        self.savename = QtWidgets.QLineEdit()
        self.savename.setText("Enter filename")
        extension = QtWidgets.QLabel(".mid")
        savebutton.setFont(self.font)
        self.savename.setFont(self.font)
        extension.setFont(self.font)
        container.layout().addWidget(savebutton, 11, 0)
        container.layout().addWidget(self.savename, 0, 5)
        container.layout().addWidget(extension, 0, 6)

        for i in range(0, len(self.percentages)):
            self.percentlabels.append(QtWidgets.QLabel(str(self.percentages[i]) + "%"))
            self.percentlabels[i].setFont(self.font)
            if i < 2:
                container.layout().addWidget(self.percentlabels[i], i, 4)
            else:
                container.layout().addWidget(self.percentlabels[i], i + 1, 4)

        exportbutton = QtWidgets.QPushButton("Export", clicked = lambda:self.export())
        self.usermessage = QtWidgets.QLabel("")
        exportbutton.setFont(self.font)
        self.usermessage.setFont(self.font)
        container.layout().addWidget(exportbutton, 1, 5, 1, 2)
        container.layout().addWidget(self.usermessage, 2, 5)
        
        self.layout().addWidget(container)

    def setdrums(self):
        self.drummidinotes[0] = int(self.kick.text())
        self.drummidinotes[1] = int(self.snare.text())
        self.drummidinotes[2] = int(self.cymbal.text())
        self.usermessage.setStyleSheet("color:lightblue")
        self.usermessage.setText("set: drums set")

    def noteinc(self, index, length):
        if not length == None:
            self.midinotelengths.append(length)
            self.updatepercentages()
        self.notevalues[index] += 1
        self.intlabels[index].setText(str(self.notevalues[index]))

    def notedec(self, index, length):
        if (not length == None) and length in self.midinotelengths:
            self.midinotelengths.remove(length)
            self.updatepercentages()
        if not self.notevalues[index] == 0:
            self.notevalues[index] -= 1
            self.intlabels[index].setText(str(self.notevalues[index]))

    def savesettings(self):
        defaultout = open(self.default, 'w')
        for i in range(0, len(self.notevalues)):
            defaultout.write(str(self.notevalues[i]) + '\n')
        defaultout.close()
        midimapout = open(self.midimap, 'w')
        for i in range(0, len(self.drummidinotes)):
            midimapout.write(str(self.drummidinotes[i]) + '\n')
        midimapout.close()
        self.usermessage.setStyleSheet("color:lightblue")
        self.usermessage.setText("set: default set")

    def updatepercentages(self):
        lentotal = 0
        lens = []
        for i in range(0, 5):
            lens.append(0)

        notetotal = 0
        note = 0

        for i in range(0, len(self.midinotelengths)):
            if self.midinotelengths[i] == 0:
                note += 1
                notetotal += 1
            elif self.midinotelengths[i] == -1:
                notetotal += 1
            else:
                lentotal += 1
                lens[int(abs(math.log(self.midinotelengths[i]) / math.log(2)))] += 1

        if not notetotal == 0:
            self.percentages[0] = int(note / notetotal * 100)
            self.percentages[1] = int((notetotal - note) / notetotal * 100)
        else:
            self.percentages[0] = 0
            self.percentages[1] = 0

        if not lentotal == 0:
            for i in range(0, len(lens)):
                self.percentages[i + 2] = int(lens[i] / lentotal * 100)
        else:
            for i in range(0, len(lens)):
                self.percentages[i + 2] = 0

        if not len(self.percentlabels) == 0:
            for i in range(0, len(self.percentlabels)):
                self.percentlabels[i].setText(str(self.percentages[i]) + "%")

    def export(self):
        if self.savename.text() == "" or self.kick.text() == "" or self.snare.text() == "" or self.cymbal.text() == "":
            self.usermessage.setText("err: missing field")
            self.usermessage.setStyleSheet("color:pink")
        else:
            snarelist = []
            cymballist = []
            kicklist = []
            kicktotal = 0
            kicklen = 0

            for i in range(0, 8 * 4):
                cymballist.append(self.drummidinotes[2])
                if i % 4 == 2:
                    snarelist.append(self.drummidinotes[1])
                else:
                    snarelist.append(-1)

            while kicktotal < 8:
                kicklen = random.choice(self.midinotelengths)
                while kicklen == 0 or kicklen == -1 or kicktotal + kicklen > 8:
                    kicklen = random.choice(self.midinotelengths)
                kicklist.append(kicklen)
                kicktotal += kicklen

            self.usermessage.setStyleSheet("color:lightgreen")
            self.usermessage.setText("exp: \"" + self.savename.text() + ".mid\"")
            self.write(kicklist, snarelist, cymballist)

    def write(self, kick, snare, cymbal):
        midifile = MIDIFile(1)
        midichannel = 0
        midivolume = 127
        miditrackbeatcounter = 0
        miditrack = 0
        midifile.addTrackName(miditrack, 0, "Drum MIDI")

        notepercent = self.notevalues[0] / (self.notevalues[0] + self.notevalues[1])
        for i in range(0, len(kick)):
            if random.uniform(0, 1) <= notepercent:
                midifile.addNote(miditrack, midichannel, self.drummidinotes[0], miditrackbeatcounter, kick[i] * 4, midivolume)
            miditrackbeatcounter += kick[i] * 4

        miditrackbeatcounter = 0
        for i in range(0, len(snare)):
            if not snare[i] == -1:
                midifile.addNote(miditrack, midichannel, self.drummidinotes[1], miditrackbeatcounter, .25 * 4, midivolume)
            if not cymbal[i] == -1:
                midifile.addNote(miditrack, midichannel, self.drummidinotes[2], miditrackbeatcounter, .25 * 4, midivolume)
            miditrackbeatcounter += .25 * 4

        with open(self.mididirectory + self.savename.text() + ".mid", "wb") as midiout:
            midifile.writeFile(midiout)

app = QtWidgets.QApplication([])
window = MainWindow()
app.setStyle("Fusion")
app.exec_()
