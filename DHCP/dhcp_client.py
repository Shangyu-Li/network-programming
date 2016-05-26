import socket
import re
import textwrap
import struct

BUFSIZE = 700 		#4608

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

op = 		b'\x01'
htype = 	b'\x01'    # ethernet 10mb
hlen = 		b'\x06'
hops = 		b'\x00'
xid = 		b'\x39\x03\xF3\x26'	#0x3903f327
secs = 		b'\x00\x00'
flags = 	b'\x00\x00'
ciaddr = 	b'\x00\x00\x00\x00'  	#client ip
yiaddr = 	b'\x00\x00\x00\x00'	#server ip
siaddr = 	b'\x00\x00\x00\x00'
giaddr = 	b'\x00\x00\x00\x00'
chaddr1 = 	b'\x00\x05\x3C\x04'
chaddr2 = 	b'\x8D\x59\x00\x00'  #'\x8D\x59\x00\x00'
chaddr3 = 	b'\x00\x00\x00\x00'
chaddr4 = 	b'\x00\x00\x00\x00'
optext = 	b'\x00'*192
magic = 	b'\x63\x82\x53\x63'  #'\x63\x82\x53\x63'
op53 = 		b'\x35\x01\x01'			#53 1 1
op50 =		b'\x32\x04\xC0\xA8\x0A\x05'  # struct.pack('BBBBBB', 50, 4, 192, 168, 10, 5) #50 4 192.168.10.5
op55 = 		b'\x37\x04\x01\x03\x0F\x06' 	#55 4 1 3 15 6
end = 		b'\xFF'


text = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 \
+ chaddr3 + chaddr4 + optext + magic + op53 + op50 + op55 + end
text = text + (576 - len(text))*b'\x00'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(('10.0.0.10', 68))

while True:

	sock.sendto(text, ('255.255.255.255', 67))
	sock.settimeout(5)
	data, address = sock.recvfrom(BUFSIZE)
	dhcpfields=[1,1,1,1,4,2,2,4,4,4,4,4,4,4,4,192,4,"msg.rfind('\xff\xff')",1,None]
	text = data
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
	opt =      	messagesplit[17]
	end =       messagesplit[18]

	i = 0
	while i < len(opt) and opt[i] != 53:
	    i+=1
	msgtype = opt[i+2]
	if msgtype == 2 :           #offer
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
		i = 0
		print('\n\n\n\n')
		while i < len(opt) and opt[i] != 53:
			i+=1
		op = b'\x01'   #op = 2
		yiaddr = b'\x00\x00\x00\x00'	#yiaddr
		op53 = b'\x35\x01\x03'				#op53
		op50 = b'\x32\x04' + siaddr	#50 4 192.168.10.5
		op54 = b'\x36\x04' + siaddr          	#op54 192.168.10.5 server identifier
		text = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 \
		+ chaddr3 + chaddr4 + optext + magic + op53 + op50 + op54 + end
		text = text + (576 - len(text))*b'\x00'
	if msgtype == 5 or msgtype == 6:           #ack
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
		break