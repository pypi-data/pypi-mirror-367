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

"""PyAMS_*** module

"""

__docformat__ = 'restructuredtext'

from zope.interface import implementer_only
from zope.schema.vocabulary import getVocabularyRegistry

from pyams_file.interfaces.thumbnail import THUMBNAILERS_VOCABULARY_NAME
from pyams_form.browser.widget import HTMLFormElement
from pyams_form.converter import BaseDataConverter
from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.widget import IFieldWidget
from pyams_form.widget import FieldWidget, Widget
from pyams_layer.interfaces import IFormLayer
from pyams_skin.interfaces import BOOTSTRAP_SIZES, BOOTSTRAP_SIZES_VOCABULARY, BOOTSTRAP_DEVICES_ICONS
from pyams_skin.interfaces.schema import BootstrapThumbnailSelection, IBootstrapThumbnailsSelectionField, \
    IBootstrapDevicesBooleanField
from pyams_skin.interfaces.widget import IBootstrapThumbnailsSelectionWidget, IBootstrapDevicesBooleanWidget
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import NO_VALUE


#
# Bootstrap thumbnails selection widget
#

@adapter_config(required=(IBootstrapThumbnailsSelectionField,
                          IBootstrapThumbnailsSelectionWidget),
                provides=IDataConverter)
class BootstrapThumbnailsSelectionDataConverter(BaseDataConverter):
    """Bootstrap thumbnails selection data converter"""

    def to_widget_value(self, value):
        return value

    def to_field_value(self, value):
        return value


@implementer_only(IBootstrapThumbnailsSelectionWidget)
class BootstrapThumbnailsSelectionWidget(HTMLFormElement, Widget):
    """Bootstrap selection widget"""

    @property
    def display_value(self):
        """Display value getter"""
        value = self.value
        if not value:
            value = {
                size: BootstrapThumbnailSelection(cols=self.field.default_width.get(size))
                for size in BOOTSTRAP_SIZES.keys()
            }
        return value

    def extract(self, default=NO_VALUE):
        """Widget value extractor"""
        params = self.request.params
        marker = params.get(f'{self.name}-empty-marker', default)
        if marker is not default:
            return {
                size: BootstrapThumbnailSelection(
                    selection=params.get(f'{self.name}-{size}-selection'),
                    cols=params.get(f'{self.name}-{size}-cols',
                                    self.field.default_width.get(size)))
                for size in BOOTSTRAP_SIZES
            }
        return default

    @property
    def bootstrap_sizes(self):
        """Bootstrap sizes getter"""
        return BOOTSTRAP_SIZES_VOCABULARY

    @property
    def thumbnails_selections(self):
        """Thumbnails selections getter"""
        return getVocabularyRegistry().get(self.context, THUMBNAILERS_VOCABULARY_NAME)


@adapter_config(required=(IBootstrapThumbnailsSelectionField, IFormLayer),
                provides=IFieldWidget)
def BootstrapThumbnailsSelectionFieldWidget(field, request):
    """Bootstrap thumbnails selection field widget factory"""
    return FieldWidget(field, BootstrapThumbnailsSelectionWidget(request))


#
# Bootstrap boolean devices field
# A small widget used to select a boolean value for each Bootstrap device
#

@adapter_config(required=(IBootstrapDevicesBooleanField,
                          IBootstrapDevicesBooleanWidget),
                provides=IDataConverter)
class BootstrapDevicesBooleanDataConverter(BaseDataConverter):
    """Bootstrap boolean devices data converter"""

    def to_widget_value(self, value):
        return value

    def to_field_value(self, value):
        return value


@implementer_only(IBootstrapDevicesBooleanWidget)
class BootstrapDevicesBooleanWidget(HTMLFormElement, Widget):
    """Bootstrap boolean devices widget"""

    @property
    def display_value(self):
        """Display value getter"""
        value = self.value
        if not value:
            value = self.field.default_value.copy()
        return value

    def extract(self, default=NO_VALUE):
        """Widget value extractor"""
        params = self.request.params
        marker = params.get(f'{self.name}-empty-marker', default)
        if marker is not default:
            return {
                size: params.get(f'{self.name}-{size}') == 'on'
                for size in BOOTSTRAP_SIZES.keys()
            }
        return default

    @property
    def bootstrap_sizes(self):
        """Bootstrap sizes getter"""
        return BOOTSTRAP_SIZES_VOCABULARY

    @property
    def bootstrap_icons(self):
        """Bootstrap icons getter"""
        return BOOTSTRAP_DEVICES_ICONS


@adapter_config(required=(IBootstrapDevicesBooleanField, IFormLayer),
                provides=IFieldWidget)
def BootstrapDevicesBooleanFieldWidget(field, request):
    """Bootstrap boolean devices field widget factory"""
    return FieldWidget(field, BootstrapDevicesBooleanWidget(request))
