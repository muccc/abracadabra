import socket
import struct
import datetime
import time
import types

ACAB_PORT = 50023  #spooler
#ACAB_PORT = 43948
#ACAB_PORT = 44203
ACAB_IP = "81.163.62.30"

SCREEN_HEIGHT = 6
SCREEN_WIDTH = 16
SCREEN_DEPTH = 8
SCREEN_CHANNELS =3

FRAME_DEFAULT_DURATION = 500

class Mask:
    def __init__(self, x=None, y=None):
        self.fields = []
        if not (x is None or y is None):
            self.add(x,y)
    
    def all(self):
        self = Mask().invert()
        return self
    
    def invert(self):
        new_fields = []
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                if not (x,y) in self.fields:
                    new_fields.append((x,y))
        self.fields = new_fields
        return self
    
    def add(self, x,y):
        if (x > SCREEN_WIDTH-1 or
            x < 0 or
            y > SCREEN_HEIGHT-1 or
            y < 0):
            raise IndexError
        
        if not (x,y) in self.fields:
            self.fields.append((x,y))
        return self
    
    def add_mask(self, other):
        for pos in other.fields:
            self.add(pos)
        return self
    
    def remove(self, x,y):
        if (x > SCREEN_WIDTH-1 or
            x < 0 or
            y > SCREEN_HEIGHT-1 or
            y < 0):
            raise IndexError
        
        if (x,y) in self.fields:
            self.fields.remove((x,y))
        return self
    
    def remove_mask(self, other):
        for pos in other.fields:
            self.remove(pos)
        return self
        
    def add_row(self, y):
        self.add([(x,y) for x in range(SCREEN_WIDTH)])
        return self

    def add_col(self, x):
        self.add([(x,y) for y in range(SCREEN_HEIGHT)])
        return self
    
    def add_square(self, x1,y1, x2,y2):
        self.add_area(range(x1,x2),range(y1,y2))
        return self
        
    def add_area(self, lx, ly):
        print lx
        print ly
        for x in lx:
            for y in ly:
                self.add(x,y)
        print self.fields
        return self
    
class Color:
    
    @staticmethod
    def avg(list):
        len = len(list)
        tr=tg=tb=0

        for c in list:
            tr+=c.r
            tg+=c.g
            tb+=c.b
        
        return Color(tr/len,tg/len,tb/len)
        
    
    def __init__(self, r=0,g=0,b=0, name=None):
        if (type(r) != types.IntType or 
            type(g) != types.IntType or
            type(b) != types.IntType):
            raise TypeError
        
        
        if not name:
            self.r = max(min(r,255),0)
            self.g = max(min(g,255),0)
            self.b = max(min(b,255),0)
        else:
            raise LookupError #TODO implement real lookup
        
    def invert(self):
        return Color(255-self.r, 255-self.g, 255-self.b)
     
    def add(self,other):
        return Color(self.r+other.r, self.g+other.g, self.b+other.b)
    
    def sub(self,other):
        return Color(self.r-other.r, self.g-other.g, self.b-other.b)
    
    def avg_add(self,other):
        return Color.avg((self,other))
    
    
    def _to_data(self):
        return "%s%s%s"%(chr(self.r),chr(self.g),chr(self.b))

class Frame:
    def __init__(self, duration = FRAME_DEFAULT_DURATION, color=Color(), clone=None):
        self.content={}
        self.duration = duration
        
        if clone:
            self.duration=clone.duration
            for key in clone.content:
                self.content[key]=clone.content[key]
            
        else:
            for x in range(SCREEN_WIDTH):
                for y in range(SCREEN_HEIGHT):
                    self.content[(x,y)]=color
        
    def __unicode__(self):
        return "Duration: %s"%(self.duration)
    
    def __str__(self):
        return self.__unicode__()
    
    def _get_content_for_stream(self):
        data = ""
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
            
                #r,g,b = self.content[(x,y)]
                data+= self.content[(x,y)]._to_data()
        return data
    
    def set(self, mask = Mask().all(), color=Color(255,255,255)):    
        print mask.fields
        for pos in mask.fields:
            self.content[pos]=color
        return self
    
    def invert(self):
        for pos in self.content:
            self.content[pos]=self.content[pos].invert()
        return self
    
    def shift(self,dx=0,dy=0):
        new_content = {}
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                new_content[(x,y)]=self.content[((x-dx)%SCREEN_WIDTH,(y-dy)%SCREEN_HEIGHT)]
        
        self.content= new_content
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
    
    def run(self,):
        connection = Connection()
        #hello = connection.receive_zero_terminated()
        #print hello
        if  connection.request(self.TITLE,self.AUTHOR):
            print "Starting Stream"
            frame = self.init_frame()
            print frame
            try:
                while frame: 
                    print "bla"
                    connection.send_frame(frame)
                    frame = self.next_frame(frame)
            except KeyboardInterrupt:
                    pass
        print "Ending Stream"
        connection.close()
    
class Connection():
    def __init__(self, ip=ACAB_IP, port=ACAB_PORT):
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
        d+= frame._get_content_for_stream()
        
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