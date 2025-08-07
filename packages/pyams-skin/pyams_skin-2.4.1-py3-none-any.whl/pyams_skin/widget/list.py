#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.widget.list module

This module defines custom widgets which are used to handle lists.
"""

__docformat__ = 'restructuredtext'

from zope.interface import implementer_only

from pyams_form.browser.widget import HTMLFormElement
from pyams_form.widget import FieldWidget, SequenceWidget
from pyams_skin.interfaces.widget import IOrderedListWidget
from pyams_utils.interfaces.form import NO_VALUE


@implementer_only(IOrderedListWidget)
class OrderedListWidget(HTMLFormElement, SequenceWidget):
    """Ordered list widget"""

    separator = ';'

    def extract(self, default=NO_VALUE):
        params = self.request.params
        value = params.get(self.name, default)
        if value is not default:
            value = tuple(value.split(self.separator))
        return value


def OrderedListFieldWidget(field, request):  # pylint: disable=invalid-name
    """Ordered list field widget factory"""
    return FieldWidget(field, OrderedListWidget(request))
