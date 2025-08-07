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

"""PyAMS_skin.viewlet.bootstrap module

This module provides TALES extension used for Bootstrap integration.
"""

from zope.interface import Interface

from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension

__docformat__ = 'restructuredtext'


@adapter_config(name='bs-cols',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class BootstrapColumnsTALESExtension(ContextRequestViewAdapter):
    """Bootstrap columns getter TALES extension"""

    def render(self, selections, prefix=''):
        """Render extension"""
        return ' '.join((
            f"{prefix}-"
            f"{'' if device == 'xs' else f'{device}-'}"
            f"{12 // cols.cols}"
            for device, cols in selections.items()
        ))
