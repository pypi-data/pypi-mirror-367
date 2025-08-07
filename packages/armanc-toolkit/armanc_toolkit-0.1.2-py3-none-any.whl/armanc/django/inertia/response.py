import json
from django.conf import settings
from django.contrib import messages
from django.utils.html import conditional_escape
from django.utils.module_loading import import_string
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from inertia.http import InertiaRequest, BaseInertiaResponseMixin

from .adapters.registry import JSContext


def get_messages(request):
    """Extract Django messages for inclusion in Inertia responses."""
    default_level_tag = messages.DEFAULT_TAGS[messages.SUCCESS]
    return [
        {
            "level": messages.DEFAULT_TAGS.get(message.level, default_level_tag),
            "content": conditional_escape(message.message),
        }
        for message in messages.get_messages(request)
    ]


class InertiaResponse(BaseInertiaResponseMixin, HttpResponse):
    def __init__(
        self,
        request,
        component,
        data=None,
        template_data=None,
        encoder=DjangoJSONEncoder,
        safe=True,
        json_dumps_params=None,
        *args,
        **kwargs,
    ):
        additional_context = {
            name: import_string(provider)(request)
            for name, provider 
            in getattr(settings, 'INERTIA_CONTEXT_PROVIDERS', {}).items()
        }

        data = {
            **additional_context,
            'messages': get_messages(request),
            **data,
        }

        js_context = JSContext()
        data = js_context.pack(data)

        self.request = InertiaRequest(request)
        self.component = component
        self.props = data or {}
        self.template_data = template_data or {}

        if self.request.is_inertia():
            if safe and not isinstance(data, dict):
                raise TypeError(
                    "In order to allow non-dict objects to be serialized set the "
                    "safe parameter to False."
                )

            if json_dumps_params is None:
                json_dumps_params = {}
            
            kwargs.setdefault("content_type", "application/json")
            headers = kwargs.pop('headers', {})
            headers.setdefault('Vary', 'X-Inertia')
            headers.setdefault('X-Inertia', 'true')
            kwargs['headers'] = headers
            data = json.dumps(self.page_data(), cls=encoder, **json_dumps_params)
            return super().__init__(content=data, **kwargs)


        data = json.dumps(self.page_data(), cls=encoder)
        content = self.build_first_load(data)
        super().__init__(
            *args,
            content=content,
            **kwargs,
        )
