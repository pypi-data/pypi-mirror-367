# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data


ca = deepcopy(mc_import_data.collegeMeeting)
ca.id = 'ca'
ca.title = 'CA'
ca.folderTitle = 'CA'
ca.shortName = 'ca'
ca.id = 'ca'
ca.shortName = 'CA'

codir = deepcopy(mc_import_data.councilMeeting)
codir.id = 'codir'
codir.title = 'CoDir'
codir.folderTitle = 'CoDir'
codir.shortName = 'codir'
codir.id = 'codir'
codir.shortName = 'CoDir'
codir.podTemplates = []

data = deepcopy(mc_import_data.data)
data.meetingConfigs = (ca, codir)
