"""
Sharepoint utils
"""
import json
import urllib.parse
import logging
import yaml

LOG = logging.getLogger(__name__)


def urlencode(string):
    """ Encode string to URL"""
    return urllib.parse.quote(string or "")


def to_yaml(data):
    """ Dump data to yaml string """
    return yaml.safe_dump(data, default_flow_style=False)


def from_json(json_text):
    """ Decode from JSON from text"""
    return json.loads(json_text)


def strings_from_list(item_list, desc="item", field="Name", **kwargs):
    """ Convert a list of items into a list of strings by field """
    sort = bool(kwargs.get('sort', True))
    prefix = kwargs.get('prefix', "")
    suffix = kwargs.get('suffix', "")

    items = []
    for item in item_list:
        if field in item:
            value = item.get(field, None)
            items.append(None if value is None else f"{prefix}{value}{suffix}")
        else:
            LOG.info("Skipping invalid %s : %s", desc, item)
    return sorted(items) if sort else items
