# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.tests.MeetingBEPTestCase import MeetingBEPTestCase
from Products.MeetingCommunes.tests.testCustomWorkflows import testCustomWorkflows as mctcw


class testCustomWorkflows(MeetingBEPTestCase, mctcw):
    """ """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomWorkflows, prefix='test_'))
    return suite
