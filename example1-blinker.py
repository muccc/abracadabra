from abracadabra import Frame, Color,Stream, Mask

class BlinkerStream(Stream):
    TITLE = "Simple Blinker"
    AUTHOR = "iggy"
    def init_frame(self):
        return Frame(1000, Color(255,0,0))
    
    def next_frame(self, last_frame):
        return last_frame.invert()
    

if __name__ == "__main__":
    BlinkerStream().run()