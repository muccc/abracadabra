import sys
import threading
import gobject
gobject.threads_init()
import gst 

import struct
import Queue
RGB_UNPACKER = struct.Struct("BBBB")
COLS = 16
ROWS = 6

from abracadabra import Frame, Color, Stream, Mask

frame_queue = Queue.Queue(1)
frame_length = 40 #default 25fps

def callback(fakesink, buffer, pad, data=None): 
    data = []
    for i in range(0, len(buffer), 4):
        data.append( RGB_UNPACKER.unpack(buffer[i:i+4]) )

    try:
        frame_queue.put_nowait( data )
    except Queue.Full:
        pass
    return True 

import sys
filename = sys.argv[1]
if filename == "--video":
    pipeline = gst.parse_launch('v4l2src ! ffmpegcolorspace ! videoscale ! alphacolor ! video/x-raw-rgb,width=16,height=6,framerate=25/1 ! fakesink name=sink sync=1') 
else:
    graph  = 'filesrc location=' + filename + ' ! decodebin name=decoder\n'
    graph += 'decoder. ! ffmpegcolorspace ! videoscale ! alphacolor ! video/x-raw-rgb,width=16,height=6,framerate=25/1 ! fakesink name=sink sync=1\n'
    graph += 'decoder. ! audioconvert ! audioresample ! alsasink'
    print graph

    pipeline = gst.parse_launch( graph )

def bus_watch( bus, message ):
    #End of movie
    frame_queue.put( None )
    pipeline.set_state( gst.STATE_NULL )
    loop.quit()
    return True

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect( "message::eos", bus_watch )

fakesink = pipeline.get_by_name('sink') 
fakesink.props.signal_handoffs = True 
fakesink.connect("handoff", callback) 

import pygame
class DataStream( Stream ):
    TITLE = "Video Stream"
    AUTHOR = "Steve"

    def __init__(self, frame_queue, output =  True):
        self.screen = pygame.display.set_mode( (160, 80) )
        self.frame_queue = frame_queue
        self.output = output

    def run(self):
        if self.output:
            self.t = threading.Thread( target = Stream.run, args=(self) )
        else:
            self.t = threading.Thread( target = self.justshow )

        self.t.start()

    def join(self):
        self.t.join()

    def justshow(self):
        self.screen = pygame.display.set_mode( (160, 80) )
        pipeline.set_state(gst.STATE_PLAYING) 

        while True:
            data = self.frame_queue.get()
            if data == None:
                return

            assert( len( data ) == COLS * ROWS )
            self.screen.fill( pygame.color.Color( 0, 0, 0 ) )
            
            for col in range(COLS):
                for row in range(ROWS):
                    r, g, b, a = data[row * COLS + col]
                    self.screen.fill( pygame.color.Color( r, g, b ), pygame.Rect( col * 10, row * 10, 10, 10 ) )
            pygame.display.update()
            pygame.time.delay(40)

    def init_frame(self):
        """
        Start with a blank frame.
        """
        pipeline.set_state(gst.STATE_PLAYING) 
        return Frame( frame_length, Color(0, 0, 0) )
    
    def next_frame( self, last_frame ):
        data = self.frame_queue.get()

        if data == None:
            #Finish streaming
            return False

        frame = Frame( frame_length )
        
        assert( len( data ) == COLS * ROWS )

        for col in range(COLS):
            for row in range(ROWS):
                r, g, b, a = data[row * COLS + col]
                frame.set( Mask( col, row ), Color( r, g, b ) )

        self.screen.fill( pygame.color.Color( 0, 0, 0 ) )
        
        for col in range(COLS):
            for row in range(ROWS):
                r, g, b, a = data[row * COLS + col]
                self.screen.fill( pygame.color.Color( r, g, b ), pygame.Rect( col * 10, row * 10, 10, 10 ) )
        pygame.display.update()

        return frame

if __name__ == "__main__":
    d = DataStream( frame_queue, False )
    d.run()
    loop = gobject.MainLoop()
    print 1
    loop.run()
    print 2
    d.join()
    print "Finished"
