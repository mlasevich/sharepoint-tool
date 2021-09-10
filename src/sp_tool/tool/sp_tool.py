"""
sp-tool implementation
"""
import os.path
import traceback
from argparse import Namespace
from functools import lru_cache

import yaml

from sp_tool.sharepoint import SharepointConnector
from sp_tool.tool.file_lister import list_files
from .logging import LOG

DEFAULT_CONFIG = dict(
    dry_run=False,
    exclude=[],
    exclude_dirs=[],
    include=[],
    include_dirs=[],
    recurse=True,
    source_dir='.',
    base_path="Shared Documents",
    client_id="",
    path="",
    secret="",
    site="",
    tenant=None,
    checkout=False
)


class SharepointTool:
    """ Sharepoint Publishing Tool """

    def __init__(self, *_args, **kwargs):
        """ Initialize """
        opts = {**DEFAULT_CONFIG, **kwargs}
        self.opts = Namespace(**opts)
        if self.opts.tenant is None:
            raise Exception('Must specify tenant')

    @property
    @lru_cache()
    def files(self):
        """ List of files to publish """
        return list_files(self.source_dir, self.opts.recurse,
                          self.opts.include, self.opts.exclude,
                          self.opts.include_dirs, self.opts.exclude_dirs)

    def publish(self):
        """ Publish to Sharepoint """
        LOG.debug("Publishing with options: \n%s",
                  yaml.safe_dump(vars(self.opts), default_flow_style=False))
        if not self.have_files:
            LOG.fatal("ERROR: No files found, unable to continue...")
            return 1

        try:
            if not self.sharepoint_connected:
                LOG.fatal("ERROR: Failed to connect to sharepoint...")
                return 2
            LOG.info("Found files to upload: \n%s",
                     yaml.safe_dump(self.files, default_flow_style=False))
            self._publish()
        except Exception as ex:
            LOG.error("Unknown Error: Failed to publish: %s", ex)
            if self.opts.debug:
                traceback.print_exc(ex, 7)
            return 4
        return 0

    @property
    def have_files(self):
        """ Check if we have files"""
        return bool(self.files)

    @property
    @lru_cache()
    def source_dir(self):
        """ Normalized source directory"""
        source_dir = self.opts.source_dir
        return source_dir

    @property
    @lru_cache()
    def sharepoint(self):
        """ Get sharepoint connection"""
        sharepoint = SharepointConnector(
            tenant=self.opts.tenant,
            client_id=self.opts.client_id,
            client_secret=self.opts.secret,
            site_name=self.opts.site
        )
        return sharepoint

    @property
    def sharepoint_connected(self):
        """ Check if sharepoint connection is working"""
        return self.sharepoint.connected

    def _publish(self):
        """ Publish files """
        files = self.files
        sharepoint = self.sharepoint
        base = self.source_dir
        sp_base = f"{self.opts.base_path}"
        if self.opts.path:
            sp_base = f"{sp_base}/{self.opts.path}"
        no_files = len(files)
        LOG.info("Processing %s file%s", no_files, "s" if no_files != 1 else "")
        LOG.info("Local path is: '%s' Remote path is: '%s'", base, sp_base)
        created_dir = []
        for file in files:
            LOG.debug("Working on '%s'", file)
            rel_file = file[len(base):] if file.startswith(base) else file
            rel_file = rel_file.strip('/')
            rel_dir = os.path.dirname(rel_file)
            sp_folder = f"{sp_base.rstrip('/')}/{rel_dir.lstrip('/')}"
            sp_folder = sp_folder.strip('/')
            sp_file = os.path.basename(rel_file)
            if not self.opts.dry_run:
                LOG.info("Uploading %s to SP as file '%s' in %s", rel_file,
                         sp_file, sp_folder)
                created_dir += sharepoint.add_folder_path(sp_folder,
                                                          created_dir)
                sharepoint.upload_file(file, target_file=sp_file,
                                       folder=sp_folder,
                                       check_out=self.opts.checkout)
            else:
                LOG.info("DRY RUN:: Would have uploaded file '%s' to '%s/%s' "
                         "(with%s checkout)", file, sp_folder, sp_file,
                         "" if self.opts.checkout else "out")
