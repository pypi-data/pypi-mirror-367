from yta_google_drive_downloader.utils import parse_url, get_filename_from_url, get_id_from_url
from yta_google_drive_downloader.downloader import GoogleDriveDownloader
from yta_file.filename.handler import FilenameHandler
from yta_file.handler import FileHandler
from yta_validation.parameter import ParameterValidator
from yta_temp import Temp
from typing import Union


class GoogleDriveResource:
    """
    Class to handle Google Drive Resources. Just instantiate
    it with its Google Drive url and it will be ready for
    download if the url is valid and available.

    A valid 'drive_url' must be like this:
    https://drive.google.com/file/d/1rcowE61X8c832ynh0xOt60TH1rJfcJ6z/view?usp=sharing&confirm=1
    """

    @property
    def id(
        self
    ) -> str:
        """
        The id of the resource, extracted from the given url.
        """
        if not hasattr(self, '_id'):
            self._id = get_id_from_url(self.url)

        return self._id
    
    @property
    def filename(
        self
    ) -> str:
        """
        The filename of the original resource as stored in
        Google Drive. It includes the extension.
        """
        if not hasattr(self, '_filename'):
            self._filename = get_filename_from_url(self.url)

        return self._filename
    
    # TODO: Maybe create 'file_name' (?)
    
    @property
    def extension(
        self
    ) -> str:
        """
        The extension of the original resource as stored in
        Google Drive. It doesn't include the dot '.'.
        """
        return FilenameHandler.get_extension(self.filename)

    def __init__(
        self,
        drive_url: str
    ):
        """
        Initialize the instance by setting the provided 'drive_url',
        that must be a valid one. This method will fire a GET request
        to obtain the real resource filename (if a valid resource).

        This method will raise an Exception if the 'drive_url'
        parameter is not a valid, open and sharable Google Drive
        url.
        """
        ParameterValidator.validate_mandatory_string('drive_url', drive_url, do_accept_empty = False)

        self.url = parse_url(drive_url)
        """
        The shareable url that contains the resource id.
        """
        # Force 'filename' to be obtained firing the request
        if self.filename is None:
            raise Exception('No original "filename" found, so it is not accesible.')

    def download(
        self,
        output_filename: Union[str, None] = None,
        do_force: bool = False
    ) -> str:
        """
        Download the Google Drive resource to the local
        storage with the given 'output_filename'. If the
        given 'output_filename' exists, it will be 
        returned unless the 'do_force' parameter is set
        as True.

        This method returns the filename from the local
        storage.
        """
        ParameterValidator.validate_string('output_filename', output_filename)
        ParameterValidator.validate_mandatory_bool('do_force', do_force)

        return (
            output_filename
            if (
                not do_force and
                output_filename is not None and
                FileHandler.is_file(output_filename)
            ) else
            GoogleDriveDownloader.download(self, output_filename)
        )

class Resource:
    """
    Class to wrap the functionality related to
    a resource that can be obtained from the 
    local storage or from Google Drive.

    This class has been created to simplify the
    way we work with resources and the way we 
    use them in our applications.
    
    If you instantiate a resource always with the
    same 'output_filename', that will guarantee
    that the file is only downloaded when needed
    so you can use that resource in many different
    parts of the project but downloading it only
    once.
    """

    @property
    def is_google_drive_resource(
        self
    ) -> bool:
        """
        Boolean that indicates if the resource is a
        Google Drive resource.
        """
        return self._google_drive_resource is not None

    @property
    def google_drive_resource(
        self
    ) -> Union[GoogleDriveResource, None]:
        """
        The GoogleDriveResource instance if the resource
        is of this type.
        """
        return self._google_drive_resource
    
    @property
    def filename(
        self
    ) -> str:
        """
        The filename of the file that can be used as the
        resource. This file is stored locally but can come
        from the Google Drive platform or from the local
        storage.

        This filename is the one that will be used to store
        the file locally but it doesn't guarantee that the
        file has been downloaded previously and it exist.
        Use the 'file' property if you want to be sure that
        it exist because it forces the download.
        """
        return (
            self._output_filename
            if self._output_filename is not None else
            Temp.get_custom_wip_filename(f'google_drive_{self.google_drive_resource.id}')
            if self.is_google_drive_resource else
            self._filename_or_google_drive_url
        )
    
    @property
    def is_ready(
        self
    ) -> bool:
        """
        Check if the file already exist and has been
        previously downloaded so its ready to use.
        """
        return FileHandler.is_file(self.filename)
    
    @property
    def file(
        self
    ) -> str:
        """
        Get the resource (by downloading it if
        necessary) and return the filename of it
        ready to be used.
        """
        if not self.is_ready:
            if self.is_google_drive_resource:
                self.google_drive_resource.download(self.filename, do_force = True)
            elif self._output_filename != self.filename:
                FileHandler.copy_file(self._output_filename, self.filename)

        return self.filename
    
    def __init__(
        self,
        filename_or_google_drive_url: str,
        output_filename: str = None
    ) -> None:
        ParameterValidator.validate_mandatory_string('filename_or_google_drive_url', filename_or_google_drive_url, do_accept_empty = False)
        ParameterValidator.validate_string('output_filename', output_filename)

        try:
            self._google_drive_resource = GoogleDriveResource(filename_or_google_drive_url)
        except:
            self._google_drive_resource = None

        self._filename_or_google_drive_url = filename_or_google_drive_url
        """
        The filename or the Google Drive url to obtain
        the resource.
        """
        self._output_filename = output_filename
        """
        The filename with which the file will be stored
        locally even if it has to be downloaded from 
        Google Drive.
        """