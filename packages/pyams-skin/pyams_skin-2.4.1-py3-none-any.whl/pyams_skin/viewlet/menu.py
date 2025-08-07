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

"""PyAMS_skin.viewlet.menu module

This module provided several base classes which can be used to build menus.
"""

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IDropdownMenu, IMenuDivider, IMenuItem
from pyams_template.template import template_config
from pyams_viewlet.manager import TemplateBasedViewletManager, WeightOrderedViewletManager
from pyams_viewlet.viewlet import Viewlet


__docformat__ = 'restructuredtext'


@template_config(template='templates/menu-dropdown.pt', layer=IPyAMSLayer)
@implementer(IDropdownMenu)
class DropdownMenu(TemplateBasedViewletManager, WeightOrderedViewletManager):
    """Dropdown menu"""

    label = FieldProperty(IDropdownMenu['label'])
    status = FieldProperty(IDropdownMenu['status'])
    css_class = FieldProperty(IDropdownMenu['css_class'])
    icon_class = FieldProperty(IDropdownMenu['icon_class'])


@template_config(template='templates/menu-item.pt', layer=IPyAMSLayer)
@implementer(IMenuItem)
class MenuItem(Viewlet):
    """Base menu item viewlet base"""

    label = FieldProperty(IMenuItem['label'])
    css_class = FieldProperty(IMenuItem['css_class'])
    icon_class = FieldProperty(IMenuItem['icon_class'])
    href = FieldProperty(IMenuItem['href'])
    click_handler = FieldProperty(IMenuItem['click_handler'])
    target = FieldProperty(IMenuItem['target'])
    modal_target = FieldProperty(IMenuItem['modal_target'])

    def get_href(self):
        """Get complete URL from internal attribute"""
        return self.href


@template_config(template='templates/menu-divider.pt', layer=IPyAMSLayer)
@implementer(IMenuDivider)
class MenuDivider(Viewlet):
    """Menu divider viewlet base"""
