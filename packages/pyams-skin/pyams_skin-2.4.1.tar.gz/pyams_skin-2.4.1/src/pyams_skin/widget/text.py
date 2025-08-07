#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.widget.text module

This module defines a custom text widget which provides a button
to copy selected value to clipboard.
"""

from zope.interface import implementer_only

from pyams_form.browser.text import TextWidget
from pyams_form.widget import FieldWidget
from pyams_skin.interfaces.widget import ITextCopyWidget


__docformat__ = 'restructuredtext'


@implementer_only(ITextCopyWidget)
class TextCopyWidget(TextWidget):
    """Text field widget with clipboard copy"""


def TextCopyFieldWidget(field, request):
    """Text field widget with clipboard copy factory"""
    return FieldWidget(field, TextCopyWidget(request))
