import os
import socket
import socketHelper
import sys
import tkinter


class CameraView:

    def __init__(self, main, address, port):

        self.main = main

        self.host = address
        self.port = port
        self.currentFileName = None
        self.fileList = []

        self.frame = tkinter.Frame(master=self.main.window, width=1000, height=870)
        self.frame.configure(background='light gray')

        self.info = tkinter.StringVar()
        self.info.set('Ready')

        img = tkinter.PhotoImage(file='Assets/Graphics/logo.png')
        self.imageLabel = tkinter.Label(self.frame, image=img)
        self.imageLabel.place(relx=0.5, rely=0.43, anchor=tkinter.CENTER)
        self.imageLabel.image = img

        self.captureButton = tkinter.Button(self.frame, text='Capture', font=('Arial', 14), command=self.captureImage)
        self.captureButton.config(height=2, width=15)
        self.captureButton.place(relx=0.5, rely=0.91, anchor=tkinter.CENTER)

        self.saveButton = tkinter.Button(self.frame, text='Save', font=('Arial', 14), command=self.saveImage)
        self.saveButton.config(height=2, width=15)
        self.saveButton.place(relx=0.3, rely=0.91, anchor=tkinter.CENTER)

        self.deleteButton = tkinter.Button(self.frame, text='Delete', font=('Arial', 14), command=self.deleteImage)
        self.deleteButton.config(height=2, width=15)
        self.deleteButton.place(relx=0.7, rely=0.91, anchor=tkinter.CENTER)

        self.infoLabel = tkinter.Label(self.frame, textvariable=self.info, font=('Arial', 14), width=20)
        self.infoLabel.configure(background='light gray')
        self.infoLabel.place(relx=0.5, rely=0.97, anchor=tkinter.CENTER)

    def start(self):

        self.frame.pack()

    def exit(self):

        if os.name == 'nt':
            path = os.path.dirname(__file__) + '/Saves/'
        else:
            path = 'Saves/'

        for file in self.fileList:
            if os.path.isfile(path + file):
                os.remove(path + file)
                print('Removed ' + file)

        self.frame.pack_forget()

    def saveImage(self):

        if self.currentFileName and self.currentFileName in self.fileList:
            self.fileList.remove(self.currentFileName)
            print('Saved ' + self.currentFileName)

    def deleteImage(self):

        if self.currentFileName and self.currentFileName not in self.fileList:
            self.fileList.append(self.currentFileName)
            print('Deleted ' + self.currentFileName)

    def captureImage(self):

        self.info.set('Connecting')
        self.infoLabel.update_idletasks()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        status = s.connect_ex((self.host, self.port))
        s.settimeout(5)

        if status != 0:
            print(status)
            self.info.set('Could not connect')
            self.infoLabel.update_idletasks()
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return

        self.info.set('Sending command')
        self.infoLabel.update_idletasks()
        socketHelper.sendData(s, 'capture'.encode())

        self.info.set('Receiving data')
        self.infoLabel.update_idletasks()

        fileName = socketHelper.recvData(s).decode()
        if os.name == 'nt':
            fileName = fileName.replace(':', '')

        self.currentFileName = fileName
        self.fileList.append(fileName)

        if os.name == 'nt':
            path = os.path.dirname(__file__) + '/Saves/'
        else:
            path = 'Saves/'

        socketHelper.recvFile(s, path + fileName)

        if 'Finished' != socketHelper.recvData(s).decode():
            sys.exit(-1)

        print('Captured ' + fileName)

        s.shutdown(socket.SHUT_RDWR)
        s.close()

        img = tkinter.PhotoImage(file='Saves/' + fileName)
        # img.subsample(1000, 750)
        self.imageLabel.config(image=img)
        self.imageLabel.image = img

        self.info.set('Finished')
        self.infoLabel.update_idletasks()
