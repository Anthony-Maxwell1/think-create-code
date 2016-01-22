{% block content %}// Title: {{ object.artwork.title }}
// Author: {{ object.artwork.author }}
// Created: {{ object.artwork.created_at }}
// Downloaded: {% now "jS F Y H:i" %}
// URL: {{ BASE_URL }}{{ object.get_absolute_url }}

{{ object.artwork.code|safe }}
{% endblock %}
