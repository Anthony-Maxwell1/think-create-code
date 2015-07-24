{% block content %}// Title: {{ object.title }}
// Author: {{ object.author }}
// Created: {{ object.created_at }}
// Downloaded: {% now "jS F Y H:i" %}
// URL: {{ BASE_URL }}{{ object.get_absolute_url }}

{{ object.code|safe }}
{% endblock %}
