import numpy as np
import SimpleITK as sITK
import os
from collections import namedtuple


from DicomModules.DICOM_Arrays.ABC.dicom_storage import DicomStorage
from DicomModules.DICOM_Objects.dicom_image import DicomImage
from DicomModules.Display_Modules.slice_viewer import SliceView

class DicomImageArray(DicomStorage):

    @property
    def sITKImage(self):
        '''
        Returns an sITK image object
        made from the images stored
        in the dicocm array
        '''

        file_name_list = self.MapDicoms(lambda dcm: dcm.filename)

        reader = sITK.ImageSeriesReader()

        reader.SetFileNames(file_name_list)

        return reader.Execute()


    def _pass_set_checks(self, value) -> bool:

        check = type(value) == DicomImage

        return check
        

    def ViewSlices(self, sort_key = lambda dcm: dcm.ImagePositionPatient[2], cm = 'gray', **dicom_filters):
        '''
        View the MR slices of the dicom in an interactive
        window, scrolling to move through the different
        slices.

        Optional Parameters:
            cm: Colour map for use by the plotting function
                    see matplotlib's color maps for more details.
                    The default is "gray"
            sort_key: The function describing how to sort the
                        images for viewing, by default they are
                        sorted by asscending z value
            
            **dicom_filters (filter parameters):
                Only the dicoms that have the key as an attribute and
                a matching value to dicom_filters[key] will have their
                images displayed

                Examples of possible dicom_filters:
                    Modality = "MR"
                    DiffusionBValue = 0.0
                    SliceLocation = 10
                    ...
        '''

        dcm_arr = self

        filters = list(filter(lambda s: not s.startswith('_'), dicom_filters.keys()))

        if not filters == []:

            for fKey in filters:

                dcm_arr = dcm_arr.FilterDicoms(lambda dcm: dcm[fKey].value == dicom_filters[fKey] if hasattr(dcm, fKey) else False)

        if dcm_arr._dicoms == []:

            msg = f"Empty DicomArray returned after applying the specified filters{': ' + ', '.join(filters)}"

            raise Exception(msg)

        dcm_arr.SortDicoms(sort_key)

        image_offset_func = lambda item: [(0.5 - float(num) / float(item.PixelSpacing[0])) for num in item.ImagePositionPatient[:2]]

        SliceViewerData = namedtuple("SliceViewerData", ["PixelData", "ContourCoords", "ContourOffset"])

        plotting_data = dcm_arr.MapDicoms(lambda dcm: SliceViewerData(dcm.pixel_array, [np.array([]),np.array([])], image_offset_func(dcm)))

        interactive = SliceView(plotting_data, cm)

        interactive.mainloop()


    def SaveImagesAsNii(self, save_path : str, include_gz = True):

        '''
        Saves the images within the image array as a .nii file or
        .nii.gz if include_gz = true

        save_path: str that contains the save path of the file,
                    should not include any file extensions
        '''
        
        dir_name = os.path.dirname(save_path)

        if not os.path.isdir(dir_name):
            
            os.makedirs(dir_name)
        
        img = self.sITKImage

        if include_gz:
            extension = '.nii.gz'
        
        else:
            extension = '.nii'
            
        sITK.WriteImage(img, save_path + extension)


    def _make_new_class(self, dicom_iter):
        return DicomImageArray(dicom_iter)
        
    
    @staticmethod
    def CreateEmpty():
        '''
        Returns an empty DicomImageArray
        '''
        return DicomImageArray([])


    @staticmethod
    def _array_data_type(path):
        return DicomImage(path)
