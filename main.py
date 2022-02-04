import tkinter as tk
import tkinter.ttk as ttk
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import csv
import cv2 as cv
import math

class DoseDistanceExtractor:
    def getpath_RTDOSE(self):
        filename = tk.filedialog.askopenfilename(filetypes=[('DICOM files', '*.dcm')])
        self.filepath_RTDOSE.set(filename)

    def getpath_RTSTRUCT(self):
        filename = tk.filedialog.askopenfilename(filetypes=[('DICOM files', '*.dcm')])
        self.filepath_RTSTRUCT.set(filename)

    def import_DICOM(self):
        try:
            self.RTDOSE = pydicom.dcmread(self.filepath_RTDOSE.get())
            self.RTSTRUCT = pydicom.dcmread(self.filepath_RTSTRUCT.get())
            self.status.set('Import success!')
            self.dose_array = self.RTDOSE.pixel_array * self.RTDOSE.DoseGridScaling
            self.patientID.set(self.RTDOSE.PatientID)
            self.dose_array_dimension.set(self.dose_array.shape)
            self.dose_z_spacing = abs(self.RTSTRUCT.ROIContourSequence[0].ContourSequence[1].ContourData[2] - self.RTSTRUCT.ROIContourSequence[0].ContourSequence[0].ContourData[2])
            self.dose_yx_spacing = [float(i) for i in self.RTDOSE.PixelSpacing]
            self.dose_array_spacing.set(tuple([self.dose_z_spacing, *self.dose_yx_spacing]))
            self.image_position = tuple([*self.RTDOSE.ImagePositionPatient])
            self.origin_coordinate.set(f'{self.image_position[2]:.1f}, {self.image_position[1]:.1f}, {self.image_position[0]:.1f}')
            self.structure_list = [self.RTSTRUCT.StructureSetROISequence[i].ROIName for i in range(len(self.RTSTRUCT.StructureSetROISequence))]
            self.structure_list_var.set([str(i) + '. ' + self.structure_list[i] for i in range(len(self.structure_list))])
            
        except FileNotFoundError:
            self.status.set('File(s) not found!')

        except pydicom.errors.InvalidDicomError:
            self.status.set('Invalid DICOM file(s)!')

        except Exception:
            self.status.set('Unknown error!')
    
    def __init__(self, root):
        root.title("Dose Distance Extractor")
        mainframe = ttk.Frame(root, padding="10 10 10 10")
        mainframe.grid(column=0, row=0)
        ttk.Label(mainframe, text='Dose Distance Extractor').grid(column=0, row=0)
        body = ttk.Frame(mainframe)
        body.grid(column=0, row=1)
        header = ttk.Frame(body)
        header.grid(column=0, row=0)
        content = ttk.Frame(body)
        content.grid(column=0, row=1)
        ttk.Label(header, text='Importer').grid(column=0, row=0)
        importer = ttk.Frame(header)
        importer.grid(column=0, row=1, sticky=tk.N)
        ttk.Label(header, text='Patient Information').grid(column=1, row=0)
        information = ttk.Frame(header)
        information.grid(column=1, row=1)
        
        ttk.Label(importer, text='RTDOSE').grid(column=0, row=0, sticky=tk.E)
        self.filepath_RTDOSE = tk.StringVar(value='Click the ... button to search DICOM file')
        ttk.Entry(importer, textvariable=self.filepath_RTDOSE, width=40).grid(column=1, row=0, sticky=tk.W)
        ttk.Button(importer, text='...', command=self.getpath_RTDOSE).grid(column=2, row=0)
        ttk.Label(importer, text='RTSTRUCT').grid(column=0, row=1, sticky=tk.E)
        self.filepath_RTSTRUCT = tk.StringVar(value='Click the ... button to search DICOM file')
        ttk.Entry(importer, textvariable=self.filepath_RTSTRUCT, width=40).grid(column=1, row=1, sticky=tk.W)
        ttk.Button(importer, text='...', command=self.getpath_RTSTRUCT).grid(column=2, row=1)
        self.status = tk.StringVar(value='')
        ttk.Label(importer, textvariable=self.status).grid(column=1, row=2)
        ttk.Button(importer, text='Import', command=self.import_DICOM).grid(column=2, row=2)

        ttk.Label(information, text='Patient ID').grid(column=0, row=0)
        self.patientID = tk.StringVar()
        ttk.Entry(information, textvariable=self.patientID, state=tk.DISABLED).grid(column=1, row=0)
        ttk.Label(information, text='Dose Array Dimension').grid(column=0, row=1)
        self.dose_array_dimension = tk.StringVar()
        ttk.Entry(information, textvariable=self.dose_array_dimension, state=tk.DISABLED).grid(column=1, row=1)
        ttk.Label(information, text='Dose Array Spacing').grid(column=0, row=2)
        self.dose_array_spacing = tk.StringVar()
        ttk.Entry(information, textvariable=self.dose_array_spacing, state=tk.DISABLED).grid(column=1, row=2)
        ttk.Label(information, text='Origin Coordinate').grid(column=0, row=3)
        self.origin_coordinate = tk.StringVar()
        ttk.Entry(information, textvariable=self.origin_coordinate, state=tk.DISABLED).grid(column=1, row=3)
        ttk.Label(information, text='Structure List').grid(column=0, row=4, sticky=tk.N)
        self.structure_list_var = tk.StringVar()
        tk.Listbox(information, listvariable=self.structure_list_var, height=5, activestyle='none').grid(column=1, row=4)

        tk.Label(content, text='AAAA').grid(column=0, row=0)
        
        for child in header.winfo_children(): 
            child.grid_configure(padx=10, pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    DoseDistanceExtractor(root)
    root.mainloop()
