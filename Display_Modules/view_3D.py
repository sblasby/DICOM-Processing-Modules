import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



class View3D(tk.Tk):

    def __init__(self, roi_data : list):

        self.index = 0

        self.upper = len(roi_data)

        self.roi_num = list(range(self.upper))

        self.data = roi_data

        super().__init__()

        self.wm_title('ROI Viewer')

        self._SetWidthHeightPosition()

        self._CreateUI()

        self._PlotData(roi_data[0])

        self._Interactivity()
    

    def _CreateUI(self):

        self._RoiInformerUI()

        self.fig = Figure()

        self.axs = self.fig.add_subplot(projection='3d')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=(10,20))


    def _RoiInformerUI(self):
        
        item_frame = tk.Frame(self)

        self.prev_button = tk.Button(item_frame, text="Previous", command= lambda: self._NextPreviousRoi(-1))

        self.next_button = tk.Button(item_frame, text="Next", command= lambda: self._NextPreviousRoi(1))

        self.roi_display = tk.Label(item_frame, text="ROI 1", padx=10)

        self.prev_button.grid(row=0, column=0)
        
        self.roi_display.grid(row=0, column=1)

        self.next_button.grid(row=0, column=2)

        item_frame.pack()


    def _Interactivity(self):

        self.protocol("WM_DELETE_WINDOW", self._OnClose)

    
    def _PlotData(self, data):

        axs = self.axs

        axs.cla()

        axs.scatter(data[0], data[1], data[2], marker='o')

        self.canvas.draw()


    def _OnClose(self):

        plt.close('all')

        self.quit()


    def _NextPreviousRoi(self, toGo):
        
        if toGo == 1 and self.index < (self.upper - 1):
            
            self.index += 1

            self.roi_display.config(text=f'ROI {self.index + 1}')

            self._PlotData(self.data[self.index])
        
        elif toGo == -1 and self.index > 0:
            
            self.index -= 1

            self.roi_display.config(text=f'ROI {self.index + 1}')

            self._PlotData(self.data[self.index])


    def _SetWidthHeightPosition(self):
        
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        gui_width = width * 3 // 4
        gui_height = height * 3 // 4
        
        x_pos = (width - gui_width) // 2
        y_pos = (height - gui_height) // 2

        self.geometry(f'{gui_width}x{gui_height}+{x_pos}+{y_pos}')
    
    

            
