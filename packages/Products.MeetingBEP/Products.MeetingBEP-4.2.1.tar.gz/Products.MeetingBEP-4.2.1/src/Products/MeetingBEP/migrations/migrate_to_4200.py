# -*- coding: utf-8 -*-

from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200

import logging


logger = logging.getLogger('MeetingBEP')


class Migrate_To_4200(MCMigrate_To_4200):

    def run(self,
            profile_name=u'profile-Products.MeetingBEP:default',
            extra_omitted=[]):

        # call steps from Products.MeetingCommunes
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Call Products.MeetingCommunes migration.
    '''
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
