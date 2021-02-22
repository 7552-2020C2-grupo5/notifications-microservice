"""Helper functions for the project."""

from flask_restx import fields


class IntegerOrStringField(fields.Raw):
    def schema(self):
        schema = dict()
        schema['oneOf'] = [{"type": "string"}, {"type": "integer"}]
        return schema
