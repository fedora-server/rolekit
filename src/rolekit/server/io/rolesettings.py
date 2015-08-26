# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2012 Red Hat, Inc.
#
# Authors:
# Thomas Woerner <twoerner@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import shutil
import json

from rolekit.config import *
from rolekit.logger import log

class RoleSettings(dict):
    """ Rolesettings store """

    def __init__(self, type_name, name, *args, **kwargs):
        super(RoleSettings, self).__init__(*args, **kwargs)

        self.name = name
        self._type = type_name

        self.path = "%s/%s" % (ETC_ROLEKIT_ROLES, self._type)

        # If we need to autogenerate a name, do it here
        if not name:
            # Check both the existing and pending role directories
            self.name = self.get_unique_instance(self._type)

        self.filepath = "%s/%s.json" % (self.path, self.name)

    def read(self):
        with open(self.filepath, "r") as f:
            data = f.read()
        imported = json.loads(data)
        del data
        if type(imported) is not dict:
            return

        for key,value in imported.items():
            self[key] = value
        del imported

    def write(self):
        try:
            os.mkdir(self.path)
        except OSError:
            pass

        try:
            shutil.copy2(self.filepath, "%s.old" % self.filepath)
        except Exception as msg:
            if os.path.exists(self.filepath):
                raise IOError("Backup of '%s' failed: %s" % (self.filepath,
                                                             msg))

        d = json.dumps(self)
        with open(self.filepath, "w") as f:
            f.write(d)

    def remove(self):
        try:
            os.remove(self.filepath)
        except OSError:
            pass

    @staticmethod
    def get_unique_instance(type):
        instances = [ ]
        for path in ("%s/%s" % (ETC_ROLEKIT_ROLES, type),):
            if os.path.exists(path) and os.path.isdir(path):
                for name in sorted(os.listdir(path)):
                    if not name.endswith(".json"):
                        continue
                    # Add this instance to the list, sans .json
                    instances.append(name[:-5])

        # We'll use numeric identifiers for instances
        id = 1
        while str(id) in instances:
            id += 1
        log.debug1("Generating unique instance %s" % str(id))
        return str(id)
