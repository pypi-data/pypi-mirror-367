# -*- coding: utf-8 -*-
#
# File: testMeetingItem.py
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.tests.MeetingBEPTestCase import MeetingBEPTestCase
from Products.MeetingCommunes.tests.testMeetingItem import testMeetingItem as mctmi


class testMeetingItem(MeetingBEPTestCase, mctmi):
    """ """

    def test_pm_ShowObservations(self):
        """Override test as MeetingItem.showObservations was overrided as well."""
        self.setUpRestrictedPowerObservers()

        cfg = self.meetingConfig
        usedItemAttrs = cfg.getUsedItemAttributes()
        usedItemAttrs = usedItemAttrs + ('observations', )
        cfg.setUsedItemAttributes(usedItemAttrs)

        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        widget = item.getField('observations').widget
        self.assertTrue(widget.testCondition(item.aq_inner.aq_parent, self.portal, item))
        self.assertTrue(item.adapted().showObservations())

        # power observer may view
        self.changeUser('powerobserver1')
        self.assertTrue(widget.testCondition(item.aq_inner.aq_parent, self.portal, item))
        self.assertTrue(item.adapted().showObservations())

        # resctricted power observer may NOT view
        self.changeUser('restrictedpowerobserver1')
        self.assertFalse(widget.testCondition(item.aq_inner.aq_parent, self.portal, item))
        self.assertFalse(item.adapted().showObservations())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingItem, prefix='test_pm_'))
    return suite
