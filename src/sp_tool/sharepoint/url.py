""" Sharepoint URL Generator """
import functools
import urllib.parse


class SharepointURL:
    """ Represents/generates Sharepoint URLs"""

    def __init__(self, tenant_name, site_name):
        """ Initialize """
        self.tenant_name = tenant_name
        self.site_name = site_name

    @property
    @functools.lru_cache(maxsize=None)
    def site_uri(self):
        """ Full site uri"""
        return f"/sites/{self.site_name}" if self.site_name else "/"

    @property
    @functools.lru_cache(maxsize=None)
    def host(self):
        """ Sharepoint Host Name"""
        return f"{self.tenant_name}.sharepoint.com"

    @property
    @functools.lru_cache(maxsize=None)
    def base(self):
        """ Server Base URL"""
        return f"https://{self.host}"

    @property
    @functools.lru_cache(maxsize=None)
    def site(self):
        """ Site Base URL"""
        return f"{self.base}/{self.site_uri}"

    @property
    @functools.lru_cache(maxsize=None)
    def api_uri(self):
        """ Get api URI"""
        return f"{self.site_uri}/_api"

    @property
    @functools.lru_cache(maxsize=None)
    def api(self):
        """ Get api URL"""
        return f"{self.base}/{self.api_uri}"

    @property
    @functools.lru_cache(maxsize=None)
    def web_uri(self):
        """ Web API URI"""
        return f"{self.api_uri}/Web"

    @property
    @functools.lru_cache(maxsize=None)
    def web(self):
        """ Get web api URL"""
        return f"{self.base}/{self.web_uri}"

    def file_uri(self, folder, filename, suffix=""):
        """ Generate a file URI base """
        folder = urllib.parse.quote(folder or "")
        filename = urllib.parse.quote(filename or "")
        return f"{self.web_uri}/GetFileByServerRelativePath(" \
               f"decodedurl='{self.site_uri}/{folder}/{filename}'" \
               f"){suffix}"

    def file(self, folder, filename, suffix=""):
        """ Generate a file url"""
        uri = self.file_uri(folder, filename, suffix)
        return f"{self.base}{uri}"

    def folder_uri(self, folder, suffix=""):
        """ Generate a folder URL base """
        folder = urllib.parse.quote(folder or "")
        return f"{self.web_uri}/GetFolderByServerRelativePath" \
               f"(decodedurl='{self.site_uri}/{folder}'){suffix}"

    def folder(self, folder, suffix=""):
        """ Generate a folder url"""
        uri = self.folder_uri(folder, suffix)
        return f"{self.base}{uri}"
