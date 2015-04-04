import logging
import xml.etree.ElementTree as ET

from memcache import Client


def xml_load(xmlstr):
    __ = {}
    root = ET.fromstring(xmlstr)
    for child in root:
        __[child.tag] = child.text
    return __


def xml_dump(obj_dict=None, root=None):
    if root is None:
        root = ET.Element('xml')
    for k in obj_dict:
        tmp = ET.SubElement(root, k)
        if isinstance(obj_dict[k], basestring):
            tmp.text = obj_dict[k]
        else:
            # now obj_dict[k] is a list who is carrying dict
            if tmp.tag == 'Articles':
                item_tag = 'item'
                for i in obj_dict[k]:
                    item = ET.SubElement(tmp, item_tag)
                    xml_dump(obj_dict=i, root=item)
            else:
                xml_dump(obj_dict[k][0], tmp)
    if root.tag == 'xml':
        xmlstr = ET.tostring(root, encoding='utf-8')
        return xmlstr


def get_logger(name, level='debug'):
    logger = logging.getLogger(name)
    level = eval('logging.' + level.upper())
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("|%(levelname)s - %(asctime)s - %(name)s - %(message)s"))
        logger.addHandler(handler)
    return logger


def get_cache(server='127.0.0.1:11211'):
    return Client([server])
