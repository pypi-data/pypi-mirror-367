import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import InvalidPage, Paginator
from django.forms import models as model_forms
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import View

from .response import InertiaResponse

from djantic import ModelSchema

# Avoid RemovedInDjango40Warning on Django 3.0+
if django.VERSION >= (3, 0):
    from django.utils.translation import gettext as _
else:
    from django.utils.translation import ugettext as _


class InertiaResponseMixin:
    """
    Mixin that provides InertiaResponse rendering capability.
    Can be used with any view class to enable Inertia.js integration.
    """
    
    template_name = None
    
    def get_context_data(self, **kwargs):
        """
        Takes a set of keyword arguments to use as the base context, and
        returns a context dictionary to use for the view.
        Must be overridden when using InertiaResponseMixin.
        """
        msg = "'%s' must override 'get_context_data()' when using InertiaResponseMixin"
        raise ImproperlyConfigured(msg % self.__class__.__name__)
    
    def get_template_names(self):
        """
        Returns a set of template names that may be used when rendering
        the response. Must define 'template_name' when using InertiaResponseMixin.
        """
        if self.template_name is not None:
            return [self.template_name]

        msg = "'%s' must define 'template_name' when using InertiaResponseMixin"
        raise ImproperlyConfigured(msg % self.__class__.__name__)
    
    def render_to_response(self, context, **response_kwargs):
        """
        Given a context dictionary, returns an InertiaResponse.
        """
        return InertiaResponse(
            self.request, self.get_template_names()[0], context, **response_kwargs
        )



class GenericView(View):
    """
    A generic base class for building template and/or form views.
    """

    form_class = None
    template_name = None

    # Form instantiation

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        msg = "'%s' must either define 'form_class' or override 'get_form_class()'"
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(self, data=None, files=None, **kwargs):
        """
        Given `data` and `files` QueryDicts, and optionally other named
        arguments, and returns a form.
        """
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)

    # Response rendering

    def get_template_names(self):
        """
        Returns a set of template names that may be used when rendering
        the response.
        """
        if self.template_name is not None:
            return [self.template_name]

        msg = (
            "'%s' must either define 'template_name' or override "
            + "'get_template_names()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_context_data(self, **kwargs):
        """
        Takes a set of keyword arguments to use as the base context, and
        returns a context dictionary to use for the view.
        """
        return kwargs

    def render_to_response(self, context, **response_kwargs):
        """
        Given a context dictionary, returns an HTTP response.
        """
        return InertiaResponse(
            self.request, self.get_template_names()[0], context, **response_kwargs
        )


class TemplateView(GenericView):
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)


class FormView(GenericView):
    success_url = None

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        if self.success_url is None:
            msg = "'%s' must define 'success_url' or override 'get_success_url()'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        return self.success_url


class GenericModelView(View):
    """
    Base class for all model generic views.
    """

    model = None
    fields = None

    # Object lookup parameters. These are used in the URL kwargs, and when
    # performing the model instance lookup.
    # Note that if unset then `lookup_url_kwarg` defaults to using the same
    # value as `lookup_field`.
    lookup_field = "pk"
    lookup_url_kwarg = None

    # All the following are optional, and fall back to default values
    # based on the 'model' shortcut.
    # Each of these has a corresponding `.get_<attribute>()` method.
    queryset = None
    form_class = None
    template_name = None
    context_object_name = None

    # Pagination parameters.
    # Set `paginate_by` to an integer value to turn pagination on.
    paginate_by = None
    page_kwarg = "page"

    # Suffix that should be appended to automatically generated template names.
    template_name_suffix = None
    
    # Template extension configuration
    template_extension = getattr(settings, 'INERTIA_TEMPLATE_EXTENSION', 'html')

    # Djantic serialization
    serializer_class = None

    # Djantic serialization

    def get_serializer_class(self):
        """
        Returns the serializer class to use for serializing model instances.
        """
        return self.serializer_class

    def serialize_object(self, obj):
        """
        Serializes a single model instance using the serializer class.
        """
        serializer_class = self.get_serializer_class()
        if serializer_class is None:
            return obj
        
        if not issubclass(serializer_class, ModelSchema):
            msg = "'%s' serializer_class must be a subclass of djantic.ModelSchema"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        
        return serializer_class.from_django(obj).model_dump()

    def serialize_object_list(self, object_list):
        """
        Serializes a list of model instances using the serializer class.
        """
        serializer_class = self.get_serializer_class()
        if serializer_class is None:
            return object_list
        
        if not issubclass(serializer_class, ModelSchema):
            msg = "'%s' serializer_class must be a subclass of djantic.ModelSchema"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        
        return [serializer_class.from_django(obj).model_dump() for obj in object_list]

    # Queryset and object lookup

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        try:
            lookup = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        except KeyError:
            msg = "Lookup field '%s' was not provided in view kwargs to '%s'"
            raise ImproperlyConfigured(
                msg % (lookup_url_kwarg, self.__class__.__name__)
            )

        return get_object_or_404(queryset, **lookup)

    def get_queryset(self):
        """
        Returns the base queryset for the view.

        Either used as a list of objects to display, or as the queryset
        from which to perform the individual object lookup.
        """
        if self.queryset is not None:
            return self.queryset._clone()

        if self.model is not None:
            return self.model._default_manager.all()

        msg = (
            "'%s' must either define 'queryset' or 'model', or override "
            + "'get_queryset()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    # Form instantiation

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class is not None:
            return self.form_class

        if self.model is not None and self.fields is not None:
            return model_forms.modelform_factory(self.model, fields=self.fields)

        msg = (
            "'%s' must either define 'form_class' or both 'model' and "
            "'fields', or override 'get_form_class()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def get_form(self, data=None, files=None, **kwargs):
        """
        Returns a form instance.
        """
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)

    # Pagination

    def get_paginate_by(self):
        """
        Returns the size of pages to use with pagination.
        """
        return self.paginate_by

    def get_paginator(self, queryset, page_size):
        """
        Returns a paginator instance.
        """
        return Paginator(queryset, page_size)

    def paginate_queryset(self, queryset, page_size):
        """
        Paginates a queryset, and returns a page object.
        """
        paginator = self.get_paginator(queryset, page_size)
        page_kwarg = self.kwargs.get(self.page_kwarg)
        page_query_param = self.request.GET.get(self.page_kwarg)
        page_number = page_kwarg or page_query_param or 1
        try:
            page_number = int(page_number)
        except ValueError:
            if page_number == "last":
                page_number = paginator.num_pages
            else:
                msg = "Page is not 'last', nor can it be converted to an int."
                raise Http404(_(msg))

        try:
            return paginator.page(page_number)
        except InvalidPage as exc:
            msg = "Invalid page (%s): %s"
            raise Http404(_(msg) % (page_number, str(exc)))

    # Response rendering

    def get_context_object_name(self, is_list=False):
        """
        Returns a descriptive name to use in the context in addition to the
        default 'object'/'object_list'.
        """
        if self.context_object_name is not None:
            return self.context_object_name

        elif self.model is not None:
            fmt = "%s_list" if is_list else "%s"
            return fmt % self.model._meta.object_name.lower()

        return None

    def get_context_data(self, **kwargs):
        """
        Returns a dictionary to use as the context of the response.

        Takes a set of keyword arguments to use as the base context,
        and adds the following keys:

        * Optionally, '{context_object_name}' or '{context_object_name}_list'
        
        If a serializer_class is defined, model instances will be automatically
        serialized using djantic.
        """
        if getattr(self, "object", None) is not None:
            context_object_name = self.get_context_object_name()
            if context_object_name:
                kwargs[context_object_name] = self.serialize_object(self.object)

        if getattr(self, "object_list", None) is not None:
            context_object_name = self.get_context_object_name(is_list=True)
            if context_object_name:
                kwargs[context_object_name] = self.serialize_object_list(self.object_list)

        return kwargs

    def get_template_names(self):
        """
        Returns a list of template names to use when rendering the response.

        If `.template_name` is not specified, then defaults to the following
        pattern: "{app_label}/{model_name}{template_name_suffix}.{extension}"
        where extension is determined by INERTIA_TEMPLATE_EXTENSION setting.
        """
        if self.template_name is not None:
            return [self.template_name]

        if self.model is not None and self.template_name_suffix is not None:
            return [
                "%s/%s%s.%s"
                % (
                    self.model._meta.app_label,
                    self.model._meta.object_name.lower(),
                    self.template_name_suffix,
                    self.template_extension,
                )
            ]

        msg = (
            "'%s' must either define 'template_name' or 'model' and "
            "'template_name_suffix', or override 'get_template_names()'"
        )
        raise ImproperlyConfigured(msg % self.__class__.__name__)

    def render_to_response(self, context, **response_kwargs):
        """
        Given a context dictionary, returns an HTTP response.
        """
        return InertiaResponse(
            self.request, self.get_template_names()[0], context, **response_kwargs
        )


# The concrete model views


class ListView(GenericModelView):
    template_name_suffix = "_list"
    allow_empty = True

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by()

        if not self.allow_empty and not queryset.exists():
            raise Http404

        if paginate_by is None:
            # Unpaginated response
            self.object_list = queryset
            context = self.get_context_data(
                page_obj=None,
                is_paginated=False,
                paginator=None,
            )
        else:
            # Paginated response
            page = self.paginate_queryset(queryset, paginate_by)
            self.object_list = page.object_list
            context = self.get_context_data(
                page_obj=page,
                is_paginated=page.has_other_pages(),
                paginator=page.paginator,
            )

        return self.render_to_response(context)


class DetailView(GenericModelView):
    template_name_suffix = "_detail"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)


class CreateView(GenericModelView):
    success_url = None
    template_name_suffix = "_form"

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        try:
            return self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = (
                "No URL to redirect to. '%s' must provide 'success_url' "
                "or define a 'get_absolute_url()' method on the Model."
            )
            raise ImproperlyConfigured(msg % self.__class__.__name__)


class UpdateView(GenericModelView):
    success_url = None
    template_name_suffix = "_form"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(instance=self.object)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=self.object,
        )
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        try:
            return self.success_url or self.object.get_absolute_url()
        except AttributeError:
            msg = (
                "No URL to redirect to. '%s' must provide 'success_url' "
                "or define a 'get_absolute_url()' method on the Model."
            )
            raise ImproperlyConfigured(msg % self.__class__.__name__)


class DeleteView(GenericModelView):
    success_url = None
    template_name_suffix = "_confirm_delete"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.success_url is None:
            msg = "No URL to redirect to. '%s' must define 'success_url'"
            raise ImproperlyConfigured(msg % self.__class__.__name__)
        return self.success_url
