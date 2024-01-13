# Downloaded python packages
import numpy as np
from collections import namedtuple
import SimpleITK as sITK
from skimage import draw
import os

# From the Modules folder
from DicomModules.DICOM_Arrays.dicom_image_array import DicomImageArray
from DicomModules.DICOM_Objects.rtstruct import RtStruct
from DicomModules.Display_Modules.slice_viewer import SliceView
from DicomModules.DICOM_Arrays.dicom_array import DicomArray
from DicomModules.DICOM_Objects.dicom_image import DicomImage

class RtAndImage:
    
    '''
    Fields:
        _images: DicomArray
        _rt: DicomProcessing
        _roi_dict: Dictionary [str : list]

    Properties:
        Images -> DicomArray
        RtStruct -> DicomProcessing
    '''

    def __init__(self, images, rts):
        '''
        Returns an RtAndImage object after initalizing
        its fields

        images -> DicomArray
        rts -> DicomProcessing
        '''
        
        self.Images = images

        self.RtStruct = rts

        self._roi_dict = {}

    @property
    def Images(self):
        '''
        Returns the dicom images that are stored
        within the object
        '''
        return self._images

    @Images.setter
    def Images(self, value):
        
        if type(value) == DicomImageArray:
            self._images = value
        
        else:
            raise ValueError(f"The value set for images must be a DicomImageArray")
        
    @property
    def RtStruct(self):
        '''
        Returns the RtStruct stored within the
        object.
        '''
        return self._rt

    @RtStruct.setter
    def RtStruct(self, value):

        if type(value) != RtStruct:
            
            raise ValueError(f"The value being set must a RtStruct object instance")
        
        else:
            self._rt = value


    def ViewSlices(self, with_contours = True, sort_key = lambda dcm: dcm.ImagePositionPatient[2], cm = 'gray', **dicom_filters):
        
        '''
        Shows the slices stored in the image field
        of the object, in an interactive UI.

        Optional Arguments:
            
            with_contours: Boolean indicating whether or 
                            not to plot the contours ontop 
                            of the image. The default is True
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

        '''

        dcm_arr = self._images

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
            

        if with_contours:
            
            roi_dict = self._rt.ContourDataDict

            contour_data = [] 
            
            for roi in roi_dict.values():
                
                contour_data.extend(roi)

            contour_coords_dict = {}

            for X, Y, Z, _ in contour_data:

                if Z[0] in contour_coords_dict:

                    coords = contour_coords_dict[Z[0]]

                    coords[0] = np.concatenate((coords[0], X))

                    coords[1] = np.concatenate((coords[1], Y))

                else:

                    contour_coords_dict[Z[0]] = [np.array(X), np.array(Y)]
                       
            for ind in range(len(plotting_data)):

                z_value = dcm_arr[ind].SliceLocation

                if z_value in contour_coords_dict:
                    
                    x_scale = float(dcm_arr[ind].PixelSpacing[0])

                    y_scale = float(dcm_arr[ind].PixelSpacing[1])

                    x_data = contour_coords_dict[z_value][0]

                    y_data = contour_coords_dict[z_value][1]

                    coords = plotting_data[ind].ContourCoords

                    # Add the x and y data
                    coords[0] = np.concatenate((coords[0], x_data / x_scale))

                    coords[1] = np.concatenate((coords[1], y_data / y_scale))

            interactive = SliceView(plotting_data, cm)
            interactive.mainloop()
        
        else:

            self._images.ViewSlices(sort_key=sort_key, cm = cm, **dicom_filters)


    def GetRtMaskDict(self, background_value = 0, mask_value = 255):
        ''''
        Return a dicitonary where each
        key value pair consists of a sITK
        image representing a mask of an ROI.
        Dictionary keys are the "Referenced ROI 
        Numbers" from the RTSTRUCT file.
        '''

        mask_dict = {}

        dicom_img = self._images.sITKImage

        contour_dict = self._rt.ContourDataDict

        for roi_key in contour_dict:

            mask_dict[roi_key] = self._mask_for_roi(contour_dict[roi_key], dicom_img, background_value, mask_value)
        
        return mask_dict
    

    def SaveAsNii(self, saveDir : str):
        '''
        Saves the contour data and the associated
        images within the object as .nii.gz files
        to the folder saveDir

        Note: Ensure before saving that the dicoms
        stored within the object are properly filtered!

        saveDir: str representing the directory where
                    the resulting files are to be 
                    stored.
        
        '''

        if not os.path.isdir(saveDir):
            os.makedirs(saveDir)
        
        
        images2save = self.Images

        images2save.SaveImagesAsNii(saveDir + os.sep + 'images')

        masks = self.GetRtMaskDict()

        for key in masks.keys():

            sITK.WriteImage(masks[key], saveDir + os.sep + str(key) + '.nii.gz')


    @staticmethod
    def SelectDir():
        '''
        Returns a tuple of RtAndImage objects. Each item
        in the tuple is an RtAndImage object corresponding
        to a set of images and an RTSTRUCT
        '''

        dcm_array = DicomArray.SelectDir()

        return RtAndImage.GroupArray(dcm_array)
        

    @staticmethod
    def ProvideDir(filepath):
        '''
        Returns a tuple of RtAndImage objects. Each item
        in the tuple is an RtAndImage object corresponding
        to a set of images and an RTSTRUCT

        filepath -> A valid file path that points
                        to a directory with Dicom
                        files.
        '''
        
        all_dcms = DicomArray.ProvideDir(filepath)

        return RtAndImage.GroupArray(all_dcms)
    

    @staticmethod
    def GroupArray(dcm_array):

        '''
        Returns a tuple of RtAndImage objects after seaching
        through the DicomArray for RTSTRUCTS and their
        associated images.
        '''
        
        rtStructs = dcm_array.FilterDicoms(lambda dcm: dcm.Modality == 'RTSTRUCT')

        objs = []

        for struct in rtStructs:
            
            filterFunction = lambda dcm: (dcm.PatientID == struct.PatientID) \
                                    and (dcm.SOPClassUID in struct.SOPClassUID) \
                                    and (dcm.Modality != "RTSTRUCT")

            related_dcms = dcm_array.FilterDicoms(filterFunction)

            DicomImage_iterable = []

            for dcm in related_dcms:

                try:
                    DicomImage_iterable.append(DicomImage(dcm.filename))
                
                except:
                    continue
                    

            image_data = DicomImageArray(DicomImage_iterable)

            rt_data = RtStruct(struct.filename)

            objs.append(RtAndImage(image_data, rt_data))
        
        return tuple(objs)
    
    
    def _mask_for_roi(self, ROI : list, dicom_img, background_fill, mask_fill):

        img_shape = dicom_img.GetSize()

        mask = sITK.Image(img_shape, sITK.sitkUInt8)

        mask.CopyInformation(dicom_img)

        mask_array = sITK.GetArrayFromImage(mask)

        mask_array.fill(background_fill)

        for contour_coord in ROI:

            X, Y, Z = contour_coord.x_values, contour_coord.y_values, contour_coord.z_values
            
            points = np.zeros([len(contour_coord.x_values), 3])

            for ind in range(len(contour_coord.x_values)):
                
                world_coords = dicom_img.TransformPhysicalPointToContinuousIndex((X[ind], Y[ind], Z[ind]))
                
                points[ind, 0], points[ind, 1], points[ind, 2] = world_coords[0], world_coords[1], world_coords[2]
            
            z_coord = int(round(points[0,2]))

            shape_input = (img_shape[1], img_shape[0]) ## Not sure

            coord_input = np.column_stack((points[:, 1], points[:, 0]))

            polygon = draw.polygon2mask(shape_input, coord_input)

            new_mask = np.logical_xor(mask_array[z_coord, :, :], polygon)
            
            mask_array[z_coord, :, :] = np.where(new_mask, mask_fill, background_fill)

        resulting_mask = sITK.GetImageFromArray(mask_array)

        resulting_mask.CopyInformation(dicom_img)

        return resulting_mask

