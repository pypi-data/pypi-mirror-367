# -*- coding: utf-8 -*-
#
# File: config.py
#
# GNU General Public License (GPL)
#

from Products.CMFCore.permissions import setDefaultRoles


__author__ = """Gauthier Bastien <g.bastien@imio.be>, Andre NUYENS <a.nuyens@imio.be>"""
__docformat__ = 'plaintext'

PROJECTNAME = "MeetingBEP"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))
product_globals = globals()

# "DU" auto replaced content values
DU_ORIGINAL_VALUE = "<p><strong><u>Proposition de décision&nbsp;:</u></strong></p>"
DU_RATIFICATION_VALUE = "<p><u><strong>Le {mc_title} décide à l'unanimité de ratifier la décision " \
    "prise en urgence en date du {emergency_decision_date}, à savoir de :</strong></u></p>"
