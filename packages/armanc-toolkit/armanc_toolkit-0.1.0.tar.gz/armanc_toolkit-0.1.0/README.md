# Armanc Toolkit

A comprehensive toolkit containing various utilities for Django and Python development, with enhanced Inertia.js integration.

## Features

### Django Inertia Integration

Enhanced Inertia.js support for Django applications with:

- **InertiaResponse**: Advanced response handling with message support
- **View Mixins**: Complete set of class-based views for Inertia.js
  - `InertiaResponseMixin`: Base mixin for Inertia responses
  - `GenericView`: Base view with form handling
  - `TemplateView`: Simple template rendering
  - `FormView`: Form handling with validation
  - `ListView`: Model list views with pagination
  - `DetailView`: Single object detail views
  - `CreateView`: Object creation with forms
  - `UpdateView`: Object editing with forms
  - `DeleteView`: Object deletion with confirmation

## Installation

```bash
pip install armanc-toolkit
```

## Usage

### Django Settings

Add the Inertia app to your Django settings:

```python
INSTALLED_APPS = [
    # ... your other apps
    'armanc.django.inertia',
]
```

### Views

```python
from armanc.django.inertia.views import TemplateView, ListView, CreateView
from django.contrib.auth.models import User

class DashboardView(TemplateView):
    template_name = 'Dashboard'

class UserListView(ListView):
    model = User
    template_name = 'Users/Index'
    paginate_by = 10

class UserCreateView(CreateView):
    model = User
    template_name = 'Users/Create'
    fields = ['username', 'email', 'first_name', 'last_name']
```

### Response Handling

```python
from armanc.django.inertia.response import InertiaResponse

def my_view(request):
    return InertiaResponse(
        request,
        component='MyComponent',
        props={'data': 'example'}
    )
```

## Requirements

- Python >=3.13
- Django >=4.2,<6.0
- djantic2 >=1.0.5
- inertia-django >=1.2.0
- telepath >=0.3.1

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
