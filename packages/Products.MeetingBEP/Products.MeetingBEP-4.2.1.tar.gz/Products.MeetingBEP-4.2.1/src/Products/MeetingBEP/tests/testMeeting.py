# -*- coding: utf-8 -*-
#
# File: testMeeting.py
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.tests.MeetingBEPTestCase import MeetingBEPTestCase
from Products.MeetingCommunes.tests.testMeeting import testMeetingType as mctm


class testMeetingType(MeetingBEPTestCase, mctm):
    """
        Tests the Meeting class methods.
    """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testMeetingType, prefix='test_'))
    return suite
