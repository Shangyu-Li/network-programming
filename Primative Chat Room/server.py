# Tcp Chat server
 
import socket, select
 
#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message.encode('ascii', 'ignore'))
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)
                del ONLINE_LIST[socket]
 
def login(sock):
    suc = 0
    while not suc:
        account = sock.recv(RECV_BUFFER).decode('ascii', 'ignore')
        password = sock.recv(RECV_BUFFER).decode('ascii', 'ignore')
        match = [acc for acc in ACCOUNT_LIST if account == acc[0] and password == acc[1]]
        if match:
            suc = 1
            ONLINE_LIST[sock] = account
            sock.send(str(1).encode('ascii', 'ignore'))
            return match
        sock.send(str(0).encode('ascii'))

def talkto(ins, sock):
    msg = ''
    try:
        name = ins[0]
        msg +=  ONLINE_LIST[sock] + ' send : ' + ' '.join(ins[1:]) + '\n'
        return msg
    except:
        print('wrong send request')

def dialog(peername, sock):
    msg = ''
    peersc = [sc for sc in ONLINE_LIST if ONLINE_LIST[sc] == peername]
    name = ONLINE_LIST[sock]
    if isinstance(peersc, list) and peersc:     peersc = peersc[0]
    if not peername in dict(ACCOUNT_LIST):
        msg += peername + ' is not an account\n'
        return msg
    if not peersc:
        msg += peername + ' is offline\n'
        return msg
    if name in [n for sub in CONVERSATION for n in sub]:
        msg += 'You are having a conversation\n'
        return msg
    if name in [n for sub in CONVERSATION for n in sub]:
        msg += name + ' is having a conversation\n'
        return msg
    if not name in [n for sub in CONVERSATION for n in sub] \
    and not peername in [n for sub in CONVERSATION for n in sub]:
        CONVERSATION.append((name, sock, peername, peersc))

def friend_manipulate(ins, sock):
    msg = ''
    try:
        i = ins[0]
        if i == 'list':
            for fri in  FRIEND_LIST[ONLINE_LIST[sock]]:
                if fri in ONLINE_LIST.values(): 
                    msg += fri + ' online\n'
                else:   msg += fri + ' offline\n'
            if not msg:
                msg += 'EMPTY\n'
        else:
            try:
                name = ins[1]
                if i == 'add' and name in [k for j in ACCOUNT_LIST for k in j]:
                    FRIEND_LIST[ONLINE_LIST[sock]].append(name)
                    msg += name + ' added into the friend list\n'
                elif i == 'rm' and name in [k for j in ACCOUNT_LIST for k in j]:
                    FRIEND_LIST[ONLINE_LIST[sock]].remove(name)
                    msg += name + ' removed from the friend list\n'
                elif i == 'add' or i == 'rm' and not name in [k for j in ACCOUNT_LIST for k in j]:
                    msg += name + ' not an account\n'
                else:
                    msg += 'friend --add|--rm --name\n'
            except:
                msg += 'friend --add|--rm --name\n'
    except:
        msg += 'friend --list\n'
    return msg

def sendfile(ins, sock):
    msg = ''
    try:
        peername = ins[0]
        peersc = [sc for sc in ONLINE_LIST if ONLINE_LIST[sc] == peername]
        name = ONLINE_LIST[sock]
        if isinstance(peersc, list) and peersc:     peersc = peersc[0]
        if not peername in dict(ACCOUNT_LIST):
            msg += peername + ' is not an account\n'
        if not peersc:
            msg += peername + ' is offline\n'
        else:
            request = '\n' + name + ' want to send file : ' + ins[1] + ', Yes or No\n'
            peersc.sendall(request.encode('ascii'))
            per = peersc.recv(1024).decode('ascii')
            sock.sendall(per.encode('ascii'))
            if not per =='Yes' and not per == 'Y' and not per == 'yes':
                msg += peername + ' deny\n'
            else:
                l = ''
                while not l == 'None'.encode('ascii') and not l[-4:] == 'None'.encode('ascii'):
                    l = sock.recv(10)
                    peersc.sendall(l)
                msg = ins[1] + ' done\n'
    except:
        msg += 'sendfile --name --filename\n'
    return msg


if __name__ == "__main__":
     
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    OUT_LIST = []
    msg = {}
    CONVERSATION = []
    OFFLINE_msg = {}
    ACCOUNT_LIST = (('Mary', '1111'), ('John', '2222'), ('Mike', '3333'))
    ONLINE_LIST = {}
    FRIEND_LIST = {'Mary':['John', 'Mike'], 'John':['John'], 'Mike':['Mary']}

    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print ("Chat server started on port " + str(PORT))
 
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,OUT_LIST,[])
 
        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                info = login(sockfd)
                print ("Client {} from ({}) connected".format(info[0][0] ,addr))
                name = ONLINE_LIST[sockfd]
                if name in OFFLINE_msg:
                    msg[sockfd] = ''.join(OFFLINE_msg[name])
                    if not sockfd in OUT_LIST:
                        OUT_LIST.append(sockfd)
                 
                broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
             
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                data = sock.recv(RECV_BUFFER).decode('ascii', 'ignore')
                if data:
                    data = data.split()
                    ins = data[0]
                    redata = ''
                    selconv = [i for i in CONVERSATION if i[0] == ONLINE_LIST[sock] or i[2] == ONLINE_LIST[sock]]                  
                    # broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)
                    if ins == 'friend':

                        redata = friend_manipulate(data[1:], sock)
                    elif ins == 'send':
                        try:
                            recipient = data[1]
                            redata = talkto(data[1:], sock)
                            if recipient in dict(ACCOUNT_LIST):
                                sock = [sc for sc in ONLINE_LIST if ONLINE_LIST[sc] == recipient]
                                if isinstance(sock, list) and sock:    sock = sock[0]
                                if not sock and not recipient in OFFLINE_msg:
                                    OFFLINE_msg[recipient] = [redata]
                                    break;
                                elif not sock and recipient in OFFLINE_msg:
                                    OFFLINE_msg[recipient].append(redata)
                                    break;
                            else:
                                redata = recipient + ' not in account\n'
                        except:
                            redata = 'send --name --message\n'
                    elif ins == 'talk':
                        try:
                            if data[1] == 'end':
                                rm = [ k for k in CONVERSATION if k[1] == sock or k[3] == sock][0]
                                redata = 'talk end\n'
                                if sock == rm[1]:
                                    msg[rm[3]] = 'talk end\n'
                                    if not rm[3] in OUT_LIST: OUT_LIST.append(rm[3])
                                else:
                                    msg[rm[1]] = 'talk end\n'
                                    if not rm[1] in OUT_LIST: OUT_LIST.append(rm[1])
                                CONVERSATION.remove(rm)
                                break
                            else:
                                redata = dialog(data[1], sock)
                                if not redata:
                                    redata = 'having a conversation with ' + data[1] + '\n'
                                    peersc = [i for i in ONLINE_LIST if ONLINE_LIST[i] == data[1]]
                                    if peersc:  peersc = peersc[0]
                                    msg[peersc] = '\nhaving a conversation with ' + ONLINE_LIST[sock] + '\n'
                                    if not peersc in OUT_LIST: OUT_LIST.append(peersc)
                        except:
                            redata = 'talk --name'

                    elif selconv:
                        if selconv[0][1] == sock:
                            sock = selconv[0][3]
                        else:
                            sock = selconv[0][1]
                        redata = ' '.join(data) + '\n'

                    # elif ins == 'logoff':
                    #     sock.close()
                    elif ins == 'sendfile':
                        redata = sendfile(data[1:], sock)
                    elif ins == 'logout':
                        sock.close()
                        if sock in CONNECTION_LIST:
                            CONNECTION_LIST.remove(sock)
                        if sock in OUT_LIST:
                            OUT_LIST.remove(sock)
                        if sock in ONLINE_LIST:
                            del ONLINE_LIST[sock]
                        break
                    else:
                        redata = 'unknown instruction\n'
                    if redata:
                        msg[sock] = '\n' + redata 
                    if not sock in OUT_LIST: OUT_LIST.append(sock)
                else:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print ("Client (%s, %s) is offline" % addr)
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    del ONLINE_LIST[socket]
                # continue
        for sock in write_sockets:
            # output events always mean we can send some data
            tosend = msg[sock]
            if tosend:
                sock.sendall(tosend.encode('ascii', 'ignore'))
                print ("bytes to %s" % str(sock.getsockname()))
                # remember data still to be sent, if any
                # tosend = tosend[nsent:]
            # if tosend: 
            #     print "%d bytes remain for %s" % (len(tosend), adrs[sock])
            #     msg[sock] = tosend
            # else:
                try: del msg[sock]
                except KeyError: pass
                OUT_LIST.remove(sock)
                print ("No data currently remain for", sock.getsockname())
     
    server_socket.close()