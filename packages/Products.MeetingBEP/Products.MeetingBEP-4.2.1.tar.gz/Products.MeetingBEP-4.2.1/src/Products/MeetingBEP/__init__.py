# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from Products.CMFCore import DirectoryView
from Products.MeetingBEP.config import product_globals

import logging


__author__ = """Gauthier Bastien <g.bastien@imio.be>"""
__docformat__ = 'plaintext'


logger = logging.getLogger('MeetingBEP')
logger.debug('Installing Product')
DirectoryView.registerDirectory('skins', product_globals)


def initialize(context):
    """initialize product (called by zope)"""
