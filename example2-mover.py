from abracadabra import Frame, Color,Stream, Mask
from random import choice

class MoverStream(Stream):
    TITLE = "Simple Mover"
    AUTHOR = "iggy"
    def init_frame(self):
        return Frame(200,Color(255,255,0)).set(Mask().add_square(7, 2, 8, 3), Color(0,0,255))
        
    
    def next_frame(self, last_frame):
        return last_frame.shift(dx=choice([-1,0,1]), dy=choice([-1,0,1]))
    

if __name__ == "__main__":
    MoverStream().run()