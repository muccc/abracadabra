import sys
import threading
import gobject
gobject.threads_init()
import gst 
import pygame
import struct
import Queue
from abracadabra import Frame, Color, Stream, Mask
import sys

COLS = 16
ROWS = 6

class VideoSource():
    RGB_UNPACKER = struct.Struct("BBBB")

    def __init__( self, loop, filename, frame_queue ):
        self.loop = loop
        self.frame_queue = frame_queue

        if filename == "--video":
            graph = 'v4l2src ! ffmpegcolorspace ! videoscale ! alphacolor ! video/x-raw-rgb,width=16,height=6,framerate=25/1 ! fakesink name=sink sync=1'
        else:
            graph  = 'filesrc location=' + filename + ' ! decodebin name=decoder\n'
            graph += 'decoder. ! ffmpegcolorspace ! videoscale ! alphacolor ! video/x-raw-rgb,width=16,height=6,framerate=25/1 ! fakesink name=sink sync=1\n'
            graph += 'decoder. ! audioconvert ! audioresample ! alsasink'

        self.pipeline = gst.parse_launch( graph )

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect( "message::eos", self.bus_watch )

        fakesink = self.pipeline.get_by_name('sink') 
        fakesink.props.signal_handoffs = True 
        fakesink.connect("handoff", self.callback) 

    def start(self):
        self.pipeline.set_state(gst.STATE_PLAYING) 

    def stop(self):
        self.pipeline.set_state( gst.STATE_NULL )

    def callback(self, fakesink, buffer, pad, data=None): 
        data = []
        for i in range(0, len(buffer), 4):
            data.append( self.RGB_UNPACKER.unpack(buffer[i:i+4]) )

        try:
            self.frame_queue.put_nowait( data )
        except Queue.Full:
            pass
        return True 

    def bus_watch( self, bus, message ):
        #End of movie
        self.frame_queue.put( None )
        self.pipeline.set_state( gst.STATE_NULL )
        self.loop.quit()
        return True

class DataStream( Stream ):
    TITLE = "Video Stream"
    AUTHOR = "Steve"

    def __init__(self, frame_queue, output, onStart):
        self.screen = pygame.display.set_mode( (160, 80) )
        self.frame_queue = frame_queue
        self.output = output
        self.onStart = onStart

    def start(self):
        if self.output:
            self.t = threading.Thread( target = self.run )
        else:
            self.t = threading.Thread( target = self.justshow )

        self.t.start()

    def join(self):
        self.t.join()

    def justshow(self):
        self.screen = pygame.display.set_mode( (160, 80) )
        self.onStart()

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
        self.onStart()
        return Frame( 40, Color(0, 0, 0) )
    
    def next_frame( self, last_frame ):
        data = self.frame_queue.get()

        if data == None:
            #Finish streaming
            return False

        frame = Frame( 40 )
        
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
    filename = sys.argv[1]

    loop = gobject.MainLoop()
    frame_queue = Queue.Queue(1)

    source = VideoSource( loop, filename, frame_queue )
    if len(sys.argv) > 2:
        d = DataStream( frame_queue, True, source.start )
    else:
        d = DataStream( frame_queue, False, source.start )

    d.start()
    loop.run()
    d.join()
