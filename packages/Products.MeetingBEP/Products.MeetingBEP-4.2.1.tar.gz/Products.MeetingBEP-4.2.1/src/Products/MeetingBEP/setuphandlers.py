# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.config import PROJECTNAME
from Products.PloneMeeting.exportimport.content import ToolInitializer

import logging
import os


__author__ = """Gauthier Bastien <g.bastien@imio.be>"""
__docformat__ = 'plaintext'

logger = logging.getLogger('MeetingBEP: setuphandlers')


def isNotMeetingBEPProfile(context):
    return context.readDataFile("MeetingBEP_marker.txt") is None


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingBEPProfile(context):
        return
    logStep("postInstall", context)
    site = context.getSite()
    # need to reinstall PloneMeeting after reinstalling MBEP workflows
    # to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    reorderSkinsLayers(context, site)


def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isMeetingBEPConfigureProfile(context):
    return context.readDataFile("MeetingBEP_zbep_marker.txt") or \
        context.readDataFile("MeetingBEP_testing_marker.txt")


def isMeetingBEPTestingProfile(context):
    return context.readDataFile("MeetingBEP_testing_marker.txt")


def installMeetingBEP(context):
    """ Run the default profile"""
    if not isMeetingBEPConfigureProfile(context):
        return
    logStep("installMeetingBEP", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingBEP:default')


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current profile.'''
    if not isMeetingBEPConfigureProfile(context):
        return

    logStep("initializeTool", context)
    # PloneMeeting is no more a dependency to avoid magic between quickinstaller
    # and portal_setup so install it manually
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied.'''

    if isNotMeetingBEPProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def reorderSkinsLayers(context, site):
    """
       Re-apply MeetingBEP skins.xml step as the reinstallation of
       MeetingBEP and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingBEPProfile(context) and not isMeetingBEPConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingBEP:default', 'skins')


def finalizeExampleInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here.
    """
    if not isMeetingBEPConfigureProfile(context):
        return
    site = context.getSite()
    site.portal_setup.runAllImportStepsFromProfile(u'profile-Products.MeetingCommunes:zcommittee_advice')


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things work as expected...
    """
    if isNotMeetingBEPProfile(context) and \
       not isMeetingBEPConfigureProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)

    portal_css = site.portal_css
    css = ['plonemeeting.css',
           'meeting.css',
           'meetingitem.css',
           'meetingbep.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)
