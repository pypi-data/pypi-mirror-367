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

"""PyAMS_skin.viewlet.footer module

This module provides a single "pyams.footer" viewlet manager used to handle internal page footer.
"""

from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IFooterViewletManager, IFormFooterViewletManager
from pyams_viewlet.manager import WeightOrderedViewletManager, viewletmanager_config


__docformat__ = 'restructuredtext'


@viewletmanager_config(name='pyams.footer', layer=IPyAMSLayer, view=Interface,
                       provides=IFooterViewletManager)
class FooterViewletManager(WeightOrderedViewletManager):
    """Internal footer viewlet manager"""


@viewletmanager_config(name='pyams.form_footer', layer=IPyAMSLayer, view=Interface,
                       provides=IFormFooterViewletManager)
class FormFooterViewletManager(WeightOrderedViewletManager):
    """Form footer viewlet manager"""
