import newrelic.agent
from django.conf import settings


class NewRelicMiddleware(object):

    def debug(self, message):
        if self.debug_enabled:
            msg = '[new relic extensions]: %s' % message
            print(msg)

    def add(self, key, value):
        if callable(value):
            value = value()
        if self.debug_enabled:
            msg = '%s: %s' % (key, value)
            print(msg)
        else:
            newrelic.agent.add_custom_parameter(key, value)

    def process_response(self, request, response):
        enabled = getattr(settings, 'NEW_RELIC_EXTENSIONS_ENABLED', False)
        if not enabled:
            return response

        attributes = getattr(settings, 'NEW_RELIC_EXTENSIONS_ATTRIBUTES', None)
        self.debug_enabled = getattr(settings, 'NEW_RELIC_EXTENSIONS_DEBUG', True)

        if not attributes:
            self.debug('No attributes specified.')
            return response

        for key in attributes.keys():

            request_attr = getattr(request, key, None)
            if not request_attr:
                msg = "HttpRequest instance doesn't have '%s' attribute." % key
                self.debug(msg)
                continue

            if isinstance(attributes[key], dict):
                for subkey in attributes[key].keys():
                    #if request is a dict, get the value one way, otherwise use getattr
                    if isinstance(request_attr, dict):
                        subvalue = request_attr.get(subkey, None)
                    else:
                        subvalue = getattr(request_attr, subkey, None)
                    if not subvalue:
                        msg = "'%s' doesn't have '%s' attribute." % (key, subkey)
                        self.debug(msg)
                        continue
                    self.add(attributes[key][subkey], subvalue)
            else:
                self.add(attributes[key], request_attr)

        return response



