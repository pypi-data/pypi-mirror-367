.. django-htpy documentation master file, created by
   sphinx-quickstart on Tue Aug  5 13:19:46 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-htpy documentation
=========================

``django-htpy`` provides Django specific add-ons for the `htpy library`_.

.. _htpy library: https://htpy.dev/

.. note:: What's that?

    If you've not seen it, ``htpy``:

        … makes writing HTML in plain Python fun and efficient, without a
        template language.

    It's particularly good for UI components. It solves the *problem of slots*
    in a way that couples nicely with the page authoring approach of the
    Django Template Language.

.. New Here?
.. ---------
..
.. To begin you should read the introductory essay.
..
.. .. toctree::
..    :maxdepth: 1
..
..    why
..

Setup
-----

First install ``django-htpy``::

    $ pip install django-htpy

Then add ``django_htpy`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        "django_htpy",
        "tests",
    ]

That's it. You're ready to go.

Usage
-----

``htpy`` already `works well with Django
<https://htpy.dev/django/>`_. In particular, you can
use htpy when preparing the context for your existing templates::

    context = {
        "content": h1["Welcome to my site!"],
    }

… and there's a template backend that let's you specify an ``hypy`` component
as your view's template.

``django-htpy`` adds a couple of specific add-ons to ease the integration.

The ``dtl`` renderable
~~~~~~~~~~~~~~~~~~~~~~

The ``dtl`` renderable embeds a Django template in your ``htpy`` components:

.. code-block:: python

    from django.template import engines
    from django_htpy import dtl

    django_engine = engines["django"]
    template = django_engine.from_string("Hello {{ name }}!")
    context = {
        "name": "django-htpy",
    }
    print(dtl(template, context)))
    # Outputs: "Hello django-htpy!"

The ``dtl`` function accepts either a template instance, as shown here, or a path to a template file, handles resolving that, renders the context, and wraps it as ``Markup`` so ``htpy`` knows it's already been escaped.

.. warning:: autoescape required

    If you disable autoescape in your template you'll need to handle safely
    injecting the template output into your component yourself, where ``htpy``
    will apply the escaping.

    Don't disable autoescape!

The ``htpy`` template tag
~~~~~~~~~~~~~~~~~~~~~~~~~

``django-htpy`` also provides an ``htpy`` template tag that allows rendering
components from your Django templates.

Assuming a component like this, at `tests.components.py`::

    from htpy import Renderable, h1

    def page_title(title: str) -> Renderable:
        return h1[title]

Then you can render the component in your template like so::

    template = django_engine.from_string("""
    {% load htpy %}
    {% htpy 'tests.components.page_title' title %}
    """)
    output = template.render({
        "title": "Testing",
    })

The ``htpy`` tag takes the the dotted import path to the component as the first
argument and will pass along any other ``*args`` and ``**kwargs`` that are
provided.
