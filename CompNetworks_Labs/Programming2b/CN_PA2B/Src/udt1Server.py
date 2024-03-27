#   This program was made by Gregorio Loi on March 26, 2023
#   Intended use was for Programming Assignment 2 Submission for Computer Networks

import sys, os, select, time, socket

import udt, packet #HELPER MODULES
from timer import Timer #Helper Timer Class
from collections import deque
import pandas as pd
#       HELPER FUNCTIONS
def getInteger(displayMessage):
    inputInt = False
    while inputInt==False:
        try:
            inputInt = int(input(displayMessage))
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Integer Input: "+str(e))
            inputInt = False
    
    return inputInt

def getReceiverIP():
    inputIP = False
    while inputIP==False:
        try:
            inputIP = str(input("Provide Receiver IP: "))
            #Verification optional
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error IP Input: "+str(e))
            inputIP = False
    
    return inputIP

def getWindowSize():
    winSize = False
    while winSize==False:
        try:
            winSize = int(input("Enter Window Size (N): #"))
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Window Size (N) Input: "+str(e))
            winSize = False
    
    return winSize

#       HELPER FUNCTIONS
def getProtocol():
    inputProtocol = False
    while inputProtocol==False:
        try:
            inputProtocol = int(input("Choose a protocol:\n1. [SnW]\n2. [GBN]\nEnter your choice (1-2): "))
            if (inputProtocol != 1) and (inputProtocol != 2):
                print("Invalid selection! Choose between 1 [SnW] or 2 [GBN].")
                inputProtocol = False
        except Exception as e:
            #Error occured, display error and retry (While Loop)
            print("Error Protocol Input: "+str(e))
            inputProtocol = False
    if inputProtocol == 1:
        return "SnW"
    return "GBN"

def send_snw(inputPort, clientIP, clientPort, timeout):
    #Important Variables
    reportDictionary={'Protocol':[], 'Start Time':[], 'End Time':[], 'Lost Packets':[], 'Duration':[]}
    clientAddress = (clientIP, clientPort)
    bufferSize = 999 #Save 1 byte for sequence number
    seqNum = 0 #Start at 0
    fileName = 'assign1.pdf'
    DEFAULT_FILE = open(fileName, 'rb') #Default File hardcoded
    fileSize = os.path.getsize(fileName)
    timerObj = Timer(timeout)
    reportStart=time.time()
    retransmittedP=0
    #Create our UDP Socket first for Server to listen on
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', inputPort))
    reportDictionary["Protocol"].append('SnW')
    reportDictionary['Start Time'].append(reportStart)
    #Go through entire file in bufferSize increments
    for i in range(0, fileSize, bufferSize):
        #Get a chunk of data from file
        dataChunk = DEFAULT_FILE.read(bufferSize)

        #Create a packet
        dataPacket = packet.make(seqNum, dataChunk)

        ackReceived = False
        while not ackReceived:
            #Send it
            udt.send(dataPacket, sock, clientAddress)

            #NOW WE TIMEOUT AND RECEIVE
            timerObj.start() #Start the timer
            while not timerObj.timeout():
                #Iteratively try to get an ACK signal
                try:
                    sock.settimeout(0.1) #VERY SHORT TIMEOUT
                    rcvPacket, rcvAddress = udt.recv(sock)
                    rcvSeqNum, rcvData = packet.extract(rcvPacket)
                    if rcvSeqNum == seqNum:
                        #We received our seq num!! Yay
                        ackReceived = True #To break while loop
                        seqNum = 1 - seqNum #Sets 1 to 0, 0 to 1
                        break
                except Exception as e:
                    #Ignore this branch of code, only used to catch socket timing out every 0.1 seconds
                    pass
            
            #Now, check if Acknowledgement was received (Packet sent successfully)
            if not ackReceived:
                print("Acknowledgement not received - Retransmitting packet!")
                retransmittedP+=1
            timerObj.stop() #For next time use
    newPacket=packet.make(-1, 'EOF'.encode('utf-8'))
    sock.sendto(newPacket, clientAddress)
    print('File Transfer complete! Closing socket.')
    sock.close()
    reportEndTime=time.time()
    reportDictionary['End Time'].append(reportEndTime)
    reportDictionary['Duration'].append(reportEndTime-reportStart)
    reportDictionary['Lost Packets'].append(retransmittedP)
    df=pd.DataFrame.from_dict(reportDictionary)
    df.to_csv('Report SnW.csv')

