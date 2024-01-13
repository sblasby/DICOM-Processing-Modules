import matplotlib.pyplot as plt

from DicomModules.DICOM_Objects.Base_Class.dicom_processing import DicomProcessing


class DicomImage(DicomProcessing):

    def __init__(self, FilePath: str):
        
        super().__init__(FilePath)


    def _dicom_file_checks(self):
        
        if not hasattr(self, 'PixelData') or self.get('PixelData') == None:
            raise TypeError("Attempted to create a DicomImage object from a DICOM file that does not have any pixel data")


    def ViewImage(self):
        '''
        Displays the image made from the pixel data
        using the bone colour map from matplotlib
        '''
            
        fig, axs = plt.subplots()

        axs.imshow(self.pixel_array, cmap = plt.cm.bone)

        plt.show()
    
    def NormalizePixelArray(self, upper):
        '''
        Returns None and mutates the pixel_array
        so that the array is normalized between
        0 and upper
        stored in the object, normalizing it.

        Effects:
            - Mutates the object
        '''

        data = self.pixel_array / self.pixel_array.max() * upper

        self.PixelData = data.tobytes()
        
        return None
