
# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
import sys
from change_summary_ui import *
from tkinter import *

class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):
        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("DDARTS: Change Summary Generation Tool...........")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        # a2aDetectButton = Button(self, anchor="w",text="Detect M2M", command=self.client_detect, height=2, width=20)
        # a2aResultButton = Button(self, anchor="w",text="Show A2A result", command=self.client_show, height=2, width=20)
        # a2aExtractButton = Button(self, anchor="w",text="Extract data for A2A", command=self.client_extract, height=2, width=20)
        # m2mStatButton = Button(self, anchor="w",text="Show annotated stat", command=self.show_stat, height=2, width=20)

        # placing the button on my window
        helpButton = Button(self, anchor="w", text="Help about DDARTS",
                                   command=self.show_summary_window, height=2, width=30)
        helpButton.place(x=200, y=100)

        changeSummaryButton = Button(self, anchor="w", text="Individual Change Summary", command=self.show_summary_window, height=2, width=30)
        changeSummaryButton.place(x=200,y=150)

        releaseNoteButton = Button(self, anchor="w", text="Design Release Notes",
                                     command=self.show_release_window, height=2, width=30)
        releaseNoteButton.place(x=200, y=200)
        # a2aResultButton.place(x=200, y=100)
        #
        # # placing the button on my window
        # a2aExtractButton.place(x=200, y=140)
        # a2aDetectButton.place(x=200, y=180)
        # m2mStatButton.place(x=200, y=220)

    def show_summary_window(self):
        DRleaseNoteUI(1, self.master).openNewWindow()
    def show_release_window(self):
        DRleaseNoteUI(0,self.master).openNewWindow()

# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = Tk()

root.geometry("800x600")
# creation of an instance
app = Window(root)

# mainloop
root.mainloop()