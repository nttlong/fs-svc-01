{{- define "python3-args" -}}
- elastic_search.server=$(elastic_search.server)
- elastic_search.prefix_index=$(elastic_search.prefix_index)
- db.host=$(db.host)
- db.port=$(db.port)
- admin_db_name=$(admin_db_name)
- temp_directory=$(temp_directory)
- rabbitmq.server=$(rabbitmq.server)
- rabbitmq.port=$(rabbitmq.port)
{{- end }}




