import sys, os, time, select, socket

# Helper Functions

def transformURL(urlName):
	#Full Name
	urlName.replace('/', '-')
	urlName.replace('.', '_')

	#Char Filtering
	chars_i_want = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-') #Can prob be easier with regex
	final_string = ''.join(c for c in urlName if c in chars_i_want)

	return final_string


if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip expiration"\n[server_ip : It is the IP Address Of Proxy Server\n[expiration: It is the lifetime in seconds of a cached file')
	sys.exit(2)
proxyExpirationTime = 200 #SECONDS
if len(sys.argv) > 2:
	#Get time for proxy file expiration
	if isinstance(sys.argv[2], (int, float, complex)): #It's a number
		proxyExpirationTime = sys.argv[2]

# The proxy server is listening at 8888 
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET for IPv4 and SOCK_STREAM for TCP
tcpSerSock.setblocking(0) #Sets blocking to false (0), which means code won't yield for sockets (instant)
tcpSerSock.bind((sys.argv[1], 8888)) #Assuming sys.argv[1] is 'localhost'
tcpSerSock.listen(100) #Number inside listen() is maximum number of queued connections allowed

#List of Sockets to monitor
socketList = [tcpSerSock]
socketMap = {} #Sockets and their Target Sockets
clientSockets = [] #ClientSockets
targetNames = {} #Target Sockets and their file names based on URL
existingProxies = []

#Let's start
while socketList:
	# Strat receiving data from the client
	readable, writable, exceptional = select.select(socketList, [], [])

	#GO THROUGH EACH READABLE FILE DESCRIPTOR
	for sock in readable:
		if sock is tcpSerSock:
			#Accept a new connection and add that new connection to list of inputs
			clientsock, addr = tcpSerSock.accept()
			print("***********************************************************")
			print("***********************************************************")
			print("Received a connection from:", addr)
			socketList.append(clientsock)
			clientSockets.append(clientsock)
		else:
			#Receive data
			data = sock.recv(4096)
			if not data:
				#Close connections one of the sockets disconnected
				#Other Socket Removal
				if sock in clientSockets:
					print("Client Socket has no Data to give.")
				else:
					print("Target Socket has no Data to give.")

				#Check if sock has another socket paired with it, so we can disconnect it too
				if sock in socketMap:
					other_socket = socketMap[sock]
					#print("Other socket removal")
					other_socket.close()
					if other_socket in socketList:
						socketList.remove(other_socket)
					if other_socket in socketMap:
						del socketMap[other_socket]
					if other_socket in clientSockets:
						clientSockets.remove(other_socket)

				#Current Socket Removal
				#print("Current socket removal")
				sock.close()
				if sock in socketList:
					socketList.remove(sock)
				if sock in socketMap:
					del socketMap[sock]
				if sock in clientSockets:
					clientSockets.remove(sock)
					
				continue #Stop here
			if sock in clientSockets and (not (sock in socketMap)):

				#Its a client! Initial Process data [[Set up Target Socket]]
				print("Client Socket initializing Data, forming Request to send!")

				#CHECK PROXY CACHE FIRST BEFORE CONTINUING :)
				if not os.path.exists("./Cache"):
					os.makedirs("./Cache")

				


				#Let's compute the URL Stuff
				lines = data.split('\r\n')
				target_line = lines[0].split()[1]
				target_server = target_line[1:] #Get rid of / at beginning
				target_params = "/"

				if not target_server:
					continue #Stop here
				#Get rid of Trailing /'s
				while target_server[len(target_server)-1] == '/':
					target_server = target_server[:(len(target_server)-1)]

				#Get URL Arguments Properly
				splitted_url = target_server.split('/', 1)
				target_server = splitted_url[0]
				if len(splitted_url) > 1:
					target_params += splitted_url[1]
				
				#FINAL SERVER NAME :D
				final_name = transformURL(target_server+target_params)

				#PROXY CHECK FINAL SERVER NAME
				filePath = "./Cache/"+final_name+".txt"
				if os.path.exists(filePath):
					#Store It
					existingProxies.append(filePath)
					#Is it out of date?
					lastModified = time.time() - os.path.getmtime(filePath)
					if lastModified >=  proxyExpirationTime:
						#RENEW PROXY FILE!!
						os.remove(filePath)
						existingProxies.remove(filePath)
					else:
						#OPEN PROXY FILE!
						print("Opening Stored Proxy File!")
						proxFile = open(filePath, "r+") #Open in read and write mode
						proxContents = proxFile.readlines()
						for proxLine in range(len(proxContents)):
							sock.send(proxContents[proxLine].encode()) #Send line by line!
						proxFile.close()
						continue #Stop here

				#Check if final_name is in proxy Cache folder. If it is, load that instead and return >:)


				getRequest = "GET "+target_params+" HTTP/1.1\r\nHost: "+target_server+"\r\n\r\n"
				print("\r\nPROCESSING CLIENT DATA \r\n"+ getRequest)
				try:
					target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					target_socket.connect((target_server, 80))
				except Exception as e:
					#print("EXCEPTION REMOVALS")
					print("Error Initializing Client Socket: "+str(e))
					target_socket.close()
					sock.close()
					socketList.remove(sock)
					clientSockets.remove(sock)
				else:
					#No error occured, continue :)
					socketMap[sock] = target_socket
					socketMap[target_socket] = sock
					socketList.append(target_socket)
					targetNames[target_socket] = final_name

					#SEND INITIAL GET REQUEST :D
					target_socket.sendall(getRequest.encode())
			elif not (sock in clientSockets):
				#It's a target socket
				print("Target Socket responding with Data!")
				socketMap[sock].sendall(data) #Send to client :)
				if sock in targetNames:
					#PROXY CHECK FINAL SERVER NAME
					targSockName = targetNames[sock]
					targPath = "./Cache/"+targSockName+".txt"

					#Create File if not Exist and Append
					appendOpen = open(targPath, 'a')
					appendOpen.write(data.decode())
					appendOpen.close()

					#Check if we are done
					if not sock in readable:
						#We are done! No more data to transmit.
						existingProxies.append(targPath)

					print("This Socket has a Target Name: "+targetNames[sock])
				#print("RECEIVED================ \r\n"+ data.decode())		
				


tcpSerSock.close()