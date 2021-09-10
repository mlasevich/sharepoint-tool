# Sharepoint API Client

[![Build Status](https://app.travis-ci.com/mlasevich/sharepoint-tool.svg?branch=main)](https://app.travis-ci.com/mlasevich/sharepoint-tool)
[![Coverage Status](https://coveralls.io/repos/github/mlasevich/sharepoint-tool/badge.svg?branch=main)](https://coveralls.io/github/mlasevich/sharepoint-tool?branch=main)
[![PyPI version](https://badge.fury.io/py/sharepoint-toolQ.svg)](https://badge.fury.io/py/sharepoint-tool)



This is a quick tool for interfacing with Sharepoint APIs without user
credentials. It includes a library to be used as well as a basic tool

***NOTE:*** this is only known to work with MS hosted instance, i.e. 
instances that have urls in form of `https://<tenant>.sharepoint.com/`.
It may work with self-hosted sharepoint, but currently the domain is 
hardcoded into the lib

## Known Issues

When creating folders using `add_folder_path()` or `upload_file()`, the
library will attempt to create all parent folders, and it may not have
permissions at certain level - causing `403` errors in the logs like these:

```
sp_tool.sharepoint.connector:E:API ERROR: 403: '{"error":{"code":"-2147024891, System.UnauthorizedAccessException","message":{"lang":"en-US","value":"Access denied."}}}'
```

These are usually safe to ignore, assuming folder already exists. In the future
we will handle this better.

## Pre-Requisites

This library leverages "AppOnly" Add-In OAuth authentication. Before you
can use this API, you will need to register your "app" and get a client_id
and a security token for authentication.

To do this you need to be admin on the space you are going to use.

***TIP***: You can generate these urls by running the app with `register` 
command like so:

    sp-tool --tenant mycompany --site MyTeam register

### Step 1 - Register your "App"

Go to URI `_layouts/15/appregnew.aspx` relative to your site - so if your 
tenant id is `mycompany` and your site is `MyTeam` it will be:

`https://mycompany.sharepoint.com/sites/MyTeam/_layouts/15/appregnew.aspx`

Fill in:
* `Client Id`: Just use Generate button to generate a good id. Save this 
  value as the client id parameter for the tool.
* `Client Secret`: Also use generate. Save this value as your API key(secret)
  for the tool
* `Title`: name of the tool
* `App Domain`: Not sure this matters - use hostname from your company url 
  or something
* `Redirect URI`: Not sure this matters - use your company url or something


### Step 2 - Grant Permissions

Now, go to uri `_layouts/15/appinv.aspx`. Going with example above it will be:

`https://mycompany.sharepoint.com/sites/MyTeam/_layouts/15/appinv.aspx`

Once there, enter the client id from step 1 and do a lookup
If all went well, it will populate all the fields except permissions
from values you set in the app.

For `Permission Request XML` enter something like (specific permissions 
depend on your needs):

```
<AppPermissionRequests AllowAppOnlyPolicy="true">  
    <AppPermissionRequest Scope="http://sharepoint/content/sitecollection" 
    Right="Write" />
</AppPermissionRequests>

```
See these links to better understand permissions:

* https://docs.microsoft.com/en-us/sharepoint/dev/sp-add-ins/add-in-permissions-in-sharepoint
* https://medium.com/ng-sp/sharepoint-add-in-permission-xml-cheat-sheet-64b87d8d7600

### Step 3 - Accept Trust Confirmation
## Using as binary

This library comes with a simple implementation as a tool to publish a 
directory of files to a SharePoint. 

Current help screen:

```
Usage: sp_tool [OPTIONS] ACTION

  Microsoft-hosted Sharepoint API interface tool

Options:
  --version                   Show the version and exit.
  --dry-run / --no-dry-run    If set, do not actually upload
  --debug                     Debug mode
  --site TEXT                 Number of greetings.
  --tenant TEXT               Sharepoint Tenant id
  --recurse / --no-recurse    If true, recurse into subdirectories
  --checkout / --no-checkout  If true, recurse into subdirectories
  --base-path TEXT            Base for uploading to sharepoint
  --path TEXT                 Path relative to base for uploading to
                              sharepoint
  --client_id TEXT            Sharepoint Client ID
  --secret TEXT               Sharepoint Secret Token
  -h                          Show this message and exit.
  --help                      Show this message and exit.

Commands:
  config   Show effective config and exit
  publish  Publish command

```

Every parameter above can be set via env variables as such:

* Authentication
    * `SP_TOOL_TENANT` - tenant in MS system (the hostname)
    * `SP_TOOL_SITE` - Site if uploading to a sub-site (leave blank to 
      upload to main site)
    * `SP_TOOL_SECRET` - secret token after registration
    * `SP_TOOL_CLIENT_ID` - client id after registration
* Connection
    * `SP_TOOL_DRY_RUN` - (true/false) set to "true" or "false" 
    * `SP_TOOL_RECURSE` - (true/false) Recursively upload files in source dir
    * `SP_TOOL_BASE_PATH` - Base Path for all files. Usually this is just ""
    * `SP_TOOL_PATH` - Base Path for all files
    * `SP_TOOL_CHECKOUT` - (true/false) if set, files are checked out
      after upload to reduce changes
    * `SP_TOOL_EXCLUDE` - one or more names or globs for files to exclude
      If blank, no files are excluded. If more than one, use path
      separator to separate (`;` on windows, `:` everywhere else).
      Example, to exclude tmp and backup files on unix, use `*.tmp:*.bak`
    * `SP_TOOL_EXCLUDE_DIR` - one or more names or globs for dir to
      exclude. If blank, no directories are excluded. if more than one,
      use path separator to separate (`;` on windows, `:` everywhere
      else). Example, to exclude tmp and backup files on unix, use
      `*.tmp:*.bak`
    * `SP_TOOL_INCLUDE` - one or more names or globs for files to include
      If blank, all files are included. If more than one, use path
      separator to separate (`;` on windows, `:` everywhere else).
      Example, to include all PDF and MD files on unix, 
      use `*.pdf:*.md:*.MD`
    * `SP_TOOL_INCLUDE_DIR` - one or more names or globs for dir to
      include. If blank, all directories are included. If more than one,
      use path separator to separate (`;` on windows, `:` everywhere
      else). Example, to exclude tmp and backup files on unix, use
      `*.tmp:*.bak`


## Using as library

To use this as a library in your code all you need to do is to
import and create SharepointConnection object:

```
from sp_tool.sharepoint import SharepointConnector

# Create Client
sharepoint = SharepointConnector(
    tenant=TENANT,
    client_id=CLIENT_ID,
    client_secret=SECRET,
    site_name=SITE
)

```

### Available APIs

Here is a quick dump of available commands as of right now:

* `api_call(action, url, headers=None, **kwargs)` low level api call
* `folder_contents(folder=DEFAULT_FOLDER)` -  ???
* `connected` - return true if connection is verified (executes a test call)

* `list_folders(folder=DEFAULT_FOLDER)` -  list folder names
* `folders(folder=DEFAULT_FOLDER)` -  list folder objects in the specified  
  folder

* `list_files(folder=DEFAULT_FOLDER)` -  list filenames in current folder
* `files(folder=DEFAULT_FOLDER)` -  list file objects in the specified  
  folder

* `list_folder_contents(folder=DEFAULT_FOLDER, sort=True)` -  list folder 
  and file names in the specified folder)

* `file_exists(filename, folder=DEFAULT_FOLDER)` -  Return true if filename 
  exists on the server
* `get_file_info(filename, folder=DEFAULT_FOLDER)` -  Get file object for 
  filename
* `get_file(filename, folder=DEFAULT_FOLDER)` -  (UNFINISHED) get file contents 
  from sharepoint
* `check_out_file(filename, folder=DEFAULT_FOLDER)` -  Checkout a  file
* `check_in_file(filename, folder=DEFAULT_FOLDER, comment="Auto Updated")` - 
  check in a checked out file
* `add_folder_path(full_folder, known_folders=None)` -  Create this folder 
  and all parent folders, if missing
* `add_folder(folder=DEFAULT_FOLDER)` -  Create folder
* `upload_file(filename, target_file=None, folder=DEFAULT_FOLDER, check_out=True)` - upload a file to folder. Creates folder path and 
  optionally checks out the file.
* `upload_page(filename, target_file=None, folder=DEFAULT_FOLDER, 
  check_out=True)` - attempts to upload file as a web template

TODO: More documentation
