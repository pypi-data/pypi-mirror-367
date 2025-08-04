from yta_constants.google_drive import DRIVE_RESOURCE_URL, CONFIRMATION_STRING, FILE_NOT_FOUND_ERROR_STRING
from lxml.html import fromstring
from typing import Union

import requests


def _force_https(
    drive_url: str
) -> str:
    """
    Replace the 'http://' substring by 'https://' if
    necessary.
    """
    return drive_url.replace('http://', 'https://')

def parse_url(
    drive_url: str
) -> str:
    """
    Validate the provided 'drive_url' and return it if
    valid, with some modifications if needed.

    [ ! ] This method will raise an Exception if the
    'drive_url' parameter is not a valid, open and
    shareable Google Drive url.
    """
    drive_url = _force_https(drive_url)

    # Force 'https'
    drive_url = (
        f'https://{drive_url}'
        if not drive_url.startswith('https://') else
        drive_url
    )

    if not drive_url.startswith(DRIVE_RESOURCE_URL):
        raise Exception(f'Provided "google_drive_url" parameter {drive_url} is not valid. It must be like "{DRIVE_RESOURCE_URL}..."')

    return (
        # previously was '&confirm=1' to avoid virus scan as they say:
        # https://github.com/tensorflow/datasets/issues/3935#issuecomment-2067094366
        f'{drive_url}&{CONFIRMATION_STRING}'
        if not CONFIRMATION_STRING in drive_url else
        drive_url
    )

def get_id_from_url(
    drive_url: str
) -> str:
    """
    Parse the provided 'drive_url' and return the Google Drive
    resource id if the url is valid.

    This method will raise an Exception if the 'drive_url'
    parameter is not a valid, open and sharable Google Drive
    url.
    """
    return parse_url(drive_url).replace(DRIVE_RESOURCE_URL, '').split('/')[0]

def get_filename_from_url(
    drive_url: str
) -> Union[str, None]:
    """
    Parse the provided 'drive_url' and return the Google Drive
    resource filename (as stored in Google Drive) if the url is
    valid.

    This is the real filename in Google Drive, so its extension
    should be also the real one.

    (!) This method will fire a GET request to the Google Drive
    url if valid to obtain the metadata.

    This method will return None if the 'drive_url' parameter
    provided is not a valid, open and sharable Google Drive
    url.
    """
    response_content = requests.get(parse_url(drive_url)).content

    return (
        fromstring(response_content).findtext('.//title').split('-')[0].strip()
        if FILE_NOT_FOUND_ERROR_STRING not in response_content.decode('utf-8') else
        None
    )

def is_valid_shareable_google_drive_url(
    drive_url: str
) -> bool:
    """
    Check if the provided 'drive_url' is a correct,
    shareable and valid Google Drive url.

    This method will fire a GET request to obtain
    the information about the file to confirm that
    is valid.
    """
    from yta_google_drive_downloader.resource import GoogleDriveResource

    try:
        GoogleDriveResource(drive_url)
    except:
        return False
    
    return True

def is_shareable_google_drive_url(
    drive_url: str
) -> bool:
    """
    Check if the given 'drive_url' has the format of a
    shareable Google Drive url, but it doesn't validate
    if it is a valid url or not.

    This method will only check the format but will not
    fire any GET request.

    This method doesn't modify the url nor includes the
    CONFIRM_STRING.
    """
    return _force_https(drive_url).startswith(DRIVE_RESOURCE_URL)