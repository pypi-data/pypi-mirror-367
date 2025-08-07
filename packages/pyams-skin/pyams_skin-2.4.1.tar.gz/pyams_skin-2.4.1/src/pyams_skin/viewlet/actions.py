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

"""PyAMS_skin.viewlet.actions module

This module provides contextual actions content providers.
"""

from zope.interface import Interface, implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IContextAction, IContextActionsViewletManager
from pyams_template.template import template_config
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import TemplateBasedViewletManager, WeightOrderedViewletManager, \
    viewletmanager_config
from pyams_viewlet.viewlet import Viewlet


__docformat__ = 'restructuredtext'


@viewletmanager_config(name='pyams.context_actions', layer=IPyAMSLayer, view=Interface,
                       provides=IContextActionsViewletManager)
@template_config(template='templates/actions.pt')
class ContextActionsViewletManager(TemplateBasedViewletManager, WeightOrderedViewletManager):
    """Context actions viewlet manager"""

    css_class = FieldProperty(IContextActionsViewletManager['css_class'])


@implementer(IContextAction)
class ContextActionMixin:
    """Base context action mixin"""

    status = FieldProperty(IContextAction['status'])
    css_class = FieldProperty(IContextAction['css_class'])
    icon_class = FieldProperty(IContextAction['icon_class'])
    label = FieldProperty(IContextAction['label'])
    hint = FieldProperty(IContextAction['hint'])
    hint_placement = FieldProperty(IContextAction['hint_placement'])
    href = FieldProperty(IContextAction['href'])
    click_handler = FieldProperty(IContextAction['click_handler'])
    target = FieldProperty(IContextAction['target'])
    modal_target = FieldProperty(IContextAction['modal_target'])

    def get_href(self):
        """Get absolute URL from internal attributes"""
        return absolute_url(self.context, self.request, self.href)


@template_config(template='templates/action.pt')
class ContextAction(ContextActionMixin, Viewlet):
    """Simple context action"""


class JsContextAction(ContextAction):
    """Javascript context action"""

    def get_href(self):
        return self.href


class ContextAddAction(ContextAction):
    """Simple context add action"""

    status = 'primary'
    icon_class = 'fas fa-plus'
    modal_target = True


@template_config(template='templates/actions-menu.pt')
class ContextActionsMenu(ContextActionMixin, TemplateBasedViewletManager,
                         WeightOrderedViewletManager):
    """Context actions menu viewlet"""
