from django.forms.widgets import Select, Widget
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from itertools import chain


class SelectOneOrNoneWidget(Select):
    '''Select Widget that checks the number of choices available before
       rendering the input element.
       If 0 choices, shows error.
       If 1 choice, shows just that choice.'''

    def render(self, name, value, attrs=None, choices=()):

        num_choices = len(self.choices.queryset)
        if num_choices > 1:
            return super(SelectOneOrNoneWidget, self).render(name, value, attrs, choices)

        output = []
        # If there's no choices, show error
        if num_choices == 0:
            output.append('<div>Sorry, no choices available.</div>')

        else:
            for option_value, option_label in chain(self.choices, choices):
                # skip field.empty_label
                if option_value:
                    output.append(format_html('<input type="{0}" name="{1}" value="{2}" id="{1}-{2}" />{3}',
                        'hidden',
                        name,
                        option_value,
                        force_text(option_label)))

        return mark_safe('\n'.join(output))


class CodeEditorWidget(Widget):

    '''Instead of displaying the content in a textarea, display it in a
       syntax-highlighted div, which updates a hidden input field.

       NOTE: Media.js relies on Jquery to populate the hidden input field with
       updated content.
    '''

    class Media:
        js = ('js/ace/ace.js', 'js/uofa.codeeditorwidget.js', )

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        value_text = force_text(value)

        input_attrs = self.build_attrs(attrs, name=name)
        input_html = format_html(u'<input type="hidden" value="{1}" {0}/>',
                                 flatatt(input_attrs),
                                 value_text)

        editable_attrs = self.build_attrs(attrs, contenteditable='true')
        editable_attrs['style'] = '; '.join([
            'position:absolute',
            'top:0',
            'left:0',
            'right:0',
            'bottom:0',
        ])
        editable_attrs['id'] = 'code-%s' % editable_attrs['id']
        editable_html = format_html(u'<code {0}>{1}</code>',
                                    flatatt(editable_attrs),
                                    value_text)

        wrapper_attrs = self.build_attrs(attrs, style='position:relative;')
        wrapper_attrs.pop('id')
        wrapper_attrs['class'] = 'uofa-code-editor-widget' # used in uofa.codeeditorwidget.js
        return format_html(u'<div {0}>{1}{2}</div>',
                           flatatt(wrapper_attrs),
                           editable_html,
                           input_html)
