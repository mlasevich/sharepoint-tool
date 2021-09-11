"""
Main CLI entry point for sp-tool
"""
import logging
from argparse import Namespace

import click

from sp_tool.sharepoint.utils import to_yaml
from .sp_tool import SharepointTool, DEFAULT_CONFIG

from .logging import initialize_logging, LOG

__created__ = "09-08-2021"
__updated__ = "09-08-2021"
__version__ = '1.0.0'
ENV_PREFIX = 'SP_TOOL'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
DEF = Namespace(**DEFAULT_CONFIG)


@click.group(subcommand_metavar='ACTION',
             context_settings=CONTEXT_SETTINGS,
             epilog="""

Have fun!
             """)
@click.pass_context
@click.version_option(version=f"{__version__}({__updated__})")
@click.option('--dry-run/--no-dry-run', default=DEF.dry_run, show_default=True,
              help='If set, do not actually upload')
@click.option('--debug', is_flag=True, help='Debug mode', show_default=True)
@click.option('--site', default="", help='Number of greetings.',
              show_default=True)
@click.option('--tenant', prompt='Tenant Id?', help='Sharepoint Tenant id',
              show_default=True)
@click.option('--recurse/--no-recurse', default=DEF.recurse, show_default=True,
              help='If true, recurse into subdirectories')
@click.option('--checkout/--no-checkout', default=DEF.checkout,
              show_default=True,
              help='If true, recurse into subdirectories')
@click.option('--base-path', default=DEF.base_path, show_default=True,
              help='Base for uploading to sharepoint')
@click.option('--exclude', default=DEF.exclude, multiple=True,
              help='File name(s) to exclude when scanning for files to upload')
@click.option('--exclude-dirs', default=DEF.exclude_dirs, multiple=True,
              help='Directory name(s) to exclude when scanning for files to '
                   'upload(only relevant when recurse is on)')
@click.option('--include', default=DEF.include, multiple=True,
              help='File name(s) to include when scanning for files to upload')
@click.option('--include-dirs', default=DEF.include_dirs, multiple=True,
              help='Directory name(s) to include when scanning for files to '
                   'upload(only relevant when recurse is on)')
@click.option('--path', default=DEF.path, show_default=True,
              help='Path relative to base for uploading to sharepoint')
@click.option('--client-id', default=DEF.client_id, help='Sharepoint Client ID')
@click.option('--secret', default=DEF.secret, help='Sharepoint Secret Token')
def cli(ctx, debug, **kwargs):
    """
        Sharepoint API interface tool for publushing to Microsoft-hosted
        Sharepoint Instances.

        Typical use is with publish command:

            sp-tool [OPTIONS] publish ./dir

    """
    ctx.ensure_object(dict)
    ctx.obj.update(kwargs)
    ctx.obj['debug'] = debug
    if debug:
        LOG.setLevel(logging.DEBUG)
        LOG.debug("Debug Level is On")


@cli.command('register')
@click.pass_context
def register(ctx, **kwargs):
    """ Show effective config and exit"""
    ctx.ensure_object(dict)
    opts = {**DEFAULT_CONFIG, **ctx.obj, **kwargs}
    opts = Namespace(**opts)
    baseurl = "https://%s.sharepoint.com%s" % (
        opts.tenant, f"/sites/{opts.site}" if opts.site else "")

    print(f"""
How to register your app so that you have a client id and secret:
=================================================================

We cannot yet auto-register for you, but we can give you the urls
you will need based on inputs:

Step 1:
=======
Go to:  {baseurl}/_layouts/15/appregnew.aspx

Register your app. Record generated client id and token. Use
whatever values you want for Title/App Domain/Url - they are not
really used.

Step 2:
=======
Go to:  {baseurl}/_layouts/15/appinv.aspx

Enter the client id and do a lookup

Fill in permissions (see docs)

Click on Create and Then Trust.

""")


@cli.command('publish', short_help='Publish to SharePoint')
@click.argument('source_dir', nargs=1, required=True,
                type=click.Path(file_okay=False, exists=True))
@click.pass_context
def publish(ctx, **kwargs):
    """ Publish SOURCE_DIR to SharePoint"""
    ctx.ensure_object(dict)
    opts = {**ctx.obj, **kwargs}
    if not opts.get("tenant"):
        LOG.error("ERROR: Must provide tenant parameter")
        return -1
    if opts.get("secret") and opts.get("client_id"):
        LOG.info("Publishing to sharepoint")
        LOG.debug("Effective Config: \n---\n%s",
                  to_yaml(_normalize_opts(**opts)))
        tool = SharepointTool(**opts)
        return tool.publish()
    register.invoke(ctx)
    LOG.error("ERROR: You must provide client id and a secret")
    return -2


def _normalize_opts(**kwargs):
    """ Normalize/Mask options for safe printing"""
    opts = dict(**kwargs)
    secret = opts.get('secret') or ''
    secret_len = len(secret)
    if secret_len > 6:
        opts['secret'] = secret[0:3] + '*' * (secret_len - 6) + secret[-3:]
    return opts


@cli.command('config')
@click.pass_context
def config(ctx, **kwargs):
    """ Show effective config and exit"""
    ctx.ensure_object(dict)
    opts = {**DEFAULT_CONFIG, **ctx.obj, **kwargs}
    LOG.info("Effective Config: \n---\n%s", to_yaml(_normalize_opts(**opts)))


def main():
    """ Main Entry point """
    initialize_logging()
    cli(auto_envvar_prefix=ENV_PREFIX)  # pylint: disable=no-value-for-parameter


if __name__ == '__main__':
    main()
