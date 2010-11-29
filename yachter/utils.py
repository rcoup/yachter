from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django import forms

# make the fields work in South
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^yachter\.utils\.JSONField"])

class JSONFormField(forms.CharField):
    """ JSON Form Field """
    def clean(self, value):
        value = super(JSONFormField, self).clean(value)
        if value == '':
            return None
        
        try:
            json_data = json.loads(value)
        except Exception:
            raise forms.ValidationError(self.error_messages['invalid'])
        
        return json_data

    def prepare_value(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)

# Based on http://www.djangosnippets.org/snippets/1478/
class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        if value == "":
            return None

        if isinstance(value, basestring):
            return json.loads(value)

        return value

    def get_db_prep_save(self, value, connection):
        """Convert our JSON object to a string before we save"""
        if value in (None, ""):
            if self.null:
                return None
            else:
                return ''

        value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_db_prep_save(value, connection=connection)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value is not None:
            return json.dumps(value, cls=DjangoJSONEncoder)
        else:
            return ""

    def formfield(self, form_class=JSONFormField, **kwargs):
        return super(JSONField, self).formfield(form_class=form_class, **kwargs)