def send_gbn(inputPort, clientIP, clientPort, windowSize, timeout):
    #Important Variables
    reportDictionary={'Protocol':[], 'Start Time':[], 'End Time':[], 'Lost Packets':[], 'Duration':[]}
    clientAddress = (clientIP, clientPort)
    bufferSize = 999 #Save 1 byte for sequence number
    seqNum = 0 #Start at 0
    fileName = 'assign1.pdf' #File has to be in current directory
    DEFAULT_FILE = open(fileName, 'rb') #Default File hardcoded
    fileSize = os.path.getsize(fileName)
    packets = [] #Array to hold all the packets
    totalPackets = 0
    timerObj = Timer(timeout)

    #Create our UDP Socket first for Server to listen on
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', inputPort))
    reportStart=time.time()
    retransmittedP=0
    reportDictionary['Protocol'].append('GbN')
    reportDictionary['Start Time'].append(reportStart)
    #Let's create packets from our file and append it to packets array
    seqNum = 0 #Start at 0
    
    for i in range(0, fileSize, bufferSize):
        dataChunk = DEFAULT_FILE.read(bufferSize) #Chunk of data read
        dataPacket = packet.make(seqNum, dataChunk) #Byte SeqNum + Bytes DataChunk
        packets.append(dataPacket) #Add it to our packets array

        #Sequence Number Assignment - Our general goal is 0, 1, 2, ..., N
        seqNum += 1 #For next packet's sequence number
        totalPackets += 1 #For keeping track of packets
    
    #Iterate
    currentPacket = 0
    window = deque() #Double ended queue for processing windows
    unackedPkts = []

    #Initially, we need to populate our window from empty to size N
    while len(window) < windowSize and currentPacket < totalPackets:
        window.append(packets[currentPacket]) #Get next packet and add it to window
        currentPacket += 1

    #Then, we need to initially transmit every packet in our window
    for pkt in window:
        tempN, tempData=packet.extract(pkt)
        print(f'Sending packet Sequence #{tempN}')
        udt.send(pkt, sock, clientAddress)
    
    while window:
        #Repopulate our window to make sure its holding N packets when possible
        while len(window) < windowSize and currentPacket < totalPackets:
            newPkt = packets[currentPacket]
            window.append(newPkt) #Get next packet and add it to window
            currentPacket += 1
            #SEND THE NEW ADDITION TO OUR WINDOW!
            tempN, tempData=packet.extract(newPkt)
            print(f'Sending packet Sequence #{tempN}')
            udt.send(newPkt, sock, clientAddress)

        
        #Check for ack on window[0]
        timerObj.start() #Start the timer
        ackReceived = False
        while not timerObj.timeout():
            #Iteratively try to get an ACK signal
            try:
                sock.settimeout(0.1) #VERY SHORT TIMEOUT
                rcvPacket, rcvAddress = udt.recv(sock)
                rcvSeqNum, rcvData = packet.extract(rcvPacket)
                firstPacket = window[0]
                currentSeqNum, currentData = packet.extract(firstPacket)
                if rcvSeqNum == currentSeqNum:
                    #We received our seq num!! Yay
                    print(f'Acknowledged Sequence #{rcvSeqNum}')
                    ackReceived = True #To break while loop
                    break
            except Exception as e:
                #Ignore this branch of code, only used to catch socket timing out every 0.1 seconds
                pass
        timerObj.stop() #For reuse
        #Do certain actions depending on if you received an ack or not
        if not ackReceived: #Not received-Retransmit entire window
            while(rcvSeqNum>currentSeqNum):
                try:
                    window.popleft()
                    currentSeqNum+=1
                except:
                    window.append(packets[rcvSeqNum])
                    break

            for pkt in window:
                retransmittedP+=1
                tempN, tempData=packet.extract(pkt)
                print(f'Sending packet Sequence #{tempN}')
                udt.send(pkt, sock, clientAddress)
        else: #Received - Pop window[0]
            window.popleft() #Pops window[0]
    newPacket=packet.make(-1, 'EOF'.encode('utf-8'))
    sock.sendto(newPacket, clientAddress)
     #END OF FILE TRANSMISSION DONE
    print('File Transfer complete! Closing socket.')
    sock.close()
    reportEndtime=time.time()
    reportDictionary['End Time'].append(reportEndtime)
    reportDictionary['Duration'].append(reportStart - reportEndtime)
    reportDictionary['Lost Packets'].append(retransmittedP)
    df=pd.DataFrame.from_dict(reportDictionary)
    df.to_csv('GbN Report.csv')




        

        
        

    

    

    



#       MAIN
def main():
    #Get Input Port Number for server listening on
    inputPort = getInteger("Provide Port for incoming connections: #") #Integer Port Number

    #Get Input IP Address to send file to
    clientIP = getReceiverIP()
    clientPort = getInteger("Provide Receiver Port: #") #Integer Port Number

    #Get Input Protocol for sending file
    inputProtocol = getProtocol() #String "SnW" or "GBN"

    #Timeout/Lifetime of a Packet in seconds
    timeout = getInteger("Enter timeout for packets in seconds: ")

    #If GBN, get Window Size!
    if inputProtocol == "GBN":
        windowSize = getWindowSize()        

    #Print Messages for Debug
    print('Sending file to '+str(clientIP)+':'+str(clientPort)+'...')
    print('Using Protocol: '+str(inputProtocol))
    if inputProtocol == "GBN":
        print('Window Size (N) is: '+str(windowSize))
    print('Packet timeout in seconds is: '+str(timeout))
    print("*****************************************************************************") #NewLine

    # #Let's listen on it >:)
    # startServer(inputPort)
    if inputProtocol == "GBN":
        print("Sending with GBN...")
        send_gbn(inputPort, clientIP, clientPort, windowSize, timeout)
    else:
        print("Sending with SnW...")
        send_snw(inputPort, clientIP, clientPort, timeout)



if __name__ == "__main__":
    main()