#!/usr/bin/env python  
# -*- coding:gbk -*-  
# Author: Lin Longxin (林龙新)
from socket import *  
from time import ctime,sleep 
import os
import threading
import sys
# 网络通信参数
loginUser = ""
HOST = '127.0.0.1'  
PORT = 21567  
BUFSIZE = 1024  
ADDR = (HOST,PORT)  
udpCliSock = socket(AF_INET, SOCK_DGRAM)   # UDP 客户端socket

def cmdSplit(command):
    cmdList = (command.strip()).split(' ') # 把输入的命令串以空格为间隔切分
    for i in range(len(cmdList)-1, -1, -1):
        if cmdList[i] == '':
            del cmdList[i]
    return cmdList

def analyzeCmd(data):
    cmdList = cmdSplit(data)
    cmd = cmdList[0]
    para = cmdList[1:]
    return cmd,para
  
# ------------------------------------------------------     
def login():
    global loginUser
    user = raw_input("Login: ")
    loginUser = user
    udpCliSock.sendto("Login "+user,ADDR)
    data,addr = udpCliSock.recvfrom(BUFSIZE)
    cmd,para = analyzeCmd(data)
    if para[0] == "ok":
        return True
    else:
        return False
# Main menu ------------------------------------------------        
def printMainMenu():
    print "------------- Book Borrowed System --------------------"
    print "         1: Display all books "
    print "         2: Display your borrowed books' List "
    print "         3: Borrow a book "
    print "         4: Return a book "
    print "         0: quit "

def getBookinfoFromData(data):
    bookList = (data.strip()).split(';')
    for i in range(len(bookList)-1, -1, -1):
        if bookList[i] == '':
            del bookList[i]
    return bookList
    
def displayAllBooks():
    udpCliSock.sendto("QueryAll",ADDR)
    data,addr = udpCliSock.recvfrom(BUFSIZE)
    bookList = getBookinfoFromData(data)
    print "All the books of our Library are shown as following: ---------- "
    print "BookID     BookName       Author        Press        Number   "
    for book in bookList:
        print book
        
        
def displayYourBorrowedBooks():
    udpCliSock.sendto("BorrowInfo " + loginUser,ADDR)
    data,addr = udpCliSock.recvfrom(BUFSIZE)
    
    if ((data.strip()).split(' '))[0] == "QueryBorrowInfo":
        print "You have no borrow information "
        return
        
    bookList = getBookinfoFromData(data)
    print "All the books you borrowed are shown as following: ---------- "
    print "BookID     BookName       Author        Press        Number   "
    for book in bookList:
        print book
    
def borrowABook():
    bookID = raw_input("Please input the bookID need to be borrowed: ")
    udpCliSock.sendto("Borrow " + loginUser + " " + bookID,ADDR)
    data,addr = udpCliSock.recvfrom(BUFSIZE)
    print "Borrow " + ((data.strip()).split(' '))[1]
    
def returnABook():
    bookID = raw_input("Please input the bookID need to be returned: ")
    udpCliSock.sendto("Return " + loginUser + " " + bookID,ADDR)
    data,addr = udpCliSock.recvfrom(BUFSIZE)
    print  "Return " + ((data.strip()).split(' '))[1]
        
if __name__ == '__main__':
    if login() == False:
        sys.exit(0)
    while True:
        printMainMenu()
        choice = input("Please input your choice : ")
        if choice == 1:
            displayAllBooks()
        elif choice == 2:
            displayYourBorrowedBooks()
        elif choice == 3:
            borrowABook()
        elif choice == 4:
            returnABook()
        elif choice == 0:
            break
