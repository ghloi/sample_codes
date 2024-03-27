#   This program was made by Gregorio Loi on March 26, 2023
#   Intended use was for Programming Assignment 2 Submission for Computer Networks

import sys, os, time, select, socket

#       HELPER FUNCTIONS
def getServerIP():
    inputIP = False
    while inputIP==False:
        try:
            inputIP = str(raw_input("Provide Server IP: "))
            #Verification optional
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error IP Input: "+str(e))
            inputIP = False
    
    return inputIP

def getPortNumber():
    inputPort = False
    while inputPort==False:
        try:
            inputPort = int(input("Provide Port: #"))
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Port Input: "+str(e))
            inputPort = False
    
    return inputPort

def getCommand():
    inputCom = False
    while inputCom==False:
        try:
            inputCom = str(raw_input("RFTCli> "))

            #Split The Command
            wordSplit = inputCom.split()

            #Check Length
            if (len(wordSplit) > 2) or (len(wordSplit) <= 0):
                print("Invalid Command structure. Try again.")
                inputCom = False 
                continue 

            #Check if first word matches a command
            firstWord = wordSplit[0]
            if firstWord == "CLOSE":
                return wordSplit #Returns Array {"CLOSE"}
            elif firstWord == "RETR":
                return wordSplit #Returns Array {"RETR", "exampleFile.pdf"}
            else:
                #No Command Match, retry >:(
                print("Invalid Command. Try again.")
                inputCom = False 
                continue
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Command Input: "+str(e))
            inputCom = False
    
    return inputCom

def receiveData(tcpSocket, fileName):
    #Let's iteratively receive data
    fileNotFound = False
    fileObj = False
    while True:
        #Receive data
        data = tcpSocket.recv(1000)
        if not data:
            print("Server Terminated Connection!")
            break 
        dataString = str(data)

        #We have to check for length of datastring to ensure 404 and EOF aren't accidentally
        #detected in the binary sequence of files
        if "Error404" in dataString: #File not found
            fileNotFound = True
            print("Error 404: File Not Found on Server!")
            break
        
        #File object initialization has to happen after determining error message or not
        if not fileObj:
            if os.path.exists("./Client/"+fileName):
                os.remove("./Client/"+fileName) #Delete old version
            fileObj = open("./Client/"+fileName, 'wb')

        if str(data)[-3:] == "EOF":
            fileObj.write(data[:len(str(data))-3]) #Remove EOF from end
            break #Done writing
        else:
            fileObj.write(data)
        
    
    #We received the file!
    if not fileNotFound:
        print("Received "+fileName)


#       MAIN
def main():
    #Get Input IP Address to connect to
    inputIP = getServerIP()

    #Get Input Port Number to connect to
    inputPort = getPortNumber()

    #Let's connect to it
    # The proxy server is connecting at IP Address and at inputPort 
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET for IPv4 and SOCK_STREAM for TCP

    
    # Attempt to connect recursively due to server startup times
    while True:
        try:
            tcpCliSock.connect((inputIP, inputPort))
            break 
        except Exception as e:
            print("Error Connecting TCP Socket: "+str(e))

    #Then let's confirm
    print("You are now connected! Enter your commands now.")
    while True:
        #Get a command
        currentCommand = getCommand()
        if currentCommand[0] == "CLOSE":
            tcpCliSock.close()
            break
        elif currentCommand[0] == "RETR":
            stringToSend = "RETR "+currentCommand[1] #Example: RETR testFile.pdf
            tcpCliSock.sendall(currentCommand[1])
            receiveData(tcpCliSock, currentCommand[1])
        #Continue




if __name__ == "__main__":
    main()

