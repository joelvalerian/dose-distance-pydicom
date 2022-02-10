import tkinter as tk
import tkinter.ttk as ttk
import pydicom
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

class DoseDistanceExtractor:

    def print(self):
        print('Executed')

    def getpath_RTDOSE(self):
        filename = tk.filedialog.askopenfilename(filetypes=[('DICOM files', '*.dcm')])
        self.rtdose_filepath.set(filename)
        self.new_rtdose.set(True)

    def getpath_RTSTRUCT(self):
        filename = tk.filedialog.askopenfilename(filetypes=[('DICOM files', '*.dcm')])
        self.rtstruct_filepath.set(filename)
        self.new_rtstruct.set(True)


    def plot(self):
        if self.is_plotted.get() == False:
            try:
                self.source_ax1_plot = self.source_ax1.imshow(self.rtdose[self.source_slice_selected.get()])
                self.source_ax2_plot = self.source_ax2.imshow(self.rtdose[self.source_slice_selected.get()])
                self.target_ax1_plot = self.target_ax1.imshow(self.rtdose[self.target_slice_selected.get()])
                self.target_ax2_plot = self.target_ax2.imshow(self.rtdose[self.target_slice_selected.get()])

                self.source_fig1_canvas = FigureCanvasTkAgg(self.source_fig1, self.plot_window)
                self.source_fig1_canvas.get_tk_widget().grid(column=0, row=0)
                self.source_fig2_canvas = FigureCanvasTkAgg(self.source_fig2, self.plot_window)
                self.source_fig2_canvas.get_tk_widget().grid(column=0, row=1)
                self.target_fig1_canvas = FigureCanvasTkAgg(self.target_fig1, self.plot_window)
                self.target_fig1_canvas.get_tk_widget().grid(column=1, row=0)
                self.target_fig2_canvas = FigureCanvasTkAgg(self.target_fig2, self.plot_window)
                self.target_fig2_canvas.get_tk_widget().grid(column=1, row=1)

                self.source_fig1_divider = make_axes_locatable(self.source_ax1)
                self.source_fig1_cb = self.source_fig1.colorbar(self.source_ax1_plot,
                    cax=self.source_fig1_divider.append_axes('right', size='5%', pad=0.05))
                self.source_fig2_divider = make_axes_locatable(self.source_ax2)
                self.source_fig2_cb = self.source_fig2.colorbar(self.source_ax2_plot,
                    cax=self.source_fig2_divider.append_axes('right', size='5%', pad=0.05))
                self.target_fig1_divider = make_axes_locatable(self.target_ax1)
                self.target_fig1_cb = self.target_fig1.colorbar(self.target_ax1_plot,
                    cax=self.target_fig1_divider.append_axes('right', size='5%', pad=0.05))
                self.target_fig2_divider = make_axes_locatable(self.target_ax2)
                self.target_fig2_cb = self.target_fig2.colorbar(self.target_ax2_plot,
                    cax=self.target_fig2_divider.append_axes('right', size='5%', pad=0.05))

                self.plot_status.set('Plotted!')
                self.is_plotted.set(True)
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_status.set('Already plotted!')

    def import_DICOM(self):
        if self.new_rtdose.get() == True and self.new_rtstruct.get() == True:
            try:
                self.RTDOSE = pydicom.dcmread(self.rtdose_filepath.get())
                self.RTSTRUCT = pydicom.dcmread(self.rtstruct_filepath.get())

                z_spacing = abs(self.RTSTRUCT.ROIContourSequence[0].ContourSequence[1].ContourData[2] - self.RTSTRUCT.ROIContourSequence[0].ContourSequence[0].ContourData[2])
                yx_spacing = [float(i) for i in self.RTDOSE.PixelSpacing]
                structure_list = [self.RTSTRUCT.StructureSetROISequence[i].ROIName for i in range(len(self.RTSTRUCT.StructureSetROISequence))]

                self.patient_id = self.RTDOSE.PatientID
                self.rtdose = self.RTDOSE.pixel_array * self.RTDOSE.DoseGridScaling
                self.rtdose_dimension = self.rtdose.shape
                self.rtdose_spacing = tuple([z_spacing, *yx_spacing])
                self.rtdose_origin = tuple([*self.RTDOSE.ImagePositionPatient])
                self.structure_list = structure_list

                self.patient_id_str.set(self.patient_id)
                self.rtdose_dimension_str.set(self.rtdose_dimension)
                self.rtdose_spacing_str.set(self.rtdose_spacing)
                self.rtdose_origin_str.set(f'{self.rtdose_origin[2]:.1f}, {self.rtdose_origin[1]:.1f}, {self.rtdose_origin[0]:.1f}')
                self.structure_list_var.set([str(i) + '. ' + structure_list[i] for i in range(len(structure_list))])

                self.importer_slice_slider1['to'] = self.rtdose.shape[0] - 1
                self.importer_slice_slider2['to'] = self.rtdose.shape[0] - 1
                
                self.update_combobox(self.extractor_source_selection, structure_list)
                self.update_combobox(self.extractor_target_selection, structure_list)
                self.plot()

                self.import_status.set('Import success!')
                self.new_rtdose.set(False)
                self.new_rtstruct.set(False)
                
            except FileNotFoundError:
                self.import_status.set('File(s) not found!')

            except pydicom.errors.InvalidDicomError:
                self.import_status.set('Invalid DICOM file(s)!')

            except Exception:
                self.import_status.set('Unknown error!')
        else:
            self.import_status.set('Already imported!')

    def ExtractContour(self, index, target_contour):
        for contour in self.RTSTRUCT.ROIContourSequence[index].ContourSequence:
            for i in range(0, len(contour.ContourData), 3):
                x = round((contour.ContourData[i]-self.rtdose_origin[0])/self.rtdose_spacing[2])
                y = round((contour.ContourData[i+1]-self.rtdose_origin[1])/self.rtdose_spacing[1])
                z = round((contour.ContourData[i+2]-self.rtdose_origin[2])/self.rtdose_spacing[0])
                target_contour.append([z, y, x])

    def FillContour(self, target_contour, target_volume):
        target_contour_slice = list(dict.fromkeys([contour[0] for contour in target_contour]))
        print(f'Thickness: {len(target_contour_slice)} slices')
        for target in target_contour_slice:
            SliceContour = []
            for z, y, x in target_contour:
                if z == target:
                    SliceContour.append([x, y])
                    SliceContour = np.asarray(SliceContour)
                    cv.fillPoly(target_volume[target], [SliceContour], 255)

    def ConvertCoordinate(self, z, y, x):
        return [self.rtdose_origin[2] + (z*self.rtdose_spacing[0]), self.rtdose_origin[1] + (y*self.rtdose_spacing[1]), self.rtdose_origin[0] + (x*self.rtdose_spacing[2])]

    def EuclideanDistance(self, A, B):
        A = np.array(A)
        B = np.array(B)
        return np.sqrt(np.sum(np.square(A-B)))

    def GetRealCoordinateDose(self, Coordinate, Volume, Dose):
        for z in range(Volume.shape[0]):
            for y in range(Volume.shape[1]):
                for x in range(Volume.shape[2]):
                    if Volume[z][y][x] == 255:
                        Coordinate.append([*ConvertCoordinate(z, y, x), Dose[z][y][x]])

    def update_combobox(self, combobox, values):
        combobox['values'] = [*values]

    def source_on_selected(self, event):
        self.source_selected.set(event.widget.get())
        self.source_index = self.structure_list.index(self.source_selected.get())

    def target_on_selected(self, event):
        self.target_selected.set(event.widget.get())
        self.target_index = self.structure_list.index(self.target_selected.get())

    def hover_source_ax1(self, event):
        if event.inaxes == self.source_ax1:
            x, y = event.xdata, event.ydata
            i, j = np.round(np.array((x, y))).astype(int)
            try:
                self.plot_coord.set(str([round(x, 3), round(y, 4)]))
                self.plot_index.set(str([i, j]))
                self.plot_value.set(str(round(self.rtdose[self.source_slice_selected.get()][j][i], 3)))
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_coord.set(str(''))
            self.plot_index.set(str(''))
            self.plot_value.set(str(''))

    def hover_source_ax2(self, event):
        if event.inaxes == self.source_ax2:
            x, y = event.xdata, event.ydata
            i, j = np.round(np.array((x, y))).astype(int)
            try:
                self.plot_coord.set(str([round(x, 3), round(y, 4)]))
                self.plot_index.set(str([i, j]))
                self.plot_value.set(str(round(self.rtdose[self.source_slice_selected.get()][j][i], 3)))
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_coord.set(str(''))
            self.plot_index.set(str(''))
            self.plot_value.set(str(''))

    def hover_target_ax1(self, event):
        if event.inaxes == self.target_ax1:
            x, y = event.xdata, event.ydata
            i, j = np.round(np.array((x, y))).astype(int)
            try:
                self.plot_coord.set(str([round(x, 3), round(y, 4)]))
                self.plot_index.set(str([i, j]))
                self.plot_value.set(str(round(self.rtdose[self.target_slice_selected.get()][j][i], 3)))
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_coord.set(str(''))
            self.plot_index.set(str(''))
            self.plot_value.set(str(''))

    def hover_target_ax2(self, event):
        if event.inaxes == self.target_ax2:
            x, y = event.xdata, event.ydata
            i, j = np.round(np.array((x, y))).astype(int)
            try:
                self.plot_coord.set(str([round(x, 3), round(y, 4)]))
                self.plot_index.set(str([i, j]))
                self.plot_value.set(str(round(self.rtdose[self.target_slice_selected.get()][j][i], 3)))
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_coord.set(str(''))
            self.plot_index.set(str(''))
            self.plot_value.set(str(''))

    def change_source_slice(self, event):
        try:
            self.source_fig1_cb.remove()
            self.source_fig2_cb.remove()
            self.source_ax1_plot = self.source_ax1.imshow(self.rtdose[int(event)])
            self.source_ax2_plot = self.source_ax2.imshow(self.rtdose[int(event)])

            self.source_fig1_canvas = FigureCanvasTkAgg(self.source_fig1, self.plot_window)
            self.source_fig1_canvas.get_tk_widget().grid(column=0, row=0)
            self.source_fig2_canvas = FigureCanvasTkAgg(self.source_fig2, self.plot_window)
            self.source_fig2_canvas.get_tk_widget().grid(column=0, row=1)

            self.source_fig1_divider = make_axes_locatable(self.source_ax1)
            self.source_fig1_cb = self.source_fig1.colorbar(self.source_ax1_plot,
                cax=self.source_fig1_divider.append_axes('right', size='5%', pad=0.05))
            self.source_fig2_divider = make_axes_locatable(self.source_ax2)
            self.source_fig2_cb = self.source_fig2.colorbar(self.source_ax2_plot,
                cax=self.source_fig2_divider.append_axes('right', size='5%', pad=0.05))


            self.source_slice_selected.set(event)

            self.plot_status.set('Replotted!')
        except AttributeError:
            pass

    def change_target_slice(self, event):
        try:
            self.target_fig1_cb.remove()
            self.target_fig2_cb.remove()
            self.target_ax1_plot = self.target_ax1.imshow(self.rtdose[int(event)])
            self.target_ax2_plot = self.target_ax2.imshow(self.rtdose[int(event)])

            self.target_fig1_canvas = FigureCanvasTkAgg(self.target_fig1, self.plot_window)
            self.target_fig1_canvas.get_tk_widget().grid(column=1, row=0)
            self.target_fig2_canvas = FigureCanvasTkAgg(self.target_fig2, self.plot_window)
            self.target_fig2_canvas.get_tk_widget().grid(column=1, row=1)

            self.target_fig1_divider = make_axes_locatable(self.target_ax1)
            self.target_fig1_cb = self.target_fig1.colorbar(self.target_ax1_plot,
                cax=self.target_fig1_divider.append_axes('right', size='5%', pad=0.05))
            self.target_fig2_divider = make_axes_locatable(self.target_ax2)
            self.target_fig2_cb = self.target_fig2.colorbar(self.target_ax2_plot,
                cax=self.target_fig2_divider.append_axes('right', size='5%', pad=0.05))

            self.target_slice_selected.set(event)

            self.plot_status.set('Replotteddd!')
        except AttributeError:
            pass

    def __init__(self, root):
        self.root = root
        self.root.title('Dose Distance Extractor')

        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky='nsew')

        self.main_title = tk.Label(self.mainframe, text='Dose Distance Extractor by Joel Valerian')
        self.main_title.grid(column=0, row=0)
        self.body = tk.Frame(self.mainframe)
        self.body.grid(column=0, row=1)

        self.header = tk.Frame(self.body)
        self.header.grid(column=0, row=0, sticky='nsew')
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)
        self.header.columnconfigure(2, weight=1)
        self.content = tk.Frame(self.body)
        self.content.grid(column=0, row=1)

        tk.Label(self.header, text='Importer').grid(column=0, row=0)
        self.importer = tk.Frame(self.header)
        self.importer.grid(column=0, row=1, sticky='n')

        self.new_rtdose = tk.BooleanVar(value=True)
        self.new_rtstruct = tk.BooleanVar(value=True)
        self.is_plotted = tk.BooleanVar(value=False)
        self.rtdose_filepath = tk.StringVar(value='C:/Users/ivand/OneDrive/Desktop/RD1.dcm')
        self.rtstruct_filepath = tk.StringVar(value='C:/Users/ivand/OneDrive/Desktop/RS1.dcm')
        self.import_status = tk.StringVar(value='No files imported')
        self.plot_status = tk.StringVar(value='No plot yet')
        self.source_slice_selected = tk.IntVar()
        self.target_slice_selected = tk.IntVar()
        self.structure_list = []

        tk.Label(self.importer, text='RTDOSE').grid(column=0, row=0, sticky='e')
        tk.Label(self.importer, text='RTSTUCT').grid(column=0, row=1, sticky='e')

        self.importer_rtdose_filepath = tk.Entry(self.importer, textvariable=self.rtdose_filepath)
        self.importer_rtdose_filepath.grid(column=1, row=0, sticky='w')
        self.importer_rtstruct_filepath = tk.Entry(self.importer, textvariable=self.rtstruct_filepath)
        self.importer_rtstruct_filepath.grid(column=1, row=1, sticky='w')
        self.importer_import_status = tk.Label(self.importer, textvariable=self.import_status)
        self.importer_import_status.grid(column=0, row=2)
        self.importer_plot_status = tk.Label(self.importer, textvariable=self.plot_status)
        self.importer_plot_status.grid(column=1, row=2)
        
        self.importer_rtdose_button = tk.Button(self.importer, text='...', command=self.getpath_RTDOSE)
        self.importer_rtdose_button.grid(column=2, row=0)
        self.importer_rtstruct_button = tk.Button(self.importer, text='...', command=self.getpath_RTSTRUCT)
        self.importer_rtstruct_button.grid(column=2, row=1)
        self.importer_import_button = tk.Button(self.importer, text='Import', command=self.import_DICOM)
        self.importer_import_button.grid(column=2, row=2, sticky='n')

        tk.Label(self.importer, text='Slice Selection').grid(column=1, row=3)
        tk.Label(self.importer, text='<- Viewer 1 || Viewer 2 ->').grid(column=1, row=4, sticky='s')

        self.importer_slice_slider1 = tk.Scale(self.importer,
            from_=0,
            to=100,
            orient='horizontal',
            command=self.change_source_slice)
        self.importer_slice_slider1.grid(column=0, row=4, sticky='s')
        self.importer_slice_slider2 = tk.Scale(self.importer,
            from_=0,
            to=100,
            orient='horizontal',
            command=self.change_target_slice)
        self.importer_slice_slider2.grid(column=2, row=4, sticky='s')

        tk.Label(self.header, text='Patient Information').grid(column=1, row=0)
        self.information = tk.Frame(self.header)
        self.information.grid(column=1, row=1, sticky='n')

        self.patient_id_str = tk.StringVar()
        self.rtdose_dimension_str = tk.StringVar()
        self.rtdose_spacing_str = tk.StringVar()
        self.rtdose_origin_str = tk.StringVar()
        self.structure_list_var = tk.StringVar()
        
        tk.Label(self.information, text='Patient ID').grid(column=0, row=0, sticky='e')
        tk.Label(self.information, text='Dose Array Dimension').grid(column=0, row=1, sticky='e')
        tk.Label(self.information, text='Dose Array Spacing').grid(column=0, row=2, sticky='e')
        tk.Label(self.information, text='Origin Coordinate').grid(column=0, row=3, sticky='e')
        tk.Label(self.information, text='Structure List').grid(column=0, row=4, sticky='ne')
        
        self.information_patient_id = tk.Entry(self.information, textvariable=self.patient_id_str, state=tk.DISABLED)
        self.information_patient_id.grid(column=1, row=0)
        self.information_rtdose_dimension = tk.Entry(self.information, textvariable=self.rtdose_dimension_str, state=tk.DISABLED)
        self.information_rtdose_dimension.grid(column=1, row=1)
        self.information_rtdose_spacing = tk.Entry(self.information, textvariable=self.rtdose_spacing_str, state=tk.DISABLED)
        self.information_rtdose_spacing.grid(column=1, row=2)
        self.information_rtdose_origin = tk.Entry(self.information, textvariable=self.rtdose_origin_str, state=tk.DISABLED)
        self.information_rtdose_origin.grid(column=1, row=3)
        self.information_structure_list = tk.Listbox(self.information, listvariable=self.structure_list_var, height=5, activestyle='none')
        self.information_structure_list.grid(column=1, row=4)
        self.structure_list_scrollbar = tk.Scrollbar(self.information, orient='vertical', command=self.information_structure_list.yview)
        self.structure_list_scrollbar.grid(column=1, row=4, sticky='nse')
        self.information_structure_list['yscrollcommand'] = self.structure_list_scrollbar.set
        
        tk.Label(self.header, text='Extractor').grid(column=2, row=0)
        self.extractor = tk.Frame(self.header)
        self.extractor.grid(column=2, row=1, sticky='n')

        self.source_selected = tk.StringVar(value='No source selected')
        self.target_selected = tk.StringVar(value='No target selected')
        self.extract_status = tk.StringVar(value='No files extracted')

        tk.Label(self.extractor, text='Contour Selection').grid(column=1, row=0)
        tk.Label(self.extractor, text='Source').grid(column=0, row=1)
        tk.Label(self.extractor, text='Target').grid(column=0, row=2)
        
        self.extractor_source_selection = ttk.Combobox(self.extractor, values=self.structure_list)
        self.extractor_source_selection.grid(column=1, row=1)
        self.extractor_source_selection.bind('<<ComboboxSelected>>', self.source_on_selected)
        self.extractor_target_selection = ttk.Combobox(self.extractor, values=self.structure_list)
        self.extractor_target_selection.grid(column=1, row=2)
        self.extractor_target_selection.bind('<<ComboboxSelected>>', self.target_on_selected)
        self.extractor_plot_status = tk.Label(self.extractor, textvariable=self.extract_status)
        self.extractor_plot_status.grid(column=1, row=3)

        self.extractor_source_selected = tk.Label(self.extractor, textvariable=self.source_selected)
        self.extractor_source_selected.grid(column=2, row=1)
        self.extractor_target_selected = tk.Label(self.extractor, textvariable=self.target_selected)
        self.extractor_target_selected.grid(column=2, row=2)
        self.extractor_plot_button = tk.Button(self.extractor, text='Extract')
        self.extractor_plot_button.grid(column=2, row=3)

        ttk.Label(self.content, text='Dose Distribution').grid(column=0, row=0)
        self.legend_window = tk.Frame(self.content)
        self.legend_window.grid(column=0, row=1)
        self.plot_window = tk.Frame(self.content)
        self.plot_window.grid(column=0, row=2)

        self.plot_coord = tk.StringVar()
        self.plot_index = tk.StringVar()
        self.plot_value = tk.StringVar()
        self.plot_scale = 2

        self.source_fig1 = Figure(figsize=(2.5*self.plot_scale, self.plot_scale))
        self.source_ax1 = self.source_fig1.add_subplot()
        self.source_fig2 = Figure(figsize=(2.5*self.plot_scale, self.plot_scale))
        self.source_ax2 = self.source_fig2.add_subplot()
        self.target_fig1 = Figure(figsize=(2.5*self.plot_scale, self.plot_scale))
        self.target_ax1 = self.target_fig1.add_subplot()
        self.target_fig2 = Figure(figsize=(2.5*self.plot_scale, self.plot_scale))
        self.target_ax2 = self.target_fig2.add_subplot()

        self.source_fig1_canvas = FigureCanvasTkAgg(self.source_fig1, self.plot_window)
        self.source_fig1_canvas.get_tk_widget().grid(column=0, row=0)
        self.source_fig2_canvas = FigureCanvasTkAgg(self.source_fig2, self.plot_window)
        self.source_fig2_canvas.get_tk_widget().grid(column=0, row=1, pady=(0, 20))
        self.target_fig1_canvas = FigureCanvasTkAgg(self.target_fig1, self.plot_window)
        self.target_fig1_canvas.get_tk_widget().grid(column=1, row=0)
        self.target_fig2_canvas = FigureCanvasTkAgg(self.target_fig2, self.plot_window)
        self.target_fig2_canvas.get_tk_widget().grid(column=1, row=1, pady=(0, 20))

        tk.Label(self.legend_window, text='Coordinates [X, Y]', width=20).grid(column=0, row=0)
        tk.Label(self.legend_window, text='Indexes [i, j]', width=20).grid(column=1, row=0)
        tk.Label(self.legend_window, text='Values (Gy)', width=20).grid(column=2, row=0)
        self.plot_coord_label = tk.Label(self.legend_window, textvariable=self.plot_coord, width=10)
        self.plot_coord_label.grid(column=0, row=1, sticky='nsew')
        self.plot_index_label = tk.Label(self.legend_window, textvariable=self.plot_index, width=10)
        self.plot_index_label.grid(column=1, row=1, sticky='nsew')
        self.plot_value_label = tk.Label(self.legend_window, textvariable=self.plot_value, width=10)
        self.plot_value_label.grid(column=2, row=1, sticky='nsew')

        self.source_fig1_canvas.mpl_connect('motion_notify_event', self.hover_source_ax1)
        self.source_fig2_canvas.mpl_connect('motion_notify_event', self.hover_source_ax2)
        self.target_fig1_canvas.mpl_connect('motion_notify_event', self.hover_target_ax1)
        self.target_fig2_canvas.mpl_connect('motion_notify_event', self.hover_target_ax2)

if __name__ == '__main__':
    root = tk.Tk()
    DoseDistanceExtractor(root)
    root.mainloop()