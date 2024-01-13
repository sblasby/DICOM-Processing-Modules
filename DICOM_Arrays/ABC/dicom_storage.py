# Downloaded python packages
from glob import glob
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import warnings


from abc import ABC, abstractmethod


from DicomModules.DICOM_Objects.Base_Class.dicom_processing import DicomProcessing

class DicomStorage(ABC):
    '''
    Class that provides methods for arrays of DicomProcessing objects.
    They can be iterated, sliced and indexed exactly like a list.

    fields:
        _dicoms -> List of DicomProcssing

    Properties:
        Dicoms -> Settable property that
                    assigns the dicoms to
                    the object
    '''

    @abstractmethod
    def _pass_set_checks(self, value) -> bool:
        '''
        Method must be overidden in the subclass.
        The point of this method is too allow 
        subclasses to preform additional checks
        on the data before adding DICOMs to the 
        _dicoms list field. Should return a boolean 
        indicating whether or not all the 
        additional checks have passed!
        '''
        pass

    @staticmethod
    @abstractmethod
    def CreateEmpty():
        '''
        A static method to be defined in 
        the subclass that returns an instance 
        with no dicoms inside
        '''
        pass

    @staticmethod
    @abstractmethod
    def _array_data_type(path):
        '''
        A static method to be overloaded
        by a method that returns the instantiaited
        data type to be stored in the array.
        '''
        pass

    @abstractmethod
    def _make_new_class(self, dicom_iter):
        '''
        A method ment to be overidden that
        instantiates an instance of the class given
        a iterable filled with DICOM_Objects
        '''
        pass


    def __init__(self, DicomProcessing_iter):

        self.Dicoms = DicomProcessing_iter


    def __getitem__(self,index):
        '''
        Indexing works identically to list
        slicing/indexing
        '''

        if isinstance(index, int):
            return self._dicoms[index]
        
        elif isinstance(index, slice):

            selected_dicoms = self._dicoms[index]

            return self._make_new_class(selected_dicoms)


    def __setitem__(self, index, value):

        if not issubclass(type(value), DicomProcessing):
            raise ValueError("The assigned value must be a DicomProcessing object")
        
        elif isinstance(index, int):
            self._dicoms[index] = value

        else:
            raise IndexError("The index must be an integer")
    

    def __iter__(self):
        
        for dicom in self._dicoms:

            yield dicom


    @property
    def Dicoms(self):
        '''
        Write only property, attempting to
        get the Dicoms will result in 
        error. To access items in the list
        use indexing or iteration.
        '''
        raise AttributeError("Dicoms is not an accessable property, it can only be set")
    

    @Dicoms.setter
    def Dicoms(self, value):
        '''
        Sets the value of the dicoms stored in the object,
        and checks to make sure that data types are correct
        '''

        self._dicoms = []

        try:
            for ele in value:

                if not issubclass(type(ele), DicomProcessing):
                    raise ValueError("Not all elements within the argument are DicomProcessing objects")

                if not self._pass_set_checks(ele):
                    print(f'Dicom with file path {ele.filename}\nDid not pass the checks and was not added to DicomImageArray instance')
                    continue

                self._dicoms.append(ele)

        except Exception as e:

            raise Exception(e)
        

    def Length(self):
        '''
        Returns an int representing the number
        of DICOMs stored within the array.
        '''
        return len(self._dicoms)

    def GetCommonAttributes(self, write_file = False):
        '''
        Returns a list of the DICOM attributes that
        are common between the DICOMS stored in the object. 
        If write_file is True, then additionaly creates a 
        txt file in the current working directory. The file 
        contains the names of all the DICOM attributes that 
        are common between all the DICOM files stored in the array

        Effects:
            - If write_file is true, any txt file
                in current working directory with
                name "Common_Attributes.txt" will
                be overwritten
        '''

        common_attrs = []

        for dcm in self._dicoms:
            
            dcm_attr = dcm.dir()

            if common_attrs == []:
                common_attrs = dcm_attr
            
            else:
                common_attrs = list(filter(lambda attr: attr in dcm_attr, common_attrs))


        if write_file:
            file = os.getcwd() + os.sep + 'Common_Attributes.txt'

            with open(file, mode='w') as fopen:

                data = '\n'.join(common_attrs)

                fopen.write(data)

        return common_attrs

    def SortDicoms(self, sort_key):
        '''
        Returns None and mutates the object by 
        sorting the Dicoms stored in the object 
        by the specified key "sort_key".

        sort_key: A function that returns the result
                    to be sorted on. Must return something
                    that can be compared for equality
        '''

        self._dicoms.sort(key=sort_key)
    
    def ClassName(self):

        T = str(type(self))

        T = T.replace("<", "")

        sList = T.split(" ")

        full_name = sList[0]

        class_name = full_name.split('.')[-1]

        return class_name


    def Append(self, dicomprocessing):
        '''
        Mutates the array stored within the object by placing
        argument "dicomprocessing" at the end of the array

        dicomprocessing -> DicomProcessing object
        '''

        if issubclass(type(dicomprocessing), DicomProcessing):
            
            if self._pass_set_checks(dicomprocessing):

                self._dicoms.append(dicomprocessing)
        
        else:
            raise TypeError("Argumnet is not a DicomProcessing object")
        
    def MapDicoms(self, func):
        '''
        Returns a list after mapping the function
        "func" over all the DicomProcessing objects
        stored within the object

        func -> a function that can be applied to a
                DicomProcessing object
        '''
        return list(map(func, self._dicoms))

    def FilterDicoms(self, func):
        '''
        Returns a DicomArray of all the stored elements 
        for which the function "func" evaluates to 
        true

        func -> a function that can be applied to a
                DicomProcessing object and returns a
                boolean
        '''

        filtered = filter(func, self._dicoms)

        return self._make_new_class(filtered)
    
    # def CreateCopy(self):
    #     '''
    #     Returns a new DicomArray instance by
    #     reading the files associated with the 
    #     DicomArray. 
        
    #     Note:
    #     Any changes made that have not been saved 
    #     to the file will not be present in the copy
    #     '''

    #     filepaths = self.MapDicoms(lambda dcm: dcm.filename)

    #     return DicomArray(map(lambda file: DicomArray(file), filepaths))


    @classmethod
    def SelectDir(cls):

        '''
        Prompts the user for a directory then
        returns a DicomArray object containg all 
        the dicoms in the folder that meet the 
        requirements set by the method _pass_set_checks
        '''

        root = tk.Tk()

        root.withdraw()
        
        directory = filedialog.askdirectory(title="Location of DICOM files")

        if not directory:
            
            raise InterruptedError('User does not wish to proceed')
        
        dcmFiles = glob(directory + '\*.dcm')

        if not dcmFiles:

            messagebox.showerror("Error", "No DICOM files found in specified directory")
            
            raise FileNotFoundError('No files exist in the specified directory') 
        
        dicom_arr = cls.CreateEmpty()

        for path in dcmFiles:

            dicom_arr.Append(cls._array_data_type(path))
        
        return dicom_arr

    @classmethod
    def ProvideDir(cls, dirPath):

        '''
        Finds all DICOM files in the specified directory
        and returns a DicomArray object containg all the
        dicoms in the folder that meet the standard set by
        the abstract method _pass_set_checks
        '''

        root = tk.Tk()

        root.withdraw()

        if not os.path.isdir(dirPath):
            
            raise ValueError("The provided file path is not a real directory on this system")
        
        dcmFiles = glob(dirPath + '\*.dcm')

        if not dcmFiles:

            messagebox.showerror("Error", "No DICOM files found in specified directory")
            
            raise FileNotFoundError('No files exist in the specified directory') 
        
        dicom_arr = cls.CreateEmpty()

        for path in dcmFiles:

            dicom_arr.Append(cls._array_data_type(path))
        
        return dicom_arr