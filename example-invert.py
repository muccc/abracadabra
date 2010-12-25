import abracadabra

class InvertStream(abracadabra.Stream):
    def init_frame(self):
        frame = abracadabra.Frame(1000)
        frame.fill((255,0,0))
        return frame
    
    def next_frame(self, last_frame):
        return last_frame.invert()
    

if __name__ == "__main__":
    InvertStream().run()