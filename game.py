import tkinter as tk
import tkinter.messagebox
import random

import sender
import receiver
import time
import threading
import communication
import utils

sender = sender.Sender()
receiver = receiver.Receiver()

class GameBoard(tk.Frame):
    def __init__(self, parent, rows=3, columns=3, size=128, color1="white", color2="blue"):
        '''size is the size of a square, in pixels'''

        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}
        self.xcord = 0
        self.ycord = 0
        self.points = 0

        self.enemyx = random.randint(0,2)
        self.enemyy = random.randint(0,2)

        while(self.enemyx == 0 and self.enemyy == 0):
            self.enemyx = random.randint(0,2)
            self.enemyy = random.randint(0,2)


        canvas_width = columns * size
        canvas_height = rows * size

        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,
                                width=canvas_width, height=canvas_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        # this binding will cause a refresh if the user interactively
        # changes the window size
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind("<Left>", self.leftKey)
        self.canvas.bind("<Right>", self.rightKey)
        self.canvas.bind("<Up>", self.upKey)
        self.canvas.bind("<Down>", self.downKey)
        self.canvas.focus_set()

    def leftKey(self, event):
        if(self.ycord > 0):
            self.ycord = self.ycord - 1
            self.placepiece("player1", self.xcord, self.ycord)
            self.enemyMove()
            self.afterMove()
    
    def rightKey(self, event):
        if(self.ycord < 2):
            self.ycord = self.ycord + 1
            self.placepiece("player1", self.xcord, self.ycord)
            self.enemyMove()
            self.afterMove()

    def upKey(self, event):
        if(self.xcord > 0):
            self.xcord = self.xcord - 1
            self.placepiece("player1", self.xcord, self.ycord)
            self.enemyMove()
            self.afterMove()

    def downKey(self, event):
        if(self.xcord < 2):
            self.xcord = self.xcord + 1
            self.placepiece("player1", self.xcord, self.ycord)
            self.enemyMove()
            self.afterMove()

    def enemyMove(self):
        vec = random.randint(0,3)
        if(vec==0):
            if(self.enemyy > 0):
                self.enemyy = self.enemyy - 1
        elif(vec==1):
            if(self.enemyy < 2):
                self.enemyy = self.enemyy + 1
        elif(vec==2):
            if(self.enemyx > 0):
                self.enemyx = self.enemyx - 1
        else:
            if(self.enemyx < 2):
                self.enemyx = self.enemyx + 1
        
        print("New enemy pos : ", self.enemyx, self.enemyy)

    def afterMove(self):
        if(self.xcord == self.enemyx and self.ycord==self.enemyy):
            print("Collision! Points = ", self.points)
            tkinter.messagebox.showinfo("Collision","Collision\nPoints : "+str(self.points))
        else:
            self.points=self.points+1
            tkinter.messagebox.showinfo("Information","Points : "+str(self.points))
        

    def addpiece(self, name, image, row=0, column=0):
        '''Add a piece to the playing board'''
        self.canvas.create_image(0,0, image=image, tags=(name, "piece"), anchor="c")
        self.placepiece(name, row, column)
        print("Enemy is at : ", self.enemyx, self.enemyy)

    def placepiece(self, name, row, column):
        '''Place a piece at the given row/column'''
        self.pieces[name] = (row, column)
        x0 = (column * self.size) + int(self.size/2)
        y0 = (row * self.size) + int(self.size/2)
        self.canvas.coords(name, x0, y0)
    
    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placepiece(name, self.pieces[name][0], self.pieces[name][1])
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def xCallBack(self):
        # oblivious_tranfer(y)
        if self.enemyx == 0:
            x_arr = [0, 0]
        elif self.enemyx == 1:
            x_arr = [1, 0]
        else:
            x_arr = [0, 1]

        y_arr = [1, 1]

        res = []

        t = threading.Thread(target=sender.execute_string_ot, args=(x_arr, y_arr))
        # DaemonThread(sender.execute_string_ot, args=(x_arr , y_arr))
        k = threading.Thread(target=lambda q, arg1, arg2: q.append(receiver.execute_string_ot(arg1, arg2)),
                             args=(res, 0, 2))
        # DaemonThread(receiver.executimport threadınge_string_ot, args=(1,2))

        t.start()
        k.start()

        t.join()
        k.join()

        val = res[0][0] + 2 * res[0][1]

        #print(val)

        tkinter.messagebox.showinfo( "X", str(val))

    def yCallBack(self):
        #oblivious_tranfer(y)
        if self.enemyy == 0:
            y_arr = [0, 0]
        elif self.enemyy == 1:
            y_arr = [1, 0]
        else:
            y_arr = [0, 1]

        x_arr = [1, 1]

        res = []

        t = threading.Thread(target=sender.execute_string_ot, args=(x_arr,y_arr))
        #DaemonThread(sender.execute_string_ot, args=(x_arr , y_arr))
        k = threading.Thread(target=lambda q,arg1,arg2: q.append(receiver.execute_string_ot(arg1,arg2)), args=(res,1,2))
        #DaemonThread(receiver.executimport threadınge_string_ot, args=(1,2))

        t.start()
        k.start()

        t.join()
        k.join()

        val = res[0][0] + 2* res[0][1]

        #print(val)

        tkinter.messagebox.showinfo( "Y", str(val))
        


# image comes from the silk icon set which is under a Creative Commons
# license. For more information see http://www.famfamfam.com/lab/icons/silk/
imagedata = '''
    R0lGODlhEAAQAOeSAKx7Fqx8F61/G62CILCJKriIHM+HALKNMNCIANKKANOMALuRK7WOVLWPV9eR
    ANiSANuXAN2ZAN6aAN+bAOCcAOKeANCjKOShANKnK+imAOyrAN6qSNaxPfCwAOKyJOKyJvKyANW0
    R/S1APW2APW3APa4APe5APm7APm8APq8AO28Ke29LO2/LO2/L+7BM+7BNO6+Re7CMu7BOe7DNPHA
    P+/FOO/FO+jGS+/FQO/GO/DHPOjBdfDIPPDJQPDISPDKQPDKRPDIUPHLQ/HLRerMV/HMR/LNSOvH
    fvLOS/rNP/LPTvLOVe/LdfPRUfPRU/PSU/LPaPPTVPPUVfTUVvLPe/LScPTWWfTXW/TXXPTXX/XY
    Xu/SkvXZYPfVdfXaY/TYcfXaZPXaZvbWfvTYe/XbbvHWl/bdaPbeavvadffea/bebvffbfbdfPvb
    e/fgb/Pam/fgcvfgePTbnfbcl/bfivfjdvfjePbemfjelPXeoPjkePbfmvffnvbfofjlgffjkvfh
    nvjio/nnhvfjovjmlvzlmvrmpvrrmfzpp/zqq/vqr/zssvvvp/vvqfvvuPvvuvvwvfzzwP//////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////yH+FUNyZWF0ZWQgd2l0aCBU
    aGUgR0lNUAAh+QQBCgD/ACwAAAAAEAAQAAAIzAD/CRxIsKDBfydMlBhxcGAKNIkgPTLUpcPBJIUa
    +VEThswfPDQKokB0yE4aMFiiOPnCJ8PAE20Y6VnTQMsUBkWAjKFyQaCJRYLcmOFipYmRHzV89Kkg
    kESkOme8XHmCREiOGC/2TBAowhGcAyGkKBnCwwKAFnciCAShKA4RAhyK9MAQwIMMOQ8EdhBDKMuN
    BQMEFPigAsoRBQM1BGLjRIiOGSxWBCmToCCMOXSW2HCBo8qWDQcvMMkzCNCbHQga/qMgAYIDBQZU
    yxYYEAA7
'''

if __name__ == "__main__":
    root = tk.Tk()
    board = GameBoard(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    player1 = tk.PhotoImage(data=imagedata)
    board.addpiece("player1", player1, 0,0)

    B1 = tk.Button(root, text ="Get X", command = board.xCallBack)
    B2 = tk.Button(root, text ="Get Y", command = board.yCallBack)
    B1.pack()
    B2.pack()
    board.mainloop()
