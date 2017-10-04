/* Auto generated JS file that inlines a given file */
{% if should_docwrite %}
    document.write({{ stringified }});
{% else %}
    window.{{ name }} = {{ stringified }};
{% endif %}


