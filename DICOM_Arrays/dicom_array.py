

from DicomModules.DICOM_Arrays.ABC.dicom_storage import DicomStorage
from DicomModules.DICOM_Objects.Base_Class.dicom_processing import DicomProcessing



class DicomArray(DicomStorage):


    def _pass_set_checks(self, value) -> bool:
        return True

    @staticmethod
    def CreateEmpty():
        return DicomArray([])
    
    @staticmethod
    def _array_data_type(path):
        return DicomProcessing(path)
    
    def _make_new_class(self, dicom_iter):
        return DicomArray(dicom_iter)