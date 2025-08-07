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

"""PyAMS_skin.interfaces.viewlet module

This module defines several interfaces for generic content managers which can be used inside
any web application.
"""

from zope.interface import Attribute, Interface
from zope.schema import Bool, Choice, Text, TextLine

from pyams_skin.interfaces import BOOTSTRAP_STATUS
from pyams_utils.text import PYAMS_HTML_RENDERERS_VOCABULARY
from pyams_viewlet.interfaces import IViewlet, IViewletManager


__docformat__ = 'restructuredtext'


class IDropdownMenu(IViewletManager):
    """Dropdown menu viewlet manager interface"""

    label = TextLine(title="Menu label")

    status = Choice(title="Dropdown Bootstrap status",
                    values=BOOTSTRAP_STATUS,
                    default='light')

    css_class = TextLine(title="Menu CSS class")

    icon_class = TextLine(title="FontAwesome icon class, including prefix")


class IMenuItem(IViewlet):
    """Menu item viewlet interface"""

    label = TextLine(title="Menu item label")

    css_class = TextLine(title="Item CSS class")

    icon_class = TextLine(title="FontAwesome icon class, including prefix")

    href = TextLine(title="Link target URL",
                    required=False,
                    default='#')

    def get_href(self):
        """Complete HREF attribute getter"""

    click_handler = TextLine(title="Optional Javascript click handler name")

    target = TextLine(title="Menu link target name")

    modal_target = Bool(title="Link to modal dialog?",
                        default=False)


class IMenuDivider(IViewlet):
    """Menu divider viewlet interface"""


class IHeaderViewletManager(IViewletManager):
    """Internal header viewlet manager interface"""


class IFormHeaderViewletManager(IViewletManager):
    """Form header viewlet manager interface"""


class IFooterViewletManager(IViewletManager):
    """Internal footer viewlet manager interface"""


class IFormFooterViewletManager(IViewletManager):
    """Form footer viewlet manager interface"""


class IHelpViewletManager(IViewletManager):
    """Content help viewlet manager interface"""


class IContentPrefixViewletManager(IViewletManager):
    """Content prefix viewlet manager interface"""


class IContentSuffixViewletManager(IViewletManager):
    """Content suffix viewlet manager interface"""


class IContextActionsViewletManager(IViewletManager):
    """Context actions viewlet manager interface"""

    css_class = TextLine(title="Actions CSS class")


class IContextAction(IViewletManager):
    """Context action viewlet manager interface"""

    status = Choice(title="Action status",
                    values=BOOTSTRAP_STATUS,
                    default='light')

    css_class = TextLine(title="Action CSS class",
                         default='btn-sm')

    icon_class = TextLine(title="FontAwesome icon class, including prefix")

    label = TextLine(title="Action label")

    hint = TextLine(title="Action hint")

    hint_placement = Choice(title="Hint placement",
                            values=('auto', 'top', 'bottom', 'left', 'right'),
                            default='auto')

    href = TextLine(title="Action URL")

    def get_href(self):
        """HREF attribute getter"""

    click_handler = TextLine(title="Optional Javascript click handler name")

    target = TextLine(title="Menu link target name")

    modal_target = Bool(title="Modal target")


class IBreadcrumbs(Interface):
    """Main breadcrumbs interface"""

    items = Attribute("Breadcrumbs items iterator attribute")


class IBreadcrumbItem(Interface):
    """Breadcrumb item interface"""

    label = TextLine(title="Item label")

    css_class = TextLine(title="CSS class")

    view_name = TextLine(title="Link view name")

    def get_href(self):
        """HREF attribute getter"""


class IAlertMessage(IViewlet):
    """Alert message"""

    status = Choice(title="Alert status",
                    values=BOOTSTRAP_STATUS,
                    default='info')

    css_class = TextLine(title="Custom alert CSS class")

    icon_class = TextLine(title="FontAwesome icon class, including prefix",
                          default='fas fa-info-circle')

    header = TextLine(title="Alert header")

    message = Text(title="Alert message")

    message_renderer = Choice(title="Message renderer",
                              vocabulary=PYAMS_HTML_RENDERERS_VOCABULARY,
                              default='text')
