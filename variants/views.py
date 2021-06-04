from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.db import transaction

from services.models import Seller, Product
from variants.forms import (
    TableFormSet,
    TimeslotFormSet,
    ProductVariationFormSet,
    VariationForm,
)
from variants.models import Variation, Table, TimeSlot, ProductVariation
from users.views import AdminRequiredMixin


""" Table (in Sellers like Restaurant) Views """
class TableCreateView(AdminRequiredMixin, FormView):
    template_name = 'variants/table.html'
    form_class = TableFormSet

    def get_object(self):
        return Seller.objects.get(slug=self.kwargs['seller_slug'])
    
    def form_valid(self, form):
        if form.is_valid():
            updated_items = set()
            for f in form:
                if f.cleaned_data.get('id', None):
                    updated_items.add(f.cleaned_data.get('id').id)
            table_items = form.instance.tables.values('id')
            for item in table_items:
                tid = item.get('id')
                if tid not in updated_items:
                    Table.objects.get(id=tid).delete()

            form.save()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def get_success_url(self):
        return reverse('seller-detail', kwargs={'seller_slug': self.get_object().slug})
    
 
""" Timeslot Views same as in Table above """
class TimeslotCreateView(AdminRequiredMixin, FormView):
    template_name = 'variants/timeslot.html'
    form_class = TimeslotFormSet

    def get_object(self):
        return Seller.objects.get(slug=self.kwargs['seller_slug'])
    
    def form_valid(self, form):
        if form.is_valid():
            updated_items = set()
            for f in form:
                if f.cleaned_data.get('id', None):
                    updated_items.add(f.cleaned_data.get('id').id)
            slot_items = form.instance.timeslots.values('id')
            for item in slot_items:
                tid = item.get('id')
                if tid not in updated_items:
                    TimeSlot.objects.get(id=tid).delete()

            form.save()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def get_success_url(self):
        return reverse('seller-detail', kwargs={'seller_slug': self.get_object().slug})
        

class VariationCreateView(AdminRequiredMixin, CreateView):
    model = Variation
    template_name = 'variations/create.html'
    form_class = VariationForm
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['variations'] = ProductVariationFormSet(self.request.POST)
        else:
            context['variations'] = ProductVariationFormSet()

        product_slug = self.kwargs.get('product_slug', None)
        context['product'] = Product.objects.get(slug=product_slug)

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        variations_formset = context['variations']
        product = context['product']
        variance_name = form.cleaned_data['name']

        try:
            Variation.objects.get(product=product, name=variance_name)
            form.add_error('name', 'This variance name already exists.')
            return super().form_invalid(form)

        except Variation.DoesNotExist:
            pass
        
        if variations_formset.is_valid():
            values = set()
            for f in variations_formset:
                if f.cleaned_data.get('value', None):
                    values.add(f.cleaned_data.get('value'))
            
            if len(values) == 0:
                product_slug = self.kwargs['product_slug']
                return redirect('product-detail', product_slug=product_slug)

            with transaction.atomic():
                form.instance.product = product
                self.object = form.save()
                variations_formset.instance = self.object
                variations_formset.save()
        else:
            return self.render_to_response(context)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('product-detail', kwargs={'product_slug': self.object.product.slug})


class VariationUpdateView(AdminRequiredMixin, UpdateView):
    model = Variation
    template_name = 'variations/update.html'
    form_class = VariationForm
    success_url = None

    def get_object(self):
        return Variation.objects.get(id=self.kwargs.get('pk'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            """ ProductVariationFormSet(instance=xxx) accepts empty formset values """
            context['variations'] = ProductVariationFormSet(self.request.POST, instance=self.get_object())
        else:
            context['variations'] = ProductVariationFormSet(instance=self.get_object())

        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        variance = self.get_object()
        variations_formset = context['variations']
        variance_name = form.cleaned_data['name']

        if variance.name != variance_name:
            try:
                Variation.objects.get(product=variance.product, name=variance_name)
                form.add_error('name', 'This variance name already exists.')
                return super().form_invalid(form)
            except Variation.DoesNotExist:
                pass
        
        if variations_formset.is_valid():
            values = set()
            updated_items = set()

            for f in variations_formset:
                if f.cleaned_data.get('value', None):
                    values.add(f.cleaned_data.get('value'))

                    if f.cleaned_data.get('id', None):
                        updated_items.add(f.cleaned_data.get('id').id)
            
            if len(values) == 0:
                return redirect(self.get_success_url())

            variant_items = self.get_object().product_variations.values('id')
            for item in variant_items:
                vid = item.get('id')
                if vid not in updated_items:
                    ProductVariation.objects.get(id=vid).delete()
            
            with transaction.atomic():
                variations_formset.save()

        else:
            return self.render_to_response(context)

            """ return super().form_invalid(form) or self.form_invalid(form) doesn't rerender form field errors with crispy Layout """
            """ context['form'] = form, which should be given when displaying formset non_form_errors """
            # return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('product-detail', kwargs={'product_slug': self.get_object().product.slug})


class VariationDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "variations/delete.html"

    def get_object(self):
        return Variation.objects.get(id=self.kwargs.get('pk'))
    
    def get_success_url(self):
        return reverse('product-detail', kwargs={'product_slug': self.object.product.slug})