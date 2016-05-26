# telnet program example
import socket, select, string, sys, os
from getpass import getpass
 
def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

def login(sock):
    suc = 0
    while not suc:
        print('account :', end='')
        sys.stdout.flush()
        account = sys.stdin.readline().splitlines()
        sock.send(account[0].encode('ascii', 'ignore'))
        password = getpass()
        sock.send(password.encode('ascii', 'ignore'))
        right = sock.recv(4096).decode('ascii', 'ignore')
        suc = int(right[0])
    print('Log in successful')
    return right[1:]
 
#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print ('Usage : python telnet.py hostname port')
        sys.exit()
     
    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print ('Unable to connect')
        sys.exit()
     
    print ('Connected to remote host. Start sending messages')
    offline_msg = login(s)
    if offline_msg:
        print(offline_msg, end = '')
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            # bit = 1
            if sock == s:
                data = sock.recv(4096).decode('ascii', 'ignore')
                if not data :
                    print ('\nDisconnected from chat server')
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    prompt()
                if 'want to send file : ' in data:
                    reply = sys.stdin.readline().split()[0]
                    sock.sendall(reply.encode('ascii'))
                    if reply == 'Yes' or reply == 'Y' or reply == 'yes':
                        start = data.find('want to') + len('want to send file : ')
                        end = data.find(',')
                        filename = 'copy' + data[start:end]
                        f = open(filename, 'wb')
                        l = ''
                        while True:
                            l = sock.recv(10)
                            if l == 'None'.encode('ascii') or l[-4:] == 'None'.encode('ascii'):
                                break
                            f.write(l)
                        print('end of ', filename, ' transmitted\n')
                        f.close()
             
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg.encode('ascii', 'ignore'))
                prompt()
                msg = msg.split()
                if msg[0] == 'sendfile':
                    per = s.recv(1024).decode('ascii')
                    if per == 'Yes' or per == 'Y' or per == 'yes':
                        filesize = os.stat(msg[2]).st_size
                        f = open(msg[2], 'rb')
                        sent = 0
                        while True:
                            l = f.read(10)
                            if not l:
                                break
                            s.sendall(l)
                            sent += len(l)
                            print(sent/filesize*100, '\% of ', msg[2], ' transmitted....\n')
                        s.sendall('None'.encode('ascii'))
                        print('end of ', msg[2], ' transmitted\n')
                        f.close()
                    else:                        
                        print(per)