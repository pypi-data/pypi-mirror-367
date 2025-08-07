from pyams_content_es.zmi import content_indexer_label==================
PyAMS_skin package
==================

Introduction
------------

This package is composed of a set of utility functions, usable into any Pyramid application.

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_viewlet import includeme as include_viewlet
    >>> include_viewlet(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_file import includeme as include_file
    >>> include_file(config)
    >>> from pyams_skin import includeme as include_skin
    >>> include_skin(config)

    >>> from pyams_utils.testing import call_decorator
    >>> from pyams_utils.adapter import adapter_config


Custom buttons
--------------

    >>> from pyams_layer.interfaces import IPyAMSLayer

    >>> from pyams_form.interfaces.button import IButtonAction
    >>> from pyams_form.interfaces.widget import IFieldWidget

    >>> from pyams_skin.interfaces.form import IActionButton, ICloseButton, IResetButton, ISubmitButton
    >>> from pyams_skin.interfaces.widget import IActionWidget, ICloseWidget, IResetWidget, ISubmitWidget

    >>> from pyams_skin.widget.button import SubmitFieldWidget, SubmitButtonAction
    >>> call_decorator(config, adapter_config, SubmitFieldWidget,
    ...                required=(ISubmitButton, IPyAMSLayer), provides=IFieldWidget)
    >>> call_decorator(config, adapter_config, SubmitButtonAction,
    ...                required=(IPyAMSLayer, ISubmitButton), provides=IButtonAction)

    >>> from pyams_skin.widget.button import ActionFieldWidget, ActionButtonAction
    >>> call_decorator(config, adapter_config, ActionFieldWidget,
    ...                required=(IActionButton, IPyAMSLayer), provides=IFieldWidget)
    >>> call_decorator(config, adapter_config, ActionButtonAction,
    ...                required=(IPyAMSLayer, IActionButton), provides=IButtonAction)

    >>> from pyams_skin.widget.button import ResetFieldWidget, ResetButtonAction
    >>> call_decorator(config, adapter_config, ResetFieldWidget,
    ...                required=(IResetButton, IPyAMSLayer), provides=IFieldWidget)
    >>> call_decorator(config, adapter_config, ResetButtonAction,
    ...                required=(IPyAMSLayer, IResetButton), provides=IButtonAction)

    >>> from pyams_form.testing import TestRequest

    >>> from zope.interface import alsoProvides, Interface
    >>> from pyams_skin.schema.button import SubmitButton, ActionButton, ResetButton, CloseButton

    >>> class ITestButtons(Interface):
    ...     submit = SubmitButton(name='submit', title="Submit")
    ...     action = ActionButton(name='action', title="Action")
    ...     reset = ResetButton(name='reset', title="Reset")
    ...     close = CloseButton(name='close', title="Close")

    >>> from pyams_form.button import Buttons
    >>> from pyams_form.field import Fields
    >>> from pyams_form.form import EditForm

    >>> class TestForm(EditForm):
    ...     buttons = Buttons(ITestButtons)
    ...     fields = Fields(Interface)

    >>> request = TestRequest()
    >>> alsoProvides(request, IPyAMSLayer)

    >>> form = TestForm(None, request)
    >>> form.update()

    >>> 'submit' in form.actions
    True
    >>> form.actions['submit']
    <SubmitButtonAction 'form.buttons.submit' 'Submit'>
    >>> print(form.actions['submit'].render())
    <button
        type="submit"
        id="form-buttons-submit"
        name="form.buttons.submit"
        class="btn btn-primary submit-widget submitbutton-field "
        value="Submit"
        data-loading-test="Submit...">
        Submit
    </button>


    >>> 'action' in form.actions
    True
    >>> form.actions['action']
    <ActionButtonAction 'form.buttons.action' 'Action'>
    >>> print(form.actions['action'].render())
    <button
        type="button"
        id="form-buttons-action"
        name="form.buttons.action"
        class="btn btn-secondary submit-widget actionbutton-field "
        value="Action"
        data-loading-test="Action...">
        Action
    </button>

    >>> 'reset' in form.actions
    True
    >>> form.actions['reset']
    <ResetButtonAction 'form.buttons.reset' 'Reset'>
    >>> print(form.actions['reset'].render())
    <button
        type="reset"
        id="form-buttons-reset"
        name="form.buttons.reset"
        class="btn btn-light submit-widget resetbutton-field"
        value="Reset">Reset</button>

    >>> 'close' in form.actions
    True
    >>> form.actions['close']
    <CloseButtonAction 'form.buttons.close' 'Close'>
    >>> print(form.actions['close'].render())
    <button
        type="button"
        id="form-buttons-close"
        name="form.buttons.close"
        class="btn btn-light submit-widget closebutton-field"
        value="Close"
        data-dismiss="modal">Close</button>


Custom form fields
------------------

    >>> from zope.schema import Tuple, TextLine, Date, Dict, Time, Datetime, Choice
    >>> from zope.schema.vocabulary import SimpleVocabulary
    >>> from pyams_utils.schema import HTTPMethodField, HTMLField
    >>> from pyams_skin.schema import BootstrapThumbnailsSelectionField, BootstrapDevicesBooleanField

    >>> class IMyContent(Interface):
    ...     textline_field = TextLine(title="Textline field")
    ...     list_field = Tuple(title="List field",
    ...                        value_type=TextLine())
    ...     http_method = HTTPMethodField(title="HTTP method")
    ...     html_field = HTMLField(title="HTML field")
    ...     date_field = Date(title="Date field")
    ...     time_field = Time(title="Time field")
    ...     datetime_field = Datetime(title="Datetime field")
    ...     select_field = Choice(title="Select field",
    ...                           vocabulary=SimpleVocabulary([]))
    ...     selection_field = BootstrapThumbnailsSelectionField(title="Selections",
    ...                                                         default_width=6)
    ...     visibility_field = BootstrapDevicesBooleanField(title="Devices",
    ...                                                     default=True)
    ...     mapping_field = Dict(title="Mapping",
    ...                          key_type=TextLine(),
    ...                          value_type=TextLine())

    >>> from zope.interface import implementer
    >>> from zope.schema.fieldproperty import FieldProperty

    >>> @implementer(IMyContent)
    ... class MyContent:
    ...     __name__ = None
    ...     __parent__ = None
    ...     textline_field = FieldProperty(IMyContent['textline_field'])
    ...     list_field = FieldProperty(IMyContent['list_field'])
    ...     http_method = FieldProperty(IMyContent['http_method'])
    ...     html_field = FieldProperty(IMyContent['html_field'])
    ...     date_field = FieldProperty(IMyContent['date_field'])
    ...     time_field = FieldProperty(IMyContent['time_field'])
    ...     datetime_field = FieldProperty(IMyContent['datetime_field'])
    ...     select_field = FieldProperty(IMyContent['select_field'])
    ...     selection_field = FieldProperty(IMyContent['selection_field'])
    ...     visibility_field = FieldProperty(IMyContent['visibility_field'])
    ...     mapping_field = FieldProperty(IMyContent['mapping_field'])

    >>> content = MyContent()
    >>> content.list_field = ('value 1', 'value2')
    >>> content.http_method = ('POST', '/api/auth/jwt/token')
    >>> content.html_field = '<p>This is a paragraph</p>'

    >>> from datetime import datetime
    >>> content.date_field = datetime.utcnow().date()
    >>> content.time_field = datetime.utcnow().time()
    >>> content.datetime_field = datetime.utcnow()

    >>> content.selection_field.get('xs')
    <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>
    >>> content.selection_field.get('xs').selection is None
    True
    >>> content.selection_field.get('xs').cols
    6
    >>> content.selection_field.get('xs').values
    (None, 6)

    >>> content.visibility_field
    {'xs': True, 'sm': True, 'md': True, 'lg': True, 'xl': True}
    >>> content.visibility_field.get('xs') is True
    True
    >>> value = content.visibility_field
    >>> value['xs'] = False
    >>> content.visibility_field = value
    >>> content.visibility_field
    {'xs': False, 'sm': True, 'md': True, 'lg': True, 'xl': True}
    >>> content.visibility_field.get('xs') is False
    True

    >>> from zope.interface import alsoProvides
    >>> from pyams_layer.interfaces import IPyAMSLayer

    >>> request = TestRequest(context=content)
    >>> alsoProvides(request, IPyAMSLayer)


Text widget with clipboard copy
-------------------------------

This widget can be used to copy input value to clipboard:

    >>> from pyams_skin.widget.text import TextCopyFieldWidget
    >>> text_widget = TextCopyFieldWidget(IMyContent['textline_field'], request)
    >>> text_widget.update()
    >>> print(text_widget.render())
    <div class="input-group"
         data-ams-modules="clipboard"
         data-target-input="nearest">
        <input type="text"
                   id="textline_field"
                   name="textline_field"
                   class="form-control text-widget required textline-field"
                   value="" />
        <div class="input-group-append">
                <div class="input-group-text hint"
                           data-original-title="Copy value to clipboard"
                           data-ams-click-handler="MyAMS.clipboard.copyText"
                           data-ams-clipboard-target="#textline_field">
                        <i class="far fa-clipboard"></i>
                </div>
        </div>
    </div>


Ordered list widget
...................

    >>> from pyams_skin.widget.list import OrderedListFieldWidget
    >>> list_widget = OrderedListFieldWidget(IMyContent['list_field'], request)
    >>> list_widget.extract()
    <NO_VALUE>

    >>> request = TestRequest(context=content, params={
    ...     'list_field': 'value2;value1'
    ... })
    >>> alsoProvides(request, IPyAMSLayer)
    >>> list_widget = OrderedListFieldWidget(IMyContent['list_field'], request)
    >>> list_widget.extract()
    ('value2', 'value1')


HTTP methods widgets
....................

    >>> from pyams_form.interfaces.form import IContextAware
    >>> from pyams_skin.widget.http import HTTPMethodFieldWidget, HTTPMethodDataConverter

    >>> http_widget = HTTPMethodFieldWidget(IMyContent['http_method'], request)
    >>> http_widget.context = content
    >>> alsoProvides(http_widget, IContextAware)
    >>> http_widget.update()
    >>> http_widget.value
    ('POST', '/api/auth/jwt/token')
    >>> http_widget.display_value
    ('POST', '/api/auth/jwt/token')

    >>> http_widget.extract()
    <NO_VALUE>

    >>> request = TestRequest(context=content, params={
    ...     'http_method-empty-marker': '1',
    ...     'http_method-verb': 'GET',
    ...     'http_method-url': '/api/auth/jwt/another'
    ... })
    >>> alsoProvides(request, IPyAMSLayer)

    >>> http_widget = HTTPMethodFieldWidget(IMyContent['http_method'], request)
    >>> http_widget.context = content
    >>> alsoProvides(http_widget, IContextAware)
    >>> http_widget.extract()
    ('GET', '/api/auth/jwt/another')
    >>> http_widget.http_methods
    ('GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS', 'DELETE')


HTML editor widgets
...................

    >>> from pyams_skin.widget.html import HTMLFieldWidget
    >>> request = TestRequest(context=content)
    >>> alsoProvides(request, IPyAMSLayer)

    >>> html_widget = HTMLFieldWidget(IMyContent['html_field'], request)
    >>> html_widget.context = content
    >>> alsoProvides(html_widget, IContextAware)
    >>> html_widget.update()
    >>> html_widget.value
    '<p>This is a paragraph</p>'
    >>> html_widget.editor_data is None
    True
    >>> print(html_widget.render())
    <textarea id="html_field"
              name="html_field"
              class="form-control tinymce textarea-widget required htmlfield-field">&lt;p&gt;This is a paragraph&lt;/p&gt;</textarea>

    >>> html_widget.editor_configuration = {'ams-editor-style': 'modern'}
    >>> print(html_widget.render())
    <textarea id="html_field"
              name="html_field"
              class="form-control tinymce textarea-widget required htmlfield-field"
              data-ams-options='{"ams-editor-style": "modern"}'>&lt;p&gt;This is a paragraph&lt;/p&gt;</textarea>


Date, time and datetime widgets
...............................

    >>> from pyams_skin.widget.datetime import DateFieldWidget, TimeFieldWidget, DatetimeFieldWidget
    >>> request = TestRequest(context=content)
    >>> alsoProvides(request, IPyAMSLayer)

    >>> date_widget = DateFieldWidget(IMyContent['date_field'], request)
    >>> date_widget.context = content
    >>> alsoProvides(date_widget, IContextAware)
    >>> date_widget.update()
    >>> date_widget.value
    '...-...-...'
    >>> print(date_widget.render())
    <div class="input-group date"
         data-ams-modules="plugins"
         data-target-input="nearest">
        <div class="input-group-prepend"
             data-target="#date_field-dt"
             data-toggle="datetimepicker">
            <div class="input-group-text hint"
                 data-original-title="Show calendar">
                <i class="far fa-calendar"></i>
            </div>
        </div>
        <input type="hidden"
               id="date_field"
               name="date_field"
               value="...-...-..." />
        <input type="text"
               id="date_field-dt"
               class="form-control datetime datetimepicker-input text-widget required date-field"
               value="...-...-..."
               data-target="date_field-dt"
               data-ams-format="L"
               data-ams-iso-target="#date_field" />
    </div>

    >>> time_widget = TimeFieldWidget(IMyContent['time_field'], request)
    >>> time_widget.context = content
    >>> alsoProvides(time_widget, IContextAware)
    >>> time_widget.update()
    >>> time_widget.value
    '...:...'
    >>> print(time_widget.render())
    <div class="input-group date"
         data-ams-modules="plugins"
         data-target-input="nearest">
        <div class="input-group-prepend"
             data-target="#time_field-dt"
             data-toggle="datetimepicker">
            <div class="input-group-text hint"
                 data-original-title="Show calendar">
                <i class="far fa-clock"></i>
            </div>
        </div>
        <input type="hidden"
               id="time_field"
               name="time_field"
               value="...:..." />
        <input type="text"
               id="time_field-dt"
               class="form-control datetime datetimepicker-input text-widget required time-field"
               value="...:..."
               data-target="time_field-dt"
               data-ams-format="LT"
               data-ams-iso-target="#time_field" />
    </div>

    >>> datetime_widget = DatetimeFieldWidget(IMyContent['datetime_field'], request)
    >>> datetime_widget.context = content
    >>> alsoProvides(datetime_widget, IContextAware)
    >>> datetime_widget.update()
    >>> datetime_widget.value
    '...-...-...T...:...:...+00:00'
    >>> print(datetime_widget.render())
    <div class="input-group date"
         data-ams-modules="plugins"
         data-target-input="nearest">
        <div class="input-group-prepend"
             data-target="#datetime_field-dt"
             data-toggle="datetimepicker">
            <div class="input-group-text hint"
                 data-original-title="Show calendar">
                <i class="far fa-calendar"></i>
            </div>
        </div>
        <input type="hidden"
               id="datetime_field"
               name="datetime_field"
               value="...-...-...T...:...:...+00:00" />
        <input type="text"
               id="datetime_field-dt"
               class="form-control datetime datetimepicker-input text-widget required datetime-field"
               value="...-...-...T...:...:...+00:00"
               data-target="datetime_field-dt"
               data-ams-iso-target="#datetime_field" />
    </div>

    >>> from pyams_skin.widget.datetime import BaseDatetimeDataConverter
    >>> converter = BaseDatetimeDataConverter(IMyContent['datetime_field'], datetime_widget)
    >>> value = datetime.utcnow()
    >>> widget_value = converter.to_widget_value(value)
    >>> widget_value
    '...-...-...T...:...:...+00:00'
    >>> field_value = converter.to_field_value(widget_value)
    >>> field_value
    datetime.datetime(..., tzinfo=<UTC>)

    >>> converter.to_widget_value(None) is None
    True
    >>> converter.to_field_value(None) is None
    True


Custom mapping widget
---------------------

This custom widget is used to use a TextArea widget to define mapping key and values, using a simple
multilines "key=value" syntax:

    >>> from pyams_skin.widget.dict import DictFieldWidget, DictWidgetDataConverter

    >>> content.mapping_field = {'Field 1': 'Value 1'}

    >>> mapping_widget = DictFieldWidget(IMyContent['mapping_field'], request)
    >>> mapping_widget.context = content
    >>> alsoProvides(mapping_widget, IContextAware)
    >>> mapping_widget.update()
    >>> mapping_widget.value
    'Field 1=Value 1'

    >>> converter = DictWidgetDataConverter(IMyContent['mapping_field'], mapping_widget)
    >>> mapping_value = converter.to_widget_value(content.mapping_field)
    >>> mapping_value
    'Field 1=Value 1'
    >>> converter.to_widget_value(None)
    ''
    >>> field_value = converter.to_field_value(mapping_value)
    >>> field_value
    {'Field 1': 'Value 1'}

    >>> converter.to_field_value('') is None
    True
    >>> pprint.pprint(converter.to_field_value('\nField 1=Value 1\n\nField 2=Value 2\n'))
    {'Field 1': 'Value 1', 'Field 2': 'Value 2'}


Dynamic select widget
.....................

PyAMS is using a Select2 plug-in to handle select inputs. When a select2 input is using
values provided from a remote server, several steps are required; we will take the principal
selector widget as an example:

    >>> from pyams_skin.interfaces.widget import IDynamicSelectWidget
    >>> class IPrincipalWidget(IDynamicSelectWidget):
    ...     """Principal widget marker interface"""

    >>> from zope.interface import implementer_only
    >>> from zope.schema.vocabulary import SimpleTerm
    >>> from pyams_form.browser.select import SelectWidget

    >>> @implementer_only(IPrincipalWidget)
    ... class PrincipalWidget(SelectWidget):
    ...
    ...     @staticmethod
    ...     def term_factory(value):
    ...         return SimpleTerm(value, title='Value ' + str(value))

    >>> request = TestRequest(context=content, params={'select_field': ['one', 'two']})
    >>> alsoProvides(request, IPyAMSLayer)

    >>> from pyams_form.widget import FieldWidget
    >>> widget = FieldWidget(IMyContent['select_field'], PrincipalWidget(request))
    >>> widget.update()
    >>> print(widget.render())
    <select id="select_field"
            name="select_field"
            class="...select-widget required choice-field"
            size="1">
    </select>
    <input name="select_field-empty-marker" type="hidden" value="1" />


    >>> from pyams_skin.widget.select import DynamicSelectWidgetTermsFactory
    >>> factory = DynamicSelectWidgetTermsFactory(content, request, None, widget.field, widget)
    >>> factory.getTerms()
    [<zope.schema.vocabulary.SimpleTerm object at 0x...>, <zope.schema.vocabulary.SimpleTerm object at 0x...>]
    >>> [(term.value, term.title) for term in factory.getTerms()]
    [('one', 'Value one'), ('two', 'Value two')]
    >>> factory.getValue('one')
    'one'


Bootstrap devices thumbnails selection widget
---------------------------------------------

This widget is used to define thumbnail selection for each Bootstrap device for a given image.

    >>> from pyams_skin.interfaces.schema import IBootstrapThumbnailsSelectionField
    >>> from pyams_skin.interfaces.widget import IBootstrapThumbnailsSelectionWidget

    >>> from pyams_skin.widget.bootstrap import BootstrapThumbnailsSelectionDataConverter

    >>> call_decorator(config, adapter_config, BootstrapThumbnailsSelectionDataConverter,
    ...                required=(IBootstrapThumbnailsSelectionField,
    ...                          IBootstrapThumbnailsSelectionWidget))

    >>> from pyams_skin.widget.bootstrap import BootstrapThumbnailsSelectionFieldWidget

    >>> field = IMyContent['selection_field']
    >>> widget = BootstrapThumbnailsSelectionFieldWidget(field, request)
    >>> widget.update()
    >>> _ = widget.render()

    >>> converter = BootstrapThumbnailsSelectionDataConverter(field, widget)
    >>> value = field.default
    >>> converter.to_field_value(value)
    {'xs': <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>,
     'sm': <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>,
     'md': <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>,
     'lg': <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>,
     'xl': <pyams_skin.interfaces.schema.BootstrapThumbnailSelection object at 0x...>}

    >>> request = TestRequest(context=content, params={
    ...     'selection_field-empty-marker': '1'
    ... })
    >>> alsoProvides(request, IPyAMSLayer)

    >>> widget = BootstrapThumbnailsSelectionFieldWidget(field, request)
    >>> widget.update()
    >>> _ = widget.render()


Bootstrap devices boolean widget
--------------------------------

This widget is used to define a boolean value for each Bootstrap device.

    >>> from pyams_skin.interfaces.schema import IBootstrapDevicesBooleanField
    >>> from pyams_skin.interfaces.widget import IBootstrapDevicesBooleanWidget

    >>> from pyams_skin.widget.bootstrap import BootstrapDevicesBooleanDataConverter

    >>> call_decorator(config, adapter_config, BootstrapDevicesBooleanDataConverter,
    ...                required=(IBootstrapDevicesBooleanField,
    ...                          IBootstrapDevicesBooleanWidget))

    >>> from pyams_skin.widget.bootstrap import BootstrapDevicesBooleanFieldWidget

    >>> field = IMyContent['visibility_field']
    >>> widget = BootstrapDevicesBooleanFieldWidget(field, request)
    >>> widget.update()
    >>> _ = widget.render()

    >>> converter = BootstrapDevicesBooleanDataConverter(field, widget)
    >>> value = field.default
    >>> converter.to_field_value(value)
    {'xs': False, 'sm': True, 'md': True, 'lg': True, 'xl': True}

    >>> request = TestRequest(context=content, params={
    ...     'visibility_field-empty-marker': '1'
    ... })
    >>> alsoProvides(request, IPyAMSLayer)

    >>> widget = BootstrapDevicesBooleanFieldWidget(field, request)
    >>> widget.update()
    >>> _ = widget.render()


Complete form
.............

    >>> from pyams_form.form import EditForm
    >>> form = EditForm(content, request)
    >>> form.fields = Fields(IMyContent)

    >>> form.update()


Tests cleanup:

    >>> tearDown()
