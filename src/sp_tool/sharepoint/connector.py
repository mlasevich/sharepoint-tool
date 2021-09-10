"""
Sharepoint Connector
"""
import json
import os
import logging
import socket

import requests

from .exceptions import APICallFailedSharepointException
from .auth import SharepointAuth
from .url import SharepointURL
from .utils import from_json, strings_from_list, urlencode

DEFAULT_FOLDER = "Shared Documents/"
LOG = logging.getLogger(__name__)


class SharepointConnector:
    """ Sharepoint Connector """
    ACTIONS = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put
    }
    DEFAULT_CONTENT_TYPE = "multipart/form-data"

    def __init__(self, tenant, client_id, client_secret, site_name=""):
        """
        Initialize SharePoint Connector

        :param tenant: prefix for url
        :param client_id: app client_id for authentication
        :param client_secret: app client_secret for authentication
        :param site_name: name of the site without `sites/` prefix
        """
        self.url = SharepointURL(tenant, site_name)
        self.auth = SharepointAuth(self.url.host, client_id, client_secret)

    def api_call(self, action, url, headers=None, **kwargs):
        """ Generic web request wrapper with authentication """
        headers = headers if headers else {}

        req = self.ACTIONS.get(action.lower(), None)
        if req is None:
            raise Exception(f"Invalid action: {action}")
        content_type = kwargs.pop('content_type', self.DEFAULT_CONTENT_TYPE)
        raise_on_error = kwargs.pop('raise_on_error', False)
        req_headers = self.headers(content_type, headers=headers)
        res = req(url, headers=req_headers, **kwargs)
        if res.status_code >= 400:
            LOG.error("API ERROR: %s: '%s'", res.status_code, res.text)
            if raise_on_error:
                raise APICallFailedSharepointException(res.status_code,
                                                       res.text)
        return res

    def folder_contents(self, folder=DEFAULT_FOLDER):
        """ Get folder contents"""
        folders = self.folders(folder)
        files = self.files(folder)
        contents = folders + files
        return contents

    @property
    def connected(self):
        """ Check if we are connected"""
        try:
            socket.gethostbyname(self.url.host)
            self.api_call('get', f"{self.url.folder('/')}/Folders",
                          raise_on_error=True)
            return True
        except socket.gaierror:
            LOG.error("Invalid host: %s" % self.url.host)
            return False
        except APICallFailedSharepointException as _ex:
            return False

    def folders(self, folder=DEFAULT_FOLDER):
        """ Get list of folders items in a given folder"""
        return self._get_items(folder, "Folder")

    def files(self, folder=DEFAULT_FOLDER):
        """ Get list of files in a given folder"""
        return self._get_items(folder, "File")

    def _get_items(self, folder=DEFAULT_FOLDER, item_type="File"):
        """ Get list of specific type in a given folder (full data)"""
        res = self.api_call('get', f"{self.url.folder(folder)}/{item_type}s")
        data = from_json(res.text)
        data = data.get('d', data)
        data = data.get('results', data)
        return data

    def list_folder_contents(self, folder=DEFAULT_FOLDER, sort=True):
        """ List files and folders in folder as just names"""
        contents = self.list_files(folder) + self.list_folders(folder)
        return sorted(contents) if sort else contents

    def list_folders(self, folder=DEFAULT_FOLDER):
        """ Get list of folder names in a given folder"""
        return self._list_items(folder, "Folder", suffix="/")

    def list_files(self, folder=DEFAULT_FOLDER):
        """ Get list of files in a given folder"""
        return self._list_items(folder, "File")

    def _list_items(self, folder=DEFAULT_FOLDER, item_type="File",
                    **kwargs):
        """ Get a list of items of a specific type (just names)"""
        items = self._get_items(folder, item_type)
        desc = f"{item_type.lower()} from folder '{folder}'"
        return strings_from_list(items, desc=desc, **kwargs)

    def file_exists(self, filename, folder=DEFAULT_FOLDER):
        """
        Check if file exists in a folder

        :param folder:
        :param filename:
        :return: true if file exists
        """
        files = self.list_files(folder)
        return filename in files

    def get_file_info(self, filename, folder=DEFAULT_FOLDER):
        """ get file """
        if not self.file_exists(filename, folder):
            LOG.info("File %s is not in folder %s", filename, folder)
            return False

        url = self.url.file(folder, filename, "")
        LOG.info("Getting file at url %s", url)
        res = self.api_call('get', url)
        if res.status_code < 400:
            return from_json(res.text)
        LOG.error("ERROR: %s: '%s'", res.status_code, res.text)
        return ""

    def get_file(self, filename, folder=DEFAULT_FOLDER):
        """ UNFINISHED get file """
        if not self.file_exists(filename, folder):
            LOG.error("File %s} is not in folder %s", filename, folder)
            return False

        folder = urlencode(folder or "")
        filename = urlencode(filename or "")
        headers = self.headers(headers={
            "Accept": "application/octet-stream"
        })
        url = f"{self.url.file(folder, filename)}"
        LOG.info("Getting file at url %s", url)
        res = self.api_call("get", url, headers=headers)
        if res.status_code < 400:
            return res.text
        LOG.error("ERROR: %s: '%s'", res.status_code, res.text)
        return ""

    def check_in_file(self, filename, folder=DEFAULT_FOLDER,
                      comment="Auto Updated"):
        """ Check-in file in folder"""
        url = self.url.file(folder, filename,
                            f"/CheckIn(comment='{comment}',checkintype=0)")
        LOG.info("Checking in file: %s/%s", folder, filename)
        # LOG.info("Checking in URL: %s", url)
        res = self.api_call('post', url)
        return res

    def check_out_file(self, filename, folder=DEFAULT_FOLDER):
        """ Checkout file in folder"""
        url = self.url.file(folder, filename, "/CheckOut()")
        LOG.info("Checking out file: %s/%s", folder, filename)
        # LOG.info("Checking in URL: %s", url)
        res = self.api_call('post', url)
        return res

    def add_folder_path(self, full_folder, known_folders=None):
        """ Add Full folder path as needed """
        if not known_folders:
            known_folders = []
        folder_parts = full_folder.split('/')
        folder = ""
        added = []
        for part in folder_parts:
            folder = f"{folder}/{part}" if folder else part
            if folder in known_folders:
                continue
            self.add_folder(folder)
            added.append(folder)
        return added

    def add_folder(self, folder=DEFAULT_FOLDER):
        """ Ensure folder exists"""
        LOG.info("Adding folder %s", folder)
        data = json.dumps({
            "__metadata": {
                "type": "SP.Folder"
            },
            "ServerRelativeUrl": f"{self.url.site_uri}/{folder}"
        })
        url = f"{self.url.web}/folders"

        LOG.debug("URL: %s", url)
        LOG.debug("data: %s", data)
        res = self.api_call('post', url,
                            data=data,
                            content_type="application/json;odata=verbose",
                            headers={
                                "Content-Length": f"{len(data)}",
                            })
        LOG.debug("%s::%s::%s", res.status_code, res.headers, res.text)
        return res.text

    def upload_file(self, filename, target_file=None, folder=DEFAULT_FOLDER,
                    check_out=True):
        """ Upload file to sharepoint folder """
        if not os.path.isfile(filename):
            LOG.error("Local File %s does not exist, cannot upload", filename)
            return False
        f_info = os.stat(filename)
        if not target_file:
            target_file = os.path.basename(filename)

        if self.file_exists(target_file, folder):
            self.check_in_file(filename=target_file, folder=folder)

        LOG.error("Uploading %s to %s/%s", filename, folder, target_file)

        file_uri = urlencode(
            f"{self.url.site_uri}/{folder}/{target_file}")

        url = self.url.folder(folder, f"/Files/"
                                      f"Add(url='{file_uri}',overwrite=true)")

        headers = self.headers("application/octet-stream", headers={
            "Content-Length": f"{f_info.st_size}"
        })
        # print(f"Headers: \n{to_yaml(headers)}\n---")
        # print(f"url={url}")
        with open(filename, 'rb') as data:
            res = requests.post(url, data=data, headers=headers)

        if res.status_code < 400:
            if check_out:
                self.check_out_file(target_file, folder)
            return res
        LOG.error("ERROR: %s: '%s'", res.status_code, res.text)
        return res

    def upload_page(self, filename, target_file=None, folder=DEFAULT_FOLDER,
                    check_out=True):
        """ Upload file to sharepoint folder """
        if not os.path.isfile(filename):
            LOG.error("Local File %s does not exist, cannot upload", filename)
            return False
        f_info = os.stat(filename)
        if not target_file:
            target_file = os.path.basename(filename)

        self.check_in_file(filename=target_file, folder=folder)

        LOG.error("Uploading %s to %s/%s", filename, folder, target_file)

        file_uri = urlencode(
            f"{self.url.site_uri}/{folder}/{target_file}")

        url = self.url.folder(folder, f"/Files/AddTemplateFile"
                                      f"("
                                      f"urloffile='{file_uri}',"
                                      f"templatefiletype=0"
                                      f")")

        headers = self.headers("application/octet-stream", headers={
            "Content-Length": f"{f_info.st_size}"
        })
        # print(f"Headers: \n{to_yaml(headers)}\n---")
        # print(f"url={url}")
        with open(filename, 'rb') as data:
            res = requests.post(url, data=data, headers=headers)

        if res.status_code < 400:
            if check_out:
                self.check_out_file(target_file, folder)
            return res
        LOG.error("ERROR: %s: '%s'", res.status_code, res.text)
        return res

    def headers(self, content_type=None, headers=None, **more_headers):
        """ Generate request headers"""
        if content_type is None:
            content_type = self.DEFAULT_CONTENT_TYPE
        if headers is None:
            headers = {}

        req_headers = {
            "Authorization": f"Bearer {self.auth.access_token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": content_type
        }
        return {**req_headers, **more_headers, **headers}
