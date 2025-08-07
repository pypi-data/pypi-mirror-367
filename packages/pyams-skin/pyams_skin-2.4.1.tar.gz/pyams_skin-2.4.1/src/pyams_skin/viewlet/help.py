#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.viewlet.help module

This module provides a "pyams.help" viewlet manager, used to display help messages in
views and forms.
A base alert message is also provided to build alerts based on Bootstrap components.
"""

from zope.interface import Interface, implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IAlertMessage, IHelpViewletManager
from pyams_template.template import template_config
from pyams_viewlet.manager import WeightOrderedViewletManager, viewletmanager_config
from pyams_viewlet.viewlet import Viewlet


__docformat__ = 'restructuredtext'


@viewletmanager_config(name='pyams.help', layer=IPyAMSLayer, view=Interface,
                       provides=IHelpViewletManager)
class HelpViewletManager(WeightOrderedViewletManager):
    """Help viewlet manager"""


@template_config(template='templates/alert.pt')
@implementer(IAlertMessage)
class AlertMessage(Viewlet):
    """Alert message"""

    status = FieldProperty(IAlertMessage['status'])
    css_class = FieldProperty(IAlertMessage['css_class'])
    icon_class = FieldProperty(IAlertMessage['icon_class'])
    header = FieldProperty(IAlertMessage['header'])
    _message = FieldProperty(IAlertMessage['message'])
    message_renderer = FieldProperty(IAlertMessage['message_renderer'])

    @property
    def message(self):
        """Translate internal message attribute"""
        return self.request.localizer.translate(self._message)
