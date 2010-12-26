from abracadabra import Frame, Color,Stream, Mask

class InvertStream(Stream):
    def init_frame(self):
        frame = Frame(200)
    
        frame.set(color = Color(255,0,0))
        frame.set(Mask(0,0).add_area((0,15), (0,3)), Color(0,255,0))
        return frame
#        red = Color(255,0,0)
#        red = (255,0,0)
#        red.invert()
#        mymask = Mask().add_column(1).invert()
#        
#        frame = abracadabra.Frame(1000)
#        frame.fill(Color(255,0,0))
#        
#        frame.set(Pos(10,3),Color(0,255,0))
#        frame.set(Color(0,255,0))
#        frame.pos(10,3)=color(255,0,0)
#        frame.pos(10,3).color(255,0,0)
#        
#        frame[(10,3)]=Color("red")
#        frame.fill(Color("red"), mask=Mask.square((10,2),(15,4)))
#        
#        frame.mask(square, ).fill

        Mask().add_square([0,0],[4,4])
        return frame
    
    def next_frame(self, last_frame):
        print last_frame
        return last_frame.shift(dx=1,dy=1)
    

if __name__ == "__main__":
    InvertStream().run()