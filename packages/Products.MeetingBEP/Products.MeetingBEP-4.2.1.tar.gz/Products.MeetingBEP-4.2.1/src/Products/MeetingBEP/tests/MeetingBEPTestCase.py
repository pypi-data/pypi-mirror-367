# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from Products.Archetypes.event import ObjectEditedEvent
from Products.MeetingBEP.config import PROJECTNAME
from Products.MeetingBEP.profiles.zbep.import_data import rhc_org
from Products.MeetingBEP.testing import MBEP_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingBEP.tests.helpers import MeetingBEPTestingHelpers
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase
from Products.PloneMeeting.exportimport.content import ToolInitializer
from zope.event import notify


class MeetingBEPTestCase(MeetingCommunesTestCase, MeetingBEPTestingHelpers):
    """Base class for defining MeetingBEP test cases."""

    layer = MBEP_TESTING_PROFILE_FUNCTIONAL
    cfg1_id = 'ca'
    cfg2_id = 'codir'

    subproductIgnoredTestFiles = ['test_robot.py',
                                  'testPerformances.py',
                                  'testContacts.py',
                                  'testVotes.py']

    def setUpRestrictedPowerObservers(self):
        """"""
        self.changeUser('siteadmin')
        context = self.portal.portal_setup._getImportContext('Products.MeetingBEP:testing')
        initializer = ToolInitializer(context, PROJECTNAME)
        initializer.addOrgs([rhc_org])
        self._setPowerObserverStates(states=('itemcreated', 'presented', 'returned_to_proposing_group',))
        self._setPowerObserverStates(observer_type='restrictedpowerobservers',
                                     states=('itemcreated', 'presented', 'returned_to_proposing_group',))
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(('return_to_proposing_group', ))
        notify(ObjectEditedEvent(cfg))
