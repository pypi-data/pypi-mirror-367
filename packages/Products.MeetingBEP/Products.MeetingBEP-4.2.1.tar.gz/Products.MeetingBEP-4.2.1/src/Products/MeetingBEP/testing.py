# -*- coding: utf-8 -*-
from plone.app.testing import FunctionalTesting
from plone.testing import z2
from plone.testing import zca
from Products.MeetingCommunes.testing import MCLayer

import Products.MeetingBEP


MBEP_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                            package=Products.MeetingBEP,
                            name='MBEP_ZCML')

MBEP_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MBEP_ZCML),
                                name='MBEP_Z2')

MBEP_TESTING_PROFILE = MCLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingBEP,
    additional_z2_products=('imio.dashboard',
                            'Products.MeetingBEP',
                            'Products.MeetingCommunes',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingBEP:testing',
    name="MBEP_TESTING_PROFILE")

MBEP_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MBEP_TESTING_PROFILE,), name="MBEP_TESTING_PROFILE_FUNCTIONAL")
