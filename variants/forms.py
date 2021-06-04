from django import forms
from django.forms import ValidationError
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from variants.models import Table, TimeSlot, Variation, ProductVariation
from services.models import Seller
from variants.custom_layout_object import Formset

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, Submit, Button


""" Table forms """
class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        exclude = ('seller',)


class TableUniqueFormset(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        
        values = set()
        for form in self.forms:
            if form.cleaned_data.get('row', None):
                row = form.cleaned_data.get('row')
                col = form.cleaned_data.get('col')
                
                if (row, col) in values:
                    form.add_error('row', 'This value is duplicated.')
                    form.add_error('col', 'This value is duplicated.')
                    return
                values.add((row, col))


TableFormSet = inlineformset_factory(
    Seller,
    Table,
    form=TableForm,
    formset=TableUniqueFormset,
    fields=('row', 'col', 'seats'),
    extra=1,
    can_delete=False, # can_delete is set to False because you can't delete non-existence instance
    # min_num=1,
    # validate_min=True,
)


""" Timeslot forms """
class TimeslotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        exclude = ('seller',)


class TimeslotValidatedFormset(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        for form in self.forms:
            if form.cleaned_data.get('start', None):
              start_time = form.cleaned_data.get('start')
              end_time = form.cleaned_data.get('end')

              if start_time > end_time:
                  form.add_error('start', 'This value must be less than end time.')
                  form.add_error('end', 'This value must be greater than start time.')
                  return


TimeslotFormSet = inlineformset_factory(
    Seller,
    TimeSlot,
    form=TimeslotForm,
    formset=TimeslotValidatedFormset,
    fields=('start', 'end'),
    extra=1,
    can_delete=False,
    # min_num=1,
    # validate_min=True,
)


""" Product variants forms """
class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        exclude = ()


def unique_field_formset(field_name):
    class UniqueFieldFormset(BaseInlineFormSet):
        def clean(self):
            if any(self.errors):
                return

            values = set()
            for form in self.forms:
                value = form.cleaned_data.get(field_name, None)
                if value:
                    if value in values:
                        form.add_error(field_name, 'This value is duplicated.')
                        return
                    values.add(value)

    return UniqueFieldFormset


ProductVariationFormSet = inlineformset_factory(
    Variation,
    ProductVariation,
    formset=unique_field_formset('value'),
    form=ProductVariationForm,
    fields=('value',),
    extra = 1,
    can_delete=False,
    # min_num=1,
    # validate_min=True,
)


class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        exclude = ('product',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Fieldset('Product Variants',
                    Formset('variations')),
                self.helper.add_input(Submit('save', 'Save')),
                self.helper.add_input(Button('cancel', 'Cancel', css_class='btn-warning')),
            )
        )
    
    # def clean_name(self):
    #     cleaned_data = self.cleaned_data['name']
    #     try:
    #         Variation.objects.get(name=cleaned_data)
    #     except Variation.DoesNotExist:
    #         pass
    #     else:
    #         raise ValidationError('Duplicate variation names for one product.')
    #     return cleaned_data