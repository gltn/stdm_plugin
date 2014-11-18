"""
/***************************************************************************
Name                 : Template database
Description          : class to create new database using the existing connection
Date                 : 11/November/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from stdm.data import STDMDb

from sqlalchemy.orm import sessionmaker
from stdm.data import _execute

dbStmt = 'CREATE DATABASE %s'

class DatabaseCreator(object):
    def __init__(self, dbname, template=None):
        """
        use the provided dbname to create a database using existing connection
        :param dbname:
        :return:
        """
        self.dbName = dbname
        self.template = template
        self._engine = STDMDb.instance().engine

    def dbExistCheck(self):
        """Check if the suggested db exist"""
        """To be implemented"""
        pass

    def createDb(self):
        """
        create a new database
        :return database object:
        """
        session = sessionmaker(bind=self._engine)()
        session.connection().connection.set_isolation_level(0)
        session.execute(dbStmt) % self.
        session.connection().connection.set_isolation_level(1)

    def createDbExtension(self):
        """
        Create postgis extension in the new database
        :return:
        """
        try:
            if self.template is not None:
                template_sql = ('CREATE EXTENSION %') % self.template
            else:
                template_sql = ('CREATE EXTENSION postgis')
            _execute(template_sql)
        except Exception as ex:
            raise ex.message


