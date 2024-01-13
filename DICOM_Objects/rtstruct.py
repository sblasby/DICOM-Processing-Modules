import numpy as np
from collections import namedtuple

from DicomModules.DICOM_Objects.Base_Class.dicom_processing import DicomProcessing
from DicomModules.Display_Modules.view_3D import View3D


class RtStruct(DicomProcessing):

    def __init__(self, FilePath: str):
        
        super().__init__(FilePath)
        
        self._roi_dict = {}


    def _dicom_file_checks(self):
        
        if (not hasattr(self, 'Modality')) or self.Modality != 'RTSTRUCT':
            
            raise TypeError(f"The modality attribute must be present and have a value of 'RTSTRUCT")
        
        elif (not hasattr(self, "ROIContourSequence")) or len(self.ROIContourSequence) <= 0:

            raise TypeError("The ROIContourSequence attribute must be present and have a length greater than 0")


    @property
    def ContourDataDict(self):
        '''
        Returns a dictionary with strings for keys
        and lists for values. The lists contain information
        regarding the regions of interest and the
        contour points within them.
        
        The items within each list are tuples that contain
        (X, Y, Z, OffSetVector). If the off set vector is not
        in the dicom then it is an empty list. The tuples within
        a list when stacked ontop of each other make a 3D contour
        of the ROI.
        '''

        def getXYZ(contour_data):

            X = []
            Y = []
            Z = []

            for coord in contour_data:
                
                if len(X) == len(Z):
                    X.append(coord)
                
                elif len(Y) < len(X):
                    Y.append(coord)
                
                else:
                    Z.append(coord)
            
            return np.array(X), np.array(Y), np.array(Z)

        Coords = namedtuple("Coordinates", ['x_values', 'y_values', 'z_values', 'offest_vector'])

        ## Check if the dictionary has been made yet  
        if self._roi_dict == {}:

            roi_num = 0

            for roi in self.ROIContourSequence:
                
                roi_num += 1

                # key = f'ROI{roi_num}'

                key = roi.ReferencedROINumber

                mapping_func = lambda item: Coords(*getXYZ(item.ContourData), item.get((0x3006, 0x0045), default = []))

                self._roi_dict[key] = list(map(mapping_func, roi.ContourSequence))

            return self._roi_dict
        
        else:
            return self._roi_dict
        
    
    def View3DContours(self):
        '''
        Display the 3D image of the contours of 
        all the ROIs in the associated RTSTRUCT
        '''

        contour_data = list(self.ContourDataDict.items())

        contour_data.sort(key= lambda n: n[0])

        contour_data = list(map(lambda item: item[1], contour_data))

        roi_data = []

        for roi in contour_data:
            
            X = []
            Y = []
            Z = []
            
            for contour_slice in roi:

                X.extend(contour_slice.x_values)

                Y.extend(contour_slice.y_values)

                Z.extend(contour_slice.z_values)
            
            roi_data.append((X,Y,Z))
        
        viewer = View3D(roi_data)

        viewer.mainloop()

