#!/usr/bin/env python
# -*- coding: utf-8 -*-

from socket import *
import sys
import threading

HOST = '127.0.0.1'
PORT = 21566
BUFSIZE = 1024
ADDR = (HOST, PORT)
udpSerSock = socket(AF_INET, SOCK_DGRAM)
udpSerSock.bind(ADDR)
udpCliSock = socket(AF_INET, SOCK_DGRAM)
stopState = False


patients = [
    {'PatientName': 'Annie', 'In_time': '', 'Time': '', 'Department': 'clinical', 'RoomNum': '302'},
    {'PatientName': 'Dan', 'In_time': '', 'Time': '', 'Department': 'medical', 'RoomNum': '301'}
]



def printMainMenu():
    print "------------- Library Management System --------------------"
    print "         1: Display all books "
    print "         2: User management "
    print "         3: Books management "
    print "         0: quit "
    print "-------------—----------------------------------------------"
    print " "

def manageThread():
    while True:
        printMainMenu()
        choice = input("Please input your choice: ")
        if choice == 1:
            displayAllPatientsInfo()
        elif choice == 0:
            udpCliSock.sendto("Quit", ADDR)
        else:
            pass

def displayAllPatientsInfo():
    print "All patients in this hospital are shown as following: \n"
    for patient in patients:
        print "PatientName     In_time       Time        Department        RoomNum   "
        print patient['PatientName'], patient['In_time'], patient['Time'], patient['Department'], patient['RoomNum']


# ---------------------
def executeCmd(command, para, addr):
    global stopState
    if command == "QueryAll":
        doQueryAll(command, addr)
    elif command == "b":
        pass
    elif command == "c":
        pass
    else:
        pass

def analyzeCmd(data):
    cmdList = cmdSplit(data)
    cmd = cmdList[0]
    para = cmdList[1:]
    return cmd, para

def cmdSplit(command):
    cmdList = (command.strip()).split(' ')  # 把输入的命令串以空格为间隔切分
    for i in range(len(cmdList) - 1, -1, -1):
        if cmdList[i] == '':
            del cmdList[i]
    return cmdList

def doQueryAll(command, addr):
    s = ""
    for patient in patients:
        s = s + patient['PatientName'] + " " + patient['In_time'] + " " + patient['Time'] + " " + \
            patient['Department'] + " " + patient['RoomNum'] + ";"
    udpCliSock.sendto(s, addr)


def communicationThread():
    while True:
        if stopState == True:
            udpSerSock.close()
            return
        data, addr = udpSerSock.recvfrom(BUFSIZE)
        command, para = analyzeCmd(data)
        executeCmd(command, para, addr)


if __name__ == '__main__':
    thread1 = threading.Thread(target=manageThread)
    thread2 = threading.Thread(target=communicationThread)
    # Start the management thread of server
    thread1.start()
    # Start the communication thread of server
    thread2.start()
    thread1.join()
    thread2.join()
