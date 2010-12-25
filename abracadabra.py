import socket
import struct
import datetime
import time

ACAB_PORT = 50023
#ACAB_PORT = 43948
#ACAB_PORT = 44203
LOCALHOST = "127.0.0.1"

SCREEN_HEIGHT = 6
SCREEN_WIDTH = 16
SCREEN_DEPTH = 8
SCREEN_CHANNELS =3

FRAME_DEFAULT_DURATION = 500

class Color:
    def __init__(self, color):
        self.r, self.g, self.b = color
    
    def invert(self):
        self.r = 255-self.r
        self.g = 255-self.g
        self.b = 255-self.b
        return (self.r,self.g,self.b)
     
    def get_data(self):
        return "%02X%02X%02X"%(self.r,self.g,self.b)

class Frame:
    def __init__(self, duration = FRAME_DEFAULT_DURATION):
        #TODO check for bogus stuff here
        self.duration = duration
        self.content={}
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                self.content[(x,y)]=(0,0,0)
        
    def __unicode__(self):
        return "Duration: %s"%(self.duration)
    
    def __str__(self):
        return self.__unicode__()
    
    def get_content_for_stream(self):
        data = ""
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                r,g,b = self.content[(x,y)]
                data+= "%s%s%s"%(chr(r),chr(g),chr(b))
        return data
        
    
    def fill(self, color):
        for pos in self.content:
            self.content[pos]=color
    
    def invert(self):
        for pos in self.content:
            self.content[pos]=Color(self.content[pos]).invert()
        return self
        
class Stream:
    TITLE = "Untitled"
    AUTHOR = "Anonymous"
    
    #Overwrite this method with your own.
    def init_frame(self):
        pass
    
    #Overwrite this method with your own.
    def next_frame(self, last_frame):
        pass 
    
    def run(self):
        connection = Connection()
        #hello = connection.receive_zero_terminated()
        #print hello
        if connection.request(self.TITLE,self.AUTHOR):
            print "Starting Stream"
            frame = self.init_frame()
            try:
                while frame: 
                    connection.send_frame(frame)
                    frame = self.next_frame(frame)
            except KeyboardInterrupt:
                    pass
        print "Ending Stream"
        connection.close()
    
class Connection():
    def __init__(self, ip=LOCALHOST, port=ACAB_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.rx_buffer = ''
        self.tx_buffer = ''
        self.previous_duration = 0
        self.previous_sent = datetime.datetime.now()
        
    def request(self, title, author):
        MESSAGE_ALLOWED = 'MOAR'
        MESSAGE_DENIED = 'GTFO'
        
        self.writeln("TITLE=%s"%title)
        self.writeln("AUTHOR=%s"%author)
        self.writeln("DONE")
        answer = self.readln()
        return (answer == MESSAGE_ALLOWED)
        
    
    def send_frame(self, frame):
        HEADER = 0x00009000
        OP_DURATION = 0x0a
        OP_SET_SCREEN = 0x11
        MASK_NO_ACK = 0
        MASK_ACK = 0x00000100
        
        duration = frame.duration*750
        
        self.socket.send(struct.pack('!III', HEADER | OP_DURATION, 8+4, duration))
        d = struct.pack('!II', HEADER | OP_SET_SCREEN | MASK_ACK,
                            8 + SCREEN_HEIGHT * SCREEN_WIDTH * SCREEN_DEPTH / 8 * SCREEN_CHANNELS)
        d+= frame.get_content_for_stream()
        
        #delta = (self.previous_sent+datetime.timedelta(milliseconds=self.previous_duration))-datetime.datetime.now()
        #if delta >= datetime.timedelta(microseconds = 10):
        #    delay = float(delta.microseconds)/1000000
        #    print "sleeping %s"%delay
        #    time.sleep(delay)
        self.socket.send(d)
        
        #self.previous_sent = datetime.datetime.now()
        #self.previous_duration = frame.duration
        self.wait_for_ack()
    
    def writeln(self, data):
        print "--> %s"%data
        self.socket.send(data+"\n")
    
    def readln(self):
        # Read to the buffer
        self.rx_buffer += self.socket.recv(4096)
        #Parse the buffer
        nl_pos = self.rx_buffer.find('\n')
        if nl_pos != -1:
            self.rx_buffer = self.rx_buffer[:nl_pos+1]
            data = self.rx_buffer[:nl_pos]
            print "<-- %s"%data
            return data
        
    def wait_for_ack(self):
        # klingon ack
        ACK = '\xf8\xe2\xf8\xe6\xf8\xd6'
        response = ""
        while len(response) < len(ACK):
            response += self.socket.recv(len(ACK)-len(response))
            
            
    def close(self):
        self.socket.close()