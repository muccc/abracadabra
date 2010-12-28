chars = {'a': ["XXXXX",
               "  X X",
               "XXXXX"],
         'b': ["XXXXX",
               "X X X",
               " X X "],
         '0': [" XXX ",
               "X X X",
               " XXX "],
         '1': ["     ",
               "   X ",
               "XXXXX"],      
         '2': ["X  X ",
               "XX  X",
               "X XX "],      
         '3': ["X X X",
               "X X X",
               " XXX "],      
         '4': ["  XXX",
               "XXX  ",
               "  X  "],      
         '5': ["X  XX",
               "X X X",
               " X  X"],      
         '6': ["XXXXX",
               "X X X",
               "XXX X"],      
         '7': ["    X",
               "XXX X",
               "  XXX"],      
         '8': ["XXXXX",
               "X X X",
               "XXXXX"],      
         '9': ["X XXX",
               "X X X",
               "XXXXX"],
         ':': ["     ",
               " x x ",
               "     "],
         ' ': ["     ",
               "     ",
               "     "],      
        }

def get_row(char, row):
    r = []
    return  chars[char][row]
    #print row_txt
    #for i in range(5):
    #    if row_txt[i]=='X':
    #        r.append(i)
    #return tuple(r)
        
        