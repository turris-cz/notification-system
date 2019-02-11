import json
import pytest

from notifylib.api import Api


@pytest.fixture
def volatile_dir(tmpdir):
    return tmpdir.mkdir('volatile')


@pytest.fixture
def persistent_dir(tmpdir):
    return tmpdir.mkdir('persistent')


@pytest.fixture
def plugin_dir(tmpdir):
    return tmpdir.mkdir('plugins')


@pytest.fixture
def simple_plugin_dir(plugin_dir):
    return plugin_dir.mkdir('simple')


@pytest.fixture
def simple_plugin():
    return """actions:
  - name: reject
    title: "{% trans %}Reject current update{% endtrans %}"
    command: updater --reject-update
  - name: dummy
    title: "{% trans %}Dummy action{% endtrans %}"
    command: /bin/true
templates:
  - type: simple_message
    supported_media:
      - plain
      - html
    src: simple.j2
  - type: complex_message
    supported_media:
      - plain
      - html
      - email
    src: complex.j2
notifications:
  - name: simple
    template: simple_message
    actions:
      - dummy
    version: 1
  - name: complex
    template: complex_message
    severity: error
    persistent: True
    explicit_dismiss: False
    actions:
      - reject
    version: 1
"""


@pytest.fixture
def template_simple():
    return """{% if media == 'html' %}
<h3>{{ _("Simple message") }}</h3>
<p>
    {{ _("HTML rendered message") }}: {{ message }}
</p>
{% else %}
= {{ _("Simple message") }} =
{{ _("Message") }}: {{message}}
{% endif %}"""


@pytest.fixture
def template_complex():
    return """{% if media == 'html' %}
<h1>{{ _("Complex message") }}</h1>
<p>Lorem ipsum dolor sit amet</p>
<p>
    {{ _("First message") }}: {{ message }}
    <br>
    {{ _("Second message") }}: {{ message2 }}
</p>
{% else %}
[{{ _("Complex message") }}]
{{ _("First message") }}: {{message}}
{{ _("Second message") }}: {{ message2 }}
{% endif %}"""


@pytest.fixture
def config(volatile_dir, persistent_dir, plugin_dir):
    return {
        'settings': {
            'volatile_dir': volatile_dir,
            'persistent_dir': persistent_dir,
            'plugin_dir': plugin_dir,
        }
    }


@pytest.fixture
def user_opts():
    return {
        'skel_id': 'simple.simple',
        'data': json.loads('{"message": "dragons kittens turtles sloths"}')
    }


@pytest.fixture
def create_plugin(simple_plugin_dir, simple_plugin, template_simple, template_complex):
    plug = simple_plugin_dir.join('plugin.yml')
    plug.write(simple_plugin)

    tpl_dir = simple_plugin_dir.mkdir('templates')
    tpl_simple = tpl_dir.join('simple.j2')
    tpl_simple.write(template_simple)

    tpl_complex = tpl_dir.join('complex.j2')
    tpl_complex.write(template_complex)


@pytest.fixture
def api(config, create_plugin):
    return Api(confdict=config)
