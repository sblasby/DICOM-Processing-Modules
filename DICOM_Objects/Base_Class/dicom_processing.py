# Downloaded python packages
import pydicom as pd
from pydicom import filereader
from pydicom.uid import UID
from pydicom.filewriter import write_file_meta_info
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
import os

import pydicom as pd


class DicomProcessing(pd.FileDataset):

    '''
    Class that aids in dicom file processing.
    It inheirts from the pydicom FileDataset
    object. As a result the DicomProcessing
    object has all the fields and methods
    that a pydicom FileDataset object has.
    '''

    def __init__(self, FilePath : str):

        '''
        Returns a DicomProcessing object

        FilePath -> Str that represents a full 
                    file path to a valid .dcm file
        
        Optional parameters

        FileMetaInfo -> Object created by pydicoms 
                            FileMetaDataset function
        '''

        dataSet = pd.dcmread(FilePath)

        metaInfo = filereader.read_file_meta_info(FilePath)

        super().__init__(FilePath, dataSet, file_meta=metaInfo)


    # def Copy(self):
    #     '''
    #     Reutrns a new object instance containing
    #     all the data stored withing the
    #     DICOM file associated with the object.
    #     If updates have been made to the data, and
    #     they have not been saved into a dicom
    #     '''

    #     return DicomProcessing(self.filename)

    def WriteAttributesTxt(self, filename : str):

        '''
        This method will write a .txt file to the current working directory. 
        The file contains all of the names of all the attributes that are 
        stored in the object contains

        filename -> Str that is the name of the txt file to create
                        (e.g. "Names.txt")
        '''
        
        fpath = os.getcwd() + os.path.sep + filename

        if os.path.isfile(fpath):
            
            root = tk.Tk()
            
            root.withdraw()

            message = 'The file which you want to write to already exists in the current directory. In proceeding, the contents' + \
                        f' of the file {filename} will be overridden. Do you wish to proceed?'

            answer = messagebox.askyesno('File Exists', message)

            if answer:
                method = 'w'
            
            else:
                raise InterruptedError("User does not want to continue")
            
        else:
            method = 'x'

            
        with open(fpath, method) as fopen:

            header = f'DICOM attributes for file on path: {self.filename}\n'

            attr = '\n'.join(self.dir())

            fopen.write(header)

            fopen.write(attr)
    
    
    def PrintDicomAttributes(self):
        '''
        Returns None and prints all the dicom
        object attributes to the console

        Effects:
            - prints to the console

        '''
        
        s = '\n'.join(self.dir())

        print(s)


    @classmethod
    def SelectFile(cls):
        '''
        Returns a DicomProcessing object containing the
        data in the selected file
        '''
        root = tk.Tk()

        root.withdraw()

        filePath = filedialog.askopenfilename(filetypes=[('DICOM Files', '*.dcm')])

        if not filePath:
            raise InterruptedError('User does not wish to proceed')
        
        return cls(filePath)
    

    @staticmethod
    def CreateNewDicom(SavePath : str, FileMetaDataDict, DicomAttributeDict = None):
        '''
        Creates a DicomProcessing object for the intention
        of creating a new dicom file.

        Required Parameters:
            SavePath: A str representing the full path to where you would
                        like the dicom to be saved
            FileMetaData: A dictionary that contains the following key 
                            value pairs:
                                    
                                    MediaStorageSOPClassUID : str
                                    MediaStorageSOPInstanceUID : str
                                    TransferSyntaxUID : str

                            Other header info can be added, check the
                            DICOM standard part 10 chapter 7.
                            

        Optional Parameters:
            DicomAttributeDict: A dicitonary with keys and values of
                                    type str. The keys must be the name 
                                    of a valid dicom attribute. If this
                                    is true then the dicom attribute with
                                    that name will be populated by the 
                                    key's associated value.
        '''

        if DicomAttributeDict is None:
            DicomAttributeDict = {}

        required_keys = [  
                         "MediaStorageSOPClassUID",
                         "MediaStorageSOPInstanceUID",
                         "TransferSyntaxUID"
                         ]
        
        for req in required_keys:

            if not req in FileMetaDataDict:
                raise ValueError(f"Assure FileMetaDataDict has the following keys {required_keys}")

        method = 'xb'
        
        if not SavePath.endswith('.dcm'):

            SavePath = SavePath + '.dcm'

        if os.path.isfile(SavePath):
            
            root = tk.Tk()
            root.withdraw()

            user_answer = messagebox.askyesno("File Exists", f"File on path\n{SavePath}\nAlready exists, do you wish to overwrite it?")

            if not user_answer:
                raise InterruptedError("User decided not to overwrite the file")
            
            else:
                method = 'wb'

        fmd = pd.Dataset()

        for key in required_keys:
            
            if key.endswith("UID"):

                FileMetaDataDict[key] = UID(FileMetaDataDict[key])
            
            setattr(fmd, key, FileMetaDataDict[key])

        with open(SavePath, method) as fopen:
            
            preamble = b'\x00' * 128

            fopen.write(preamble)

            fopen.write(b'DICM')

            write_file_meta_info(fopen, fmd, enforce_standard=True)

        dcm = pd.dcmread(SavePath)
        # dcm = cls(SavePath)

        for key in DicomAttributeDict:

            setattr(dcm, key, DicomAttributeDict[key])

        pd.dcmwrite(SavePath, dcm, write_like_original=False)

        return None
    