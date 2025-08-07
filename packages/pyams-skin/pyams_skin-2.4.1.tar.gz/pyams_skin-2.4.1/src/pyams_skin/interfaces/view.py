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

"""PyAMS_skin.interfaces.view module

This module provided generic interfaces and associated templates for several kinds of
generic views.
"""

from pyramid.interfaces import IView
from zope.interface import Interface
from zope.schema import TextLine

from pyams_layer.interfaces import IPyAMSLayer
from pyams_template.template import layout_config


__docformat__ = 'restructuredtext'


class IFullPage(IView):
    """Full page view marker interface"""


@layout_config(template='templates/fullpage-modal-layout.pt', layer=IPyAMSLayer)
class IModalFullPage(IFullPage):
    """Full page modal dialog view marker interface"""

    modal_class = TextLine(title="Modal dialog CSS class",
                           default='modal-lg')

    modal_content_class = TextLine(title="Modal dialog content CSS class",
                                   default='')


@layout_config(template='templates/inner-layout.pt', layer=IPyAMSLayer)
class IInnerPage(IView):
    """Inner page view marker interface"""


@layout_config(template='templates/modal-layout.pt', layer=IPyAMSLayer)
class IModalPage(IView):
    """Modal page view marker interface"""

    modal_class = TextLine(title="Modal dialog CSS class",
                           default='modal-lg')

    modal_content_class = TextLine(title="Modal dialog content CSS class",
                                   default='')


class IModalAddForm(IModalPage):
    """Modal add form marker interface"""


class IModalEditForm(IModalPage):
    """Modal edit form marker interface"""


class IModalDisplayForm(IModalPage):
    """Modal display form marker interface"""


class ISearchPage(Interface):
    """Custom search page view marker interface"""
