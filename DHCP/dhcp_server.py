import socket
import re
import binascii
import textwrap
import struct

BUFSIZE = 700


def todec(num):
    show = ''
    for i in num:
        show += str(i) + '.'
    show = show[0:len(show)-1]
    return show

def slicendice(msg,slices):  #generator for each of the dhcp fields
    for x in slices:
        if str(type(x)) == "<class 'str'>": 
            x =msg.rfind(b'\xff') #really dirty, deals with variable length options
        yield msg[:x]
        msg = msg[x:]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('10.0.0.10', 67))
print('Listening for datagrams at {}'.format(sock.getsockname()))
while True:
    sock.settimeout(5)
    data, address = sock.recvfrom(BUFSIZE)
    text = data

    dhcpfields=[1,1,1,1,4,2,2,4,4,4,4,4,4,4,4,192,4,"msg.rfind('\xff\xff')",1,None]
    messagesplit=[x for x in slicendice(text,dhcpfields)]
    print (address)
    op =        messagesplit[0]
    htype =     messagesplit[1]
    hlen =      messagesplit[2]
    hops =      messagesplit[3]
    xid =       messagesplit[4]
    secs =      messagesplit[5]
    flags =     messagesplit[6]
    ciaddr =    messagesplit[7]
    yiaddr =    messagesplit[8]
    siaddr =    messagesplit[9]
    giaddr =    messagesplit[10]
    chaddr1 =   messagesplit[11]
    chaddr2 =   messagesplit[12]
    chaddr3 =   messagesplit[13]
    chaddr4 =   messagesplit[14]
    optext =    messagesplit[15]
    magic =     messagesplit[16]
    opt =       messagesplit[17]
    end =       messagesplit[18]

    print('OP : ', todec(op), ' HTYPE : ', todec(htype), ' HLEN : ', todec(hlen), ' HOPS : ', todec(hops))
    print('XID : ', todec(xid), ' SECS : ', todec(secs), ' FLAGS : ', todec(flags))
    print('CIADDR : ', todec(ciaddr), ' YIADDR : ', todec(yiaddr))
    print('SIADDR : ', todec(siaddr), ' GIADDR : ', todec(giaddr))
    print('CHADDR1 : ', todec(chaddr1), ' CHADDR2 : ', todec(chaddr2))
    print('CHADDR3 : ', todec(chaddr3), ' CHADDR4 : ', todec(chaddr4))
    print('MAGIC COOKIE : ', todec(magic))
    print('DHCP Options : ')
    i = 0
    while i < len(opt):
        op = opt[i]
        i += 1
        length = opt[i]
        i += 1
        j = 0
        print('OP', op, ', LEN : ', length, ' , ', end = '')
        while j < length :
            print(opt[i+j], ', ', end = '')
            j += 1
        i = j+i
        print();
    print('\n\n\n\n')

    op = b'\x02'                  #op = 2
    flags = b'\x00\x00'                  #flags = 0
    yia = address[0].split('.')
    ip1 = struct.pack('B', int(yia[0]))
    ip2 = struct.pack('B', int(yia[1]))
    ip3 = struct.pack('B', int(yia[2]))
    ip4 = struct.pack('B', int(yia[3]))
    yiaddr = ip1 + ip2 + ip3 + ip4
    op1 = b'\x01\x04\xff\xff\xff\x00'    #op1 255.255.255.0
    op51 = b'\x33\x04\x00\x01\x51\x80'   #op51 86400s
    op6 = b'\x06\x0C\x09\x07\x0A\x0F\x09\x07\x0A\x10\x09\x07\x0A\x12'           #  9.        7.        10.       15       , 9.       7.        10.        16 

    i = 0
    while i < len(opt) and opt[i] != 53:   i+=1
    mestype = opt[i+2]
    if mestype == 1 :           #discover

        sia = '192.168.10.5'.split('.')
        siaddr = struct.pack('B', int(sia[0])) + struct.pack('B', int(sia[1])) + struct.pack('B', int(sia[2])) + struct.pack('B', int(sia[3]))
        #sia
        op54 = b'\x36\x04' + siaddr          #op54 192.168.10.5 server identifier
        op3 = b'\x03\x04' + siaddr           #op3 192.168.10,5 router
        op53 = b'\x35\x01\x02'              #op53
        text = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 \
        + chaddr3 + chaddr4 + optext + magic + op53 + op1 + op3 + op51 + op54 + op6 + end
        text = text + (576 - len(text))*b'\x00'
        
    if mestype == 3 :           #request
        op53 = b'\x35\x01\x05'              #op53  ack
        op54 = b'\x36\x04' + siaddr          #op54 192.168.10.5 server identifier
        op3 = b'\x03\x04' + siaddr           #op3 192.168.10,5 router
        text = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 \
        + chaddr3 + chaddr4 + optext + magic + op53 + op1 + op3 + op51 + op54 + op6 + end
        text = text + (576 - len(text))*b'\x00'

    sock.sendto(text, ('255.255.255.255', 68))

