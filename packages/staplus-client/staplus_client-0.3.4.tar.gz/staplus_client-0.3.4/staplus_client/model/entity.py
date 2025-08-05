# Copyright (C) 2023-2024 Secure Dimensions GmbH, Munich, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from frost_sta_client.model import entity
from staplus_client.service.staplusservice import STAplusService

class Entity(entity.Entity):
    def service(self, value):
        if value is None or isinstance(value, STAplusService):
            self._service = value
            return
        raise ValueError('service should be of type STAplusService')

    def set_service(self, service):
        if self.service != service:
            self.service = service
            self.ensure_service_on_children(service)
