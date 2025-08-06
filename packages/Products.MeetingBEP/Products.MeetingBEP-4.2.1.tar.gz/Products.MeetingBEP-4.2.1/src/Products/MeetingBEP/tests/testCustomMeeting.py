# -*- coding: utf-8 -*-
#
# File: testCustomMeeting.py
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.tests.MeetingBEPTestCase import MeetingBEPTestCase
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeetingType as mctcm


class testCustomMeetingType(MeetingBEPTestCase, mctcm):
    """ """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingType, prefix='test_'))
    return suite
