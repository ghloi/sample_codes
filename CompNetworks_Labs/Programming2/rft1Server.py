#   This program was made by Gregorio Loi on March 26, 2023
#   Intended use was for Programming Assignment 2 Submission for Computer Networks


import sys, os, time, select, socket

#       HELPER FUNCTIONS
def getPortNumber():
    inputPort = False
    while inputPort==False:
        try:
            inputPort = int(input("Listen at Port: #"))
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Port Input: "+str(e))
            inputPort = False
    
    return inputPort

def startServer(inputPort):
    # The proxy server is listening at inputPort 
    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET for IPv4 and SOCK_STREAM for TCP
    tcpSerSock.setblocking(1) #Sets blocking to true (1), which means code will yield for sockets
    tcpSerSock.bind(('localhost', inputPort))
    tcpSerSock.listen(100) #Number inside listen() is maximum number of queued connections allowed

    #List of Sockets to monitor
    socketList = [tcpSerSock]

    #Let's start
    while socketList:
        # Strat receiving data from the client
        readable, writable, exceptional = select.select(socketList, [], [])

        #GO THROUGH EACH READABLE FILE DESCRIPTOR
        for sock in readable:
            if sock is tcpSerSock:
                #Accept a new connection and add that new connection to list of inputs
                clientsock, addr = tcpSerSock.accept()
                print('Connection accepted from '+str(addr[0]))
                socketList.append(clientsock)
            else:
                data = sock.recv(1000) #TCP Payload
                #Send 1000 and receive 1000
                if not data:
                    #Close connections one of the sockets disconnected
                    print("Connection closed, See you later!")
                    print(" ")
                    print('Listening for connection at Port '+str(inputPort)+'...')
                    print("*****************************************************************************") #NewLine

                    #Current Socket Removal
                    sock.close()
                    if sock in socketList:
                        socketList.remove(sock)
                    continue #Stop here
                
                #File Name and File Path Variables
                fileName = str(data)
                filePath = "./Server/"+str(data)

                #Check if file exists, otherwise send an error
                print("Asking for file: "+fileName)
                if not os.path.exists(filePath):
                    print("File Not Found! Sending error ...")
                    sock.send("Error404EOF") #File Not Found
                    print("Error Message Sent!")
                else:
                    print("Sending the file ...")
                    fileObj = open(filePath, 'rb')
                    while True:
                        fileChunk = fileObj.read(1000)
                        if not fileChunk:
                            break #End of File
                        #Send the FileChunk
                        sock.send(fileChunk)
                    #Done transferring
                    print("Transfer Complete!")
                    sock.send("EOF")

                
                #sock.sendall("EOF") #Signal we're done sending data!

    tcpSerSock.close()




#       MAIN
def main():
    #Get Input Port Number to listen on
    inputPort = getPortNumber()
    print('Listening for connection at Port '+str(inputPort)+'...')
    print("*****************************************************************************") #NewLine

    #Let's listen on it >:)
    startServer(inputPort)



if __name__ == "__main__":
    main()