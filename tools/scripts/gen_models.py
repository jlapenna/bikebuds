#!/usr/bin/python

"""
$ xclip -o | tools/scripts/gen_models.py SegmentEffort
"""

import argparse
import functools
import sys

CONVERTER_TEMPLATE = """

class _%(model)sConverter(object):
    __ALL_FIELDS = SortedSet(
    %(field_names)s
    )
    __INCLUDE_IN_INDEXES = SortedSet(['id'])
    __STORED_FIELDS = SortedSet([
        __ALL_FIELDS,  # TODO
    ])
    EXCLUDE_FROM_INDEXES = list(__ALL_FIELDS - __INCLUDE_IN_INDEXES)

    @classmethod
    def to_entity(cls, %(model_snake)s, parent=None):
        properties_dict = %(model_snake)s.to_dict()
        properties_dict['id'] = %(model_snake)s.id

        entity = Entity(
            ds_util.client.key('%(model)s', int(%(model_snake)s.id), parent=parent),
            exclude_from_indexes=cls.EXCLUDE_FROM_INDEXES,
        )
%(adapters)s
        entity.update(properties_dict)
        return entity
"""

ADAPTER_TEMPLATE = """\
        if %(model_snake)s.%(field)s is not None:
            properties_dict['%(field)s'] = %(adapter)s
"""


FIELD_TYPE_MAP = {
    'integer': 'fields.Integer',
    'long': 'fields.Integer',
    'string': 'fields.String',
    'float': 'fields.Float',
    'DateTime': 'fields.DateTime',
    'boolean': 'fields.Boolean',
}


def to_snake(s):
    return functools.reduce(
        lambda x, y: x + ('_' if y.isupper() else '') + y, s
    ).lower()


def to_camel(s):
    return ''.join(x.capitalize() or '_' for x in s.split('_'))


def gen_converter(model, field_type_pairs):
    adapters = []
    for field, ft in field_type_pairs:
        subs = {}
        subs.update(
            {
                'model': model,
                'field': field,
                'field_camel': to_camel(field),
                'model_snake': to_snake(model),
            }
        )
        if ft == 'DateTime':
            if field.endswith('_local'):
                subs['adapter'] = (
                    '%(model_snake)s.%(field)s.replace(tzinfo=None)' % subs
                )
            else:
                subs['adapter'] = (
                    '%(model_snake)s.%(field)s.astimezone(pytz.UTC).replace(tzinfo=pytz.UTC)'
                    % subs
                )
        elif ft in FIELD_TYPE_MAP:
            if field.endswith('_time'):
                subs['adapter'] = '%(model_snake)s.%(field)s.seconds' % subs
            else:
                subs['adapter'] = '%(model_snake)s.%(field)s' % subs
        else:
            subs['adapter'] = (
                '_%(field_camel)sConverter.to_entity(%(model_snake)s.%(field)s)' % subs
            )
        adapters.append(ADAPTER_TEMPLATE % subs)
    adapters = '\n'.join(adapters)
    print(
        CONVERTER_TEMPLATE
        % {
            'model': model,
            'model_snake': to_snake(model),
            'field_names': [f[0] for f in field_type_pairs],
            'adapters': adapters,
        }
    )
    pass


def gen_api_model(model, field_type_pairs):
    print("%s_model = api.model(\n'%s', \n{" % (to_snake(model), model))

    for ft in field_type_pairs:
        print(
            "        %s'%s': %s,"
            % (
                '' if ft[1] in FIELD_TYPE_MAP else '# ',
                ft[0],
                FIELD_TYPE_MAP.get(
                    ft[1], 'fields.Nested(%s_model, skip_none=True)' % to_snake(ft[1])
                ),
            )
        )
    print("    }\n)")


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('model', metavar='N', type=str, nargs='+')
    args = parser.parse_args()

    model = args.model[0]

    spec = sys.stdin.read().strip().split('\n')
    fields = map(lambda x: (x.split('\t')[0]), spec)[::2]
    types = map(lambda x: (x.split('\t')[0]), spec)[1::2]
    field_type_pairs = zip(fields, types)
    gen_api_model(model, field_type_pairs)
    print('\n# CONVERTER\n')
    gen_converter(model, field_type_pairs)


if __name__ == '__main__':
    main()
