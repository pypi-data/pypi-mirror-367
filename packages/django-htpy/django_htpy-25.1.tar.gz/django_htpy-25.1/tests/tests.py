from django.template import engines
from django.test import TestCase
from django_htpy import dtl

from .components import page_title


django_engine = engines["django"]


class DjangoHtpyTestCase(TestCase):
    def test_dtl_with_template_instance(self):
        template = django_engine.from_string("Hello {{ name }}!")
        context = {
            "name": "django-htpy",
        }
        self.assertEqual(str(dtl(template, context)), "Hello django-htpy!")

    def test_dtl_with_template_path(self):
        template = "hello.txt"
        context = {
            "name": "django-htpy",
        }
        self.assertEqual(str(dtl(template, context)).strip(), "Hello django-htpy!")

    def test_component_loading_as_template(self):
        expected_output = str(page_title("Testing"))
        template = django_engine.from_string("""
        {% load htpy %}
        {% htpy 'tests.components.page_title' title %}
        """)
        output = template.render({
            "title": "Testing",
        })
        self.assertEqual(expected_output, output.strip())
