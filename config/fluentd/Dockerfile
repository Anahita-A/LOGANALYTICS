# config/fluentd/Dockerfile
FROM fluent/fluentd:v1.14

# Use root account to use apk
USER root

# Install plugins
RUN apk add --no-cache --update \
    && gem install fluent-plugin-s3 -v "~> 1.6.0" \
    && gem sources --clear-all \
    && apk del build-base \
    && rm -rf /tmp/* /var/tmp/* /usr/lib/ruby/gems/*/cache/*.gem

USER fluent