import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SliceView(tk.Tk):

    def __init__(self, data, colour_map = 'gray'):

        self.slices_data = data

        self.cm = colour_map

        super().__init__()

        self.wm_title('Dicom Slice View')
        
        self._SetWidthHeightPosition()

        self._CreateUI()

        self.current_slice_ind = len(self.slices_data) // 2

        self._PlotData()

        self._Interactivity()
    

    def _CreateUI(self):

        self._SliceInformerUI(self.slices_data)

        self.fig = Figure()

        self.axs = self.fig.add_subplot()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=(10,20))


    def _SliceInformerUI(self, data):
        
        slice_num_frame = tk.Frame(self)

        slice_num_label = tk.Label(slice_num_frame, text="Slice Number: ")

        self.slice_num_field = tk.Entry(slice_num_frame, width=3)

        slice_num_label2 = tk.Label(slice_num_frame, text=f' of {len(data)}')

        slice_num_label.grid(row=0, column=0)
        self.slice_num_field.grid(row=0, column=1)
        slice_num_label2.grid(row=0, column=2)

        slice_num_frame.pack(pady=(10,0))


    def _Interactivity(self):

        self.protocol("WM_DELETE_WINDOW", self._OnClose)

        self.canvas.get_tk_widget().bind('<MouseWheel>', self._Scroll)

        self.bind_all('<Return>', self._Enter)
    

    def _PlotData(self):

        pixel_contour_data = self.slices_data[self.current_slice_ind]

        pixel_data = pixel_contour_data.PixelData

        contour_x = pixel_contour_data.ContourCoords[0]

        contour_y = pixel_contour_data.ContourCoords[1]

        contour_offset_x = pixel_contour_data.ContourOffset[0]

        contour_offset_y = pixel_contour_data.ContourOffset[1]

        self.slice_num_field.delete(0, tk.END)

        self.slice_num_field.insert(0, f'{self.current_slice_ind + 1}')

        axs = self.axs

        axs.cla()

        axs.imshow(pixel_data, cmap=self.cm)

        axs.plot(contour_x + contour_offset_x, contour_y + contour_offset_y, 'rx', markersize = 2)

        self.canvas.draw()


    def _OnClose(self):

        plt.close('all')

        self.quit()


    def _SetWidthHeightPosition(self):
        
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()

        gui_width = width * 3 // 4
        gui_height = height * 3 // 4
        
        x_pos = (width - gui_width) // 2
        y_pos = (height - gui_height) // 2

        self.geometry(f'{gui_width}x{gui_height}+{x_pos}+{y_pos}')
    

    def _Scroll(self, event):

        slice_ind = self.current_slice_ind
        
        if event.delta > 0 and slice_ind < len(self.slices_data) - 1:
            
            self.current_slice_ind += 1
            

        elif event.delta < 0 and 0 < slice_ind:

            self.current_slice_ind -= 1
            

        self._PlotData()
    
    def _Enter(self, event):
        
        try:

            slice_value = int(self.slice_num_field.get())

            self.current_slice_ind = slice_value - 1

            self._PlotData()
        
        except:
            pass

            
