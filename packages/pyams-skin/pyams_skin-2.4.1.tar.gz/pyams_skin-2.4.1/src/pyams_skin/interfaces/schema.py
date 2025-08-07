#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_skin.schema module

This module provides Bootstrap related schema fields.
"""

__docformat__ = 'restructuredtext'

from persistent import Persistent
from zope.interface import Interface, implementer
from zope.schema import Bool, Dict, Choice, Int
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IChoice, IDict

from pyams_file.interfaces.thumbnail import THUMBNAILERS_VOCABULARY_NAME
from pyams_skin.interfaces import BOOTSTRAP_SIZES_VOCABULARY


class IBootstrapSizeField(IChoice):
    """Bootstrap size selection field interface"""


@implementer(IBootstrapSizeField)
class BootstrapSizeField(Choice):
    """Bootstrap size field"""

    def __init__(self, values=None, vocabulary=None, source=None, **kw):
        super().__init__(vocabulary=BOOTSTRAP_SIZES_VOCABULARY, **kw)


class IThumbnailSelectionField(IChoice):
    """Bootstrap size choice field interface"""


@implementer(IThumbnailSelectionField)
class ThumbnailSelectionField(Choice):
    """Thumbnail selection field"""

    def __init__(self, values=None, vocabulary=None, source=None, **kw):
        super().__init__(vocabulary=THUMBNAILERS_VOCABULARY_NAME, **kw)


class IBootstrapThumbnailSelection(Interface):
    """Bootstrap thumbnail selection"""

    selection = ThumbnailSelectionField(required=False)
    cols = Int(min=0, max=12, required=False)

    def values(self):
        """Iterator over selection and columns"""


@implementer(IBootstrapThumbnailSelection)
class BootstrapThumbnailSelection(Persistent):
    """Bootstrap thumbnail selection"""

    selection = FieldProperty(IBootstrapThumbnailSelection['selection'])
    cols = FieldProperty(IBootstrapThumbnailSelection['cols'])

    def __init__(self, **kwargs):
        selection = kwargs.get('selection')
        if selection:
            self.selection = selection
        cols = kwargs.get('cols')
        if cols:
            self.cols = int(cols)

    @property
    def values(self):
        """Values getter as tuple"""
        return self.selection, self.cols


class IBootstrapThumbnailsSelectionField(IDict):
    """Bootstrap thumbnails selection mapping field interface"""

    default_width = Int(min=0, max=12, required=False)

    change_width = Bool(default=True)


class IThumbnailSelection(Interface):
    """Thumbnail selection interface"""


class IBootstrapDevicesBooleanField(IDict):
    """Bootstrap devices boolean field interface

    This field interface allows to define a boolean value for each Bootstrap
    device size.
    """

    default_value = Dict(key_type=BootstrapSizeField(),
                         required=False)
