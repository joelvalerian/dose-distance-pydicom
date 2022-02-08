import tkinter as tk
import tkinter.ttk as ttk
import pydicom
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
import cv2 as cv
import math

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
            self.source_ax1.imshow(self.rtdose[50])
            self.source_ax2.imshow(self.rtdose[70])
            self.source_canvas = FigureCanvasTkAgg(self.source_fig, self.plot_window)
            self.source_canvas.draw()
            self.source_canvas.get_tk_widget().grid(column=0, row=0)
            self.target_ax1.imshow(self.rtdose[100])
            self.target_ax2.imshow(self.rtdose[120])
            self.target_canvas = FigureCanvasTkAgg(self.target_fig, self.plot_window)
            self.target_canvas.draw()
            self.target_canvas.get_tk_widget().grid(column=1, row=0)
            self.plot_status.set('Plotted!')

        except AttributeError:
            self.plot_status.set('No DICOM imported!')

    def __init__(self, root):
        self.root = root
        self.root.title('Dose Distance Extractor')

        self.mainframe = tk.Frame(self.root, bd=0)
        self.mainframe.grid(column=0, row=0)
        
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
        self.plot_window = tk.Frame(self.content)
        self.plot_window.grid(column=0, row=1)

        self.source_fig = Figure(figsize=(4, 4))
        self.source_ax1 = self.source_fig.add_subplot(211)
        self.source_ax2 = self.source_fig.add_subplot(212)

        self.target_fig = Figure(figsize=(4, 4))
        self.target_ax1 = self.target_fig.add_subplot(211)
        self.target_ax2 = self.target_fig.add_subplot(212)

        self.source_canvas = FigureCanvasTkAgg(self.source_fig, self.plot_window)
        self.source_canvas.draw()
        self.source_canvas.get_tk_widget().grid(column=0, row=0)

        self.target_canvas = FigureCanvasTkAgg(self.target_fig, self.plot_window)
        self.target_canvas.draw()
        self.target_canvas.get_tk_widget().grid(column=1, row=0)

if __name__ == '__main__':
    root = tk.Tk()
    DoseDistanceExtractor(root)
    root.mainloop()