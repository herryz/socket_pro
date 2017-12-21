#!/usr/bin/env python  
# -*- coding:gbk -*-  
# Author: Lin Longxin (林龙新)
  
from socket import *             # 网络接口函数模块
from time import ctime,sleep  
import os                        # 操作系统模块
import threading                 # 线程操作模块

# 网络通信参数  
HOST = '127.0.0.1'     # 服务器IP地址，采用本地地址
PORT = 21567           # UDP 端口
BUFSIZE = 1024         # 接收消息的缓冲区大小
ADDR = (HOST,PORT)  
udpSerSock = socket(AF_INET, SOCK_DGRAM)   #获得一个socket插口
udpSerSock.bind(ADDR)                      # 服务器UDP端口绑定
udpCliSock = socket(AF_INET, SOCK_DGRAM)   # UDP 客户端socket，用于管理线程往服务线程发送消息
stopState = False                          # 服务线程停止状态字

# 图书信息
books = [
        { 'BookID': 'book001', 'BookName': "C语言程序设计", 'Author': "谭浩强", 'Press': "教育出版社", 'Number': 5 },
        { 'BookID': 'book002', 'BookName': "大学国文", 'Author': "无名氏", 'Press': "教育出版社", 'Number': 4 },
        { 'BookID': 'book003', 'BookName': "计算机科学基础", 'Author': "陆汉权", 'Press': "电子工业出版社", 'Number': 5 }
        ]
        
users = ['zhang', 'li', 'wang']          # 用于列表
                                         
# 用户图书借阅情况信息表                                        
borrowInfo = {
              'zhang':{'book001':1, 'book002':1},
              'li':{'book001':1, 'book002':2}
             }

# Main menu -----------------------------------------------------------------------------------------
def printMainMenu():
    print "------------- Library Management System --------------------"
    print "         1: Display all books "
    print "         2: User management "
    print "         3: Books management "
    print "         0: quit "
    print "-------------—----------------------------------------------"
    print " "

# Function 1: Display all books' information
def displayAllBooksInfo():
    print "All books in this Library are shown as following: \n"
    for book in books:
        print "BookID     BookName       Author        Press        Number   "
        print book['BookID'],  book['BookName'],  book['Author'], book['Press'], book['Number']

# Function 2: User management
def addUser():
    userName = raw_input("Please input a new user name: ")
    for u in users:
        if userName == u:
            print "The user has existed, not need to be added "
            return
    users.append(userName)

    print "Add new user successful, now, the users are : "
    for u in users:
        print u

def returnBooksForUser(user):
    if borrowInfo.has_key(user) == False:
        return
    bookList = borrowInfo[user]
    keys = bookList.keys()
    
    for book in keys:
        for i in range(0, len(books)):
            if book == books[i]['BookID']:
                books[i]['Number'] += bookList[book]
    del borrowInfo[user]
    
def delUser():
    userName = raw_input("Please input a user needed to be deleted: ")
    userExisted = False
    for u in users:
        if userName == u:
            returnBooksForUser(userName)
            users.remove(userName)
            userExisted = True
            print "The user %s has been removed" % userName
            break

    if userExisted == False:
        print "Input user is not existed , please check it again"
    print "The users in this Library are : "
    for u in users:
        print u

def userManage():
    while True:
        print "----Sub Function - User Management ------------"
        print "         1: Add a user "
        print "         2: Delete a user "
        print "         0: return "
        choice = input("Please input your choice : ")
        if choice == 1:
            addUser()
        elif choice == 2:
            delUser()
        elif choice == 0:
            return

# Function 3: Book manage, add a new book or output user's borrow information
def cmdSplit(command):
    cmdList = (command.strip()).split(' ') # 把输入的命令串以空格为间隔切分
    for i in range(len(cmdList)-1, -1, -1):
        if cmdList[i] == '':
            del cmdList[i]
    return cmdList

def addNewBook():
    print "Please input a new book's information [BookID  BookName  Author Press  Number]"
    command = raw_input()
    cmdList = cmdSplit(command)

    if len(cmdList) != 5:
        print "Input format error, correct format is [BookID     BookName       Author        Press        Number]"
        return

    bookID = cmdList[0]
    bookName = cmdList[1]
    author = cmdList[2]
    press = cmdList[3]
    number = int(cmdList[4])

    for i in range(0, len(books)):
        if bookID == books[i]['BookID']:
            books[i]['Number'] += number
            return
    books.append({ 'BookID': bookID, 'BookName': bookName, 'Author': author, 'Press': press, 'Number': number })

def getBookInfo(bookID):
    for i in range(0, len(books)):
        if books[i]['BookID'] == bookID:
            return [bookID, books[i]['BookName'], books[i]['Author'], books[i]['Press']]
        
def displayAllBorrowInfo():
    print " --- All borrow information is shown as following ----- "
    keys = borrowInfo.keys()
    for i in range(0, len(keys)):
        user = keys[i]
        borrowList = borrowInfo[user]
        print "%s has borrowed the following books: "%user
        borrowedBooks = borrowList.keys()
        for j in range(0, len(borrowedBooks)):
            bookInfo = getBookInfo(borrowedBooks[j])
            print bookInfo[0], bookInfo[1],bookInfo[2],bookInfo[3], borrowList[borrowedBooks[j]]
    
def bookManage():
    while True:
        print "---- Sub Function - book Management -------------------"
        print "         1: add a new book "
        print "         2: output all user's borrow information "
        print "         0: return "
        choice = input("please input your choice : ")
        if choice == 1:
            addNewBook()
        elif choice == 2:
            displayAllBorrowInfo()
        elif choice == 0:
            return

def manageThread():
    while True:
        printMainMenu()
        choice = input("Please input your choice : ")
        if choice == 1:
            displayAllBooksInfo()
        elif choice == 2:
            userManage()
        elif choice == 3:
            bookManage()
        elif choice == 0:
            udpCliSock.sendto("Quit",ADDR)
            break
        else:
            pass
# ---------------- 以上是服务器侧管理线程的相关函数实现 -----------------------------
def analyzeCmd(data):
    cmdList = cmdSplit(data)
    cmd = cmdList[0]
    para = cmdList[1:]
    return cmd,para

def doLogin(command,para,addr):
    for u in users:
        if u == para[0]:
            udpSerSock.sendto("LoginRsp ok",addr)
            return
    udpSerSock.sendto("LoginRsp fail",addr)

def doQueryBorrowInfo(command,para,addr):
    user = para[0]
    if borrowInfo.has_key(user) == False:
        udpSerSock.sendto("QueryBorrowInfo Fail-No borrowing information",addr)
        return
    else:
        borrowedList = borrowInfo[user]
        keys = borrowInfo[user].keys()
        s =""
        for i in range(0, len(keys)):
            bookInfo = getBookInfo(keys[i])
            s = s + " " + bookInfo[0] + " " + bookInfo[1] + " " + bookInfo[2] + " " + bookInfo[3] + " " + str(borrowedList[keys[i]]) + ";"
        udpSerSock.sendto(s,addr)
    
def doReturn(command,para,addr):
    userName = para[0]
    bookID = para[1]
    borrowedBooks = borrowInfo[userName]
    if borrowedBooks.has_key(bookID) == True:
        borrowedBooks[bookID] -= 1
        if borrowedBooks[bookID] == 0:
            del borrowedBooks[bookID]
            
        for i in range(0,len(books)):
            if books[i]['BookID'] == bookID:
                books[i]['Number'] += 1
        udpSerSock.sendto("ReturnRsp Success",addr)
        return
    udpSerSock.sendto("ReturnRsp Fail",addr)

def doQueryAll(command,addr):
    s = ""
    for book in books:
        s = s + book['BookID'] + " " +  book['BookName'] + " " +  book['Author'] + " " +  book['Press'] + " " + str(book['Number']) + ";"
    udpSerSock.sendto(s,addr)
    
def doBorrow(command,para,addr):
    userName = para[0]
    bookID = para[1]
    for i in range(0,len(books)):
        if books[i]['BookID'] == bookID:
            if books[i]['Number'] == 0: #这本书被借完了
                break
            else:
                books[i]['Number'] -= 1
                if borrowInfo.has_key(userName) == False:
                    borrowInfo[userName] = {}
                borrowedBooks = borrowInfo[userName]
                if borrowedBooks.has_key(bookID) == True:
                    borrowedBooks[bookID] += 1
                else:
                    borrowedBooks[bookID] = 1
                udpSerSock.sendto("BorrowRsp Success",addr)
                return
    udpSerSock.sendto("BorrowRsp Fail",addr)

def executeCmd(command, para, addr):
    global stopState # 必须要申明此变量为全局变量，否则会出问题的。
    if command == "Login": # ok
        doLogin(command,para,addr)
    elif command == "BorrowInfo":
        doQueryBorrowInfo(command,para,addr)
    elif command == "Borrow":
        doBorrow(command,para,addr)
    elif command == "Return":
        doReturn(command,para,addr)
    elif command == "QueryAll": 
        doQueryAll(command,addr)
    elif command == "Quit": # ok
        stopState = True
    else:
        pass

def communicationThread():
    while True:
        if stopState == True:
            udpSerSock.close()
            return
        # 通信协议定义
        # 1. 用户登录， 命令为, "Login userName", 例如： Login llx， 如果没有此用户，返回："LoginRsp fail", 否则返回："LoginRsp ok"
        # 2. 用户借阅信息查询， 命令为, "BorrowInfo userName", 例如：BorrowInfo llx， 如果没有图书借阅信息，返回："none", 否则返回： "图书信息1;图书信息2;图书信息3"
        # 3. 用户借书，命令为，"Borrow userName bookID", 返回成功或者失败
        # 4. 用户还书, 命令 "Return userName bookID", 返回成功或者失败
        # 5. 用户查询所有在库书籍，命令"QueryAll", 返回图书列表信息
        # 6. 退出服务线程，命令"Quit"
        data, addr = udpSerSock.recvfrom(BUFSIZE)
        command,para = analyzeCmd(data)
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

    
        

