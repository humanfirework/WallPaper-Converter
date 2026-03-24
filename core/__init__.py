# Core modules
from .mpkg_converter import MPKGParser, MPKGFile, mpkg_to_mp4, batch_mpkg_to_mp4, is_mpkg_file
from .ncm_converter import (
    is_ncm_file, 
    get_ncm_info, 
    ncm_to_audio, 
    batch_ncm_to_audio
)

__all__ = [
    # MPKG
    'MPKGParser',
    'MPKGFile', 
    'mpkg_to_mp4',
    'batch_mpkg_to_mp4',
    'is_mpkg_file',
    # NCM
    'is_ncm_file',
    'get_ncm_info',
    'ncm_to_audio',
    'batch_ncm_to_audio',
]