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

"""PyAMS_skin.widget.button module

This module provides custom forms buttons widgets, with their matching actions.
"""

from zope.interface import implementer_only

from pyams_form.action import Action
from pyams_form.browser.submit import SubmitWidget as SubmitWidgetBase
from pyams_form.button import ButtonAction
from pyams_form.interfaces.button import IButtonAction
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces.form import IActionButton, ICloseButton, IResetButton, ISubmitButton
from pyams_skin.interfaces.widget import IActionWidget, ICloseWidget, IResetWidget, ISubmitWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.data import ObjectDataManagerMixin


__docformat__ = 'restructuredtext'


#
# Submit widget and actions
#

@implementer_only(ISubmitWidget)
class SubmitWidget(ObjectDataManagerMixin, SubmitWidgetBase):
    """Submit button widget"""


@adapter_config(required=(ISubmitButton, IFormLayer), provides=IFieldWidget)
def SubmitFieldWidget(field, request):  # pylint:disable=invalid-name
    """Form submit button factory adapter"""
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit


@adapter_config(required=(IFormLayer, ISubmitButton),
                provides=IButtonAction)
class SubmitButtonAction(SubmitWidget, ButtonAction):
    """Submit button action"""

    def __init__(self, request, field):  # pylint:disable=super-init-not-called
        Action.__init__(self, request, field.title)  # pylint:disable=non-parent-init-called
        SubmitWidget.__init__(self, request)
        self.field = field


#
# Secondary action button widget and actions
#

@implementer_only(IActionWidget)
class ActionWidget(ObjectDataManagerMixin, SubmitWidgetBase):
    """Secondary button widget"""


@adapter_config(required=(IActionButton, IFormLayer), provides=IFieldWidget)
def ActionFieldWidget(field, request):  # pylint:disable=invalid-name
    """Form secondary button factory adapter"""
    action = FieldWidget(field, ActionWidget(request))
    action.value = field.title
    return action


@adapter_config(required=(IFormLayer, IActionButton),
                provides=IButtonAction)
class ActionButtonAction(ActionWidget, ButtonAction):
    """Secondary button action"""

    def __init__(self, request, field):  # pylint:disable=super-init-not-called
        Action.__init__(self, request, field.title)  # pylint:disable=non-parent-init-called
        ActionWidget.__init__(self, request)
        self.field = field


#
# Reset widget and actions
#

@implementer_only(IResetWidget)
class ResetWidget(ObjectDataManagerMixin, SubmitWidgetBase):
    """Reset button widget"""


@adapter_config(required=(IResetButton, IFormLayer), provides=IFieldWidget)
def ResetFieldWidget(field, request):  # pylint:disable=invalid-name
    """Form reset button factory adapter"""
    reset = FieldWidget(field, ResetWidget(request))
    reset.value = field.title
    return reset


@adapter_config(required=(IFormLayer, IResetButton),
                provides=IButtonAction)
class ResetButtonAction(ResetWidget, ButtonAction):
    """Reset button action"""

    def __init__(self, request, field):  # pylint:disable=super-init-not-called
        Action.__init__(self, request, field.title)  # pylint:disable=non-parent-init-called
        ResetWidget.__init__(self, request)
        self.field = field


#
# Close widget and actions
#

@implementer_only(ICloseWidget)
class CloseWidget(ObjectDataManagerMixin, SubmitWidgetBase):
    """Close button widget"""


@adapter_config(required=(ICloseButton, IFormLayer), provides=IFieldWidget)
def CloseFieldWidget(field, request):  # pylint:disable=invalid-name
    """Form close button factory adapter"""
    reset = FieldWidget(field, ResetWidget(request))
    reset.value = field.title
    return reset


@adapter_config(required=(IFormLayer, ICloseButton),
                provides=IButtonAction)
class CloseButtonAction(CloseWidget, ButtonAction):
    """Close button action"""

    def __init__(self, request, field):  # pylint:disable=super-init-not-called
        Action.__init__(self, request, field.title)  # pylint:disable=non-parent-init-called
        CloseWidget.__init__(self, request)
        self.field = field
