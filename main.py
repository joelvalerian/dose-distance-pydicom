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
        self.filepath_RTDOSE.set(filename)

    def getpath_RTSTRUCT(self):
        filename = tk.filedialog.askopenfilename(filetypes=[('DICOM files', '*.dcm')])
        self.filepath_RTSTRUCT.set(filename)

    def import_DICOM(self):
        try:
            RTDOSE = pydicom.dcmread(self.rtdose_filepath.get())
            RTSTRUCT = pydicom.dcmread(self.rtstruct_filepath.get())
            z_spacing = abs(RTSTRUCT.ROIContourSequence[0].ContourSequence[1].ContourData[2] - RTSTRUCT.ROIContourSequence[0].ContourSequence[0].ContourData[2])
            yx_spacing = [float(i) for i in RTDOSE.PixelSpacing]
            structure_list = [RTSTRUCT.StructureSetROISequence[i].ROIName for i in range(len(RTSTRUCT.StructureSetROISequence))]

            self.patient_id = RTDOSE.PatientID
            self.rtdose = RTDOSE.pixel_array * RTDOSE.DoseGridScaling
            self.rtdose_dimension = self.rtdose.shape
            self.rtdose_spacing = tuple([z_spacing, *yx_spacing])
            self.rtdose_origin = tuple([*RTDOSE.ImagePositionPatient])
            self.structure_list = structure_list

            self.patient_id_str.set(self.patient_id)
            self.rtdose_dimension_str.set(self.rtdose_dimension)
            self.rtdose_spacing_str.set(self.rtdose_spacing)
            self.rtdose_origin_str.set(f'{self.rtdose_origin[2]:.1f}, {self.rtdose_origin[1]:.1f}, {self.rtdose_origin[0]:.1f}')
            self.structure_list_var.set([str(i) + '. ' + structure_list[i] for i in range(len(structure_list))])

            self.update_combobox(self.importer_source_selection, structure_list)
            self.update_combobox(self.importer_target_selection, structure_list)

            self.import_status.set('Import success!')
            
        except FileNotFoundError:
            self.import_status.set('File(s) not found!')

        except pydicom.errors.InvalidDicomError:
            self.import_status.set('Invalid DICOM file(s)!')

        # except Exception:
        #     self.import_status.set('Unknown error!')

    def update_combobox(self, combobox, values):
        combobox['values'] = [*values]

    def source_on_selected(self, event):
        self.source_selected.set(event.widget.get())

    def target_on_selected(self, event):
        self.target_selected.set(event.widget.get())

    def plot(self):
        try:
            self.source_ax1_plot = self.source_ax1.imshow(self.rtdose[120])
            self.source_ax2_plot = self.source_ax2.imshow(self.rtdose[70])
            self.target_ax1_plot = self.target_ax1.imshow(self.rtdose[100])
            self.target_ax2_plot = self.target_ax2.imshow(self.rtdose[120])

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
            print(np.argmax(self.rtdose[120]))
        except AttributeError:
            self.plot_status.set('No DICOM imported!')

    def hover_source_ax1(self, event):
        if event.inaxes == self.source_ax1:
            x, y = event.xdata, event.ydata
            i, j = np.round(np.array((x, y))).astype(int)
            try:
                self.plot_coord.set(str([round(x, 3), round(y, 4)]))
                self.plot_index.set(str([i, j]))
                self.plot_value.set(str(round(self.rtdose[50][j][i], 3)))
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
                self.plot_value.set(str(round(self.rtdose[70][j][i], 3)))
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
                self.plot_value.set(str(round(self.rtdose[100][j][i], 3)))
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
                self.plot_value.set(str(round(self.rtdose[120][j][i], 3)))
            except AttributeError:
                self.plot_status.set('No DICOM imported!')
        else:
            self.plot_coord.set(str(''))
            self.plot_index.set(str(''))
            self.plot_value.set(str(''))

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
        self.header.grid(column=0, row=0)
        self.content = tk.Frame(self.body)
        self.content.grid(column=0, row=1)

        tk.Label(self.header, text='Importer').grid(column=0, row=0)
        self.importer = tk.Frame(self.header)
        self.importer.grid(column=0, row=1)

        self.rtdose_filepath = tk.StringVar(value='C:/Users/ivand/OneDrive/Desktop/RD1.dcm')
        self.rtstruct_filepath = tk.StringVar(value='C:/Users/ivand/OneDrive/Desktop/RS1.dcm')
        self.import_status = tk.StringVar(value='No files imported')
        self.plot_status = tk.StringVar(value='No plot yet')
        self.source_selected = tk.StringVar(value='No source selected')
        self.target_selected = tk.StringVar(value='No target selected')
        self.structure_list = []

        tk.Label(self.importer, text='RTDOSE').grid(column=0, row=0, sticky='e')
        tk.Label(self.importer, text='RTSTUCT').grid(column=0, row=1, sticky='e')

        self.importer_rtdose_filepath = tk.Entry(self.importer, textvariable=self.rtdose_filepath)
        self.importer_rtdose_filepath.grid(column=1, row=0, sticky='w')
        self.importer_rtstruct_filepath = tk.Entry(self.importer, textvariable=self.rtstruct_filepath)
        self.importer_rtstruct_filepath.grid(column=1, row=1, sticky='w')
        self.importer_import_status = tk.Label(self.importer, textvariable=self.import_status)
        self.importer_import_status.grid(column=1, row=2)
        
        self.importer_rtdose_button = tk.Button(self.importer, text='...', command=self.getpath_RTDOSE)
        self.importer_rtdose_button.grid(column=2, row=0)
        self.importer_rtstruct_button = tk.Button(self.importer, text='...', command=self.getpath_RTSTRUCT)
        self.importer_rtstruct_button.grid(column=2, row=1)
        self.importer_import_button = tk.Button(self.importer, text='Import', command=self.import_DICOM)
        self.importer_import_button.grid(column=2, row=2, sticky='n')

        tk.Label(self.importer, text='Contour Selection').grid(column=1, row=3)
        tk.Label(self.importer, text='Source').grid(column=0, row=4)
        tk.Label(self.importer, text='Target').grid(column=0, row=5)
        
        self.importer_source_selection = ttk.Combobox(self.importer, values=self.structure_list)
        self.importer_source_selection.grid(column=1, row=4)
        self.importer_source_selection.bind('<<ComboboxSelected>>', self.source_on_selected)
        self.importer_target_selection = ttk.Combobox(self.importer, values=self.structure_list)
        self.importer_target_selection.grid(column=1, row=5)
        self.importer_target_selection.bind('<<ComboboxSelected>>', self.target_on_selected)
        self.importer_plot_status = tk.Label(self.importer, textvariable=self.plot_status)
        self.importer_plot_status.grid(column=1, row=6)

        self.importer_source_selected = tk.Label(self.importer, textvariable=self.source_selected)
        self.importer_source_selected.grid(column=2, row=4)
        self.importer_target_selected = tk.Label(self.importer, textvariable=self.target_selected)
        self.importer_target_selected.grid(column=2, row=5)
        self.importer_plot_button = tk.Button(self.importer, text='Plot', command=self.plot)
        self.importer_plot_button.grid(column=2, row=6)

        tk.Label(self.header, text='Patient Information').grid(column=1, row=0)
        self.information = tk.Frame(self.header)
        self.information.grid(column=1, row=1)

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
        self.source_fig2_canvas.get_tk_widget().grid(column=0, row=1)
        self.target_fig1_canvas = FigureCanvasTkAgg(self.target_fig1, self.plot_window)
        self.target_fig1_canvas.get_tk_widget().grid(column=1, row=0)
        self.target_fig2_canvas = FigureCanvasTkAgg(self.target_fig2, self.plot_window)
        self.target_fig2_canvas.get_tk_widget().grid(column=1, row=1)

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