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

"""PyAMS_skin.schema.button module

This modules provides schema fields for custom action buttons.
"""

from zope.interface import implementer

from pyams_form.button import Button
from pyams_skin.interfaces.form import IActionButton, ICloseButton, IResetButton, ISubmitButton


__docformat__ = 'restructuredtext'


@implementer(ISubmitButton)
class SubmitButton(Button):
    """Submit button class"""


@implementer(IActionButton)
class ActionButton(Button):
    """Secondary action button"""


@implementer(IResetButton)
class ResetButton(Button):
    """Reset button class"""


@implementer(ICloseButton)
class CloseButton(Button):
    """Close button class"""
