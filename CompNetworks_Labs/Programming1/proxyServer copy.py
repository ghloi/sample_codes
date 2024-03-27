import sys, os, time, select, socket

if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip expiration"\n[server_ip : It is the IP Address Of Proxy Server\n[expiration: It is the lifetime in seconds of a cached file')
	sys.exit(2)
	
# The proxy server is listening at 8888 
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET for IPv4 and SOCK_STREAM for TCP
tcpSerSock.setblocking(0) #Sets blocking to false (0), which means code won't yield for sockets (instant)
tcpSerSock.bind((sys.argv[1], 8888)) #Assuming sys.argv[1] is 'localhost'
tcpSerSock.listen(100) #Number inside listen() is maximum number of queued connections allowed

#List of Sockets to monitor
socketList = [tcpSerSock]
socketMap = {} #Sockets and their Target Sockets

#Let's start
while socketList:
	# Strat receiving data from the client
	print('Ready to serve...')
	readable, writable, exceptional = select.select(socketList, [], [])

	#GO THROUGH EACH READABLE FILE DESCRIPTOR
	for sock in readable:
		if sock is tcpSerSock:
			#Accept a new connection and add that new connection to list of inputs
			clientsock, addr = tcpSerSock.accept()
			print("***********************************************************")
			print("Received a connection from:", addr)
			socketList.append(clientsock)

			#Establish target socket
			data = clientsock.recv(4096) #Max 4096
			if data:
				#Let's compute the URL Stuff
			else:
				#NO INFO PROVIDED?? BYE
				clientsock.close()
				socketList.remove(clientsock)

		else:
			#Receive data from connected client
			data = sock.recv(4096) #Max 4096
			if data:
				# sock.sendall(data) #Send data back to client
				#Prepare Stuff
				decodedData = data.decode()
				lines = data.split('\r\n')
				target_line = lines[0].split()[1]
				target_server = target_line[1:] #Get rid of / at beginning
				target_params = "/"

				#Get rid of Trailing /'s
				while target_server[len(target_server)-1] == '/':
					target_server = target_server[:(len(target_server)-1)]

				#Get URL Arguments Properly
				splitted_url = target_server.split('/', 1)
				target_server = splitted_url[0]
				if len(splitted_url) > 1:
					target_params += splitted_url[1]
				
				getRequest = "GET "+target_params+" HTTP/1.1\r\nHost: "+target_server+"\r\n\r\n"

				print("Get Request based on Data:", getRequest)

				#Sending Connection
				print("=====================================")
				print("Sending to Server:", target_server)

				#Target Server connection request
				
				try:
					target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					target_socket.connect((target_server, 80))
					target_socket.sendall(getRequest.encode())

					#Response
					response = target_socket.recv(4096)
					print("RESPONSE:", response)
					sock.sendall(response)
					print("=====================================")
				except Exception as e:
					print("Error Encountered:", str(e))
				finally:
					#Close connection on no data
					socketList.remove(sock) #Remove client socket from list of sockets
					sock.close() #Close client socket
					target_socket.close()
			else:
				#Close connection on no data
				socketList.remove(sock) #Remove client socket from list of sockets
				sock.close() #Close client socket

	
tcpSerSock.close()