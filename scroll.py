from abracadabra import Frame, Color,Stream, Mask
from random import choice
from chars import get_row
from datetime import datetime



class ScrollStream(Stream):
    TITLE = "clock"
    AUTHOR = "iggy"
    

    def init_frame(self):
        self.char_index = 0
        self.row_index = 0
        self.msg = str(datetime.now().time())[:8]+"    "
        return Frame(200)
        
        
    def next_frame(self, last_frame):
        last_frame.shift(dx=-1)
        
        if self.row_index<= 2:
            row = get_row(self.msg[self.char_index],self.row_index)
        else:
            row="     "
            self.row_index = -1
            self.char_index = (self.char_index+1)
            if self.char_index == len(self.msg):
                self.char_index = 0
                self.msg = str(datetime.now().time())[:8]+"   "
        m = Mask()
        print row
        print self.row_index
        print self.char_index
        print "Char %s"%self.msg[self.char_index]
        for y in range(5):
            if row[y]!=" ":
                last_frame.set(Mask(15,5-y),Color(0,0,255))
            else:
                last_frame.set(Mask(15,5-y),Color(0,0,0))
        #last_frame.set(m, Color(0,0,255))
        #f.set(Mask().add_row(15).remove_mask(m), Color(0,0,0))
        self.row_index +=1
    
        return last_frame
            
    

if __name__ == "__main__":
    ScrollStream().run()