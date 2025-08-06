# -*- __init__.py: python ; coding: utf-8 -*-
import base64
import pickle
import re
from enum import Enum

from pandas import DataFrame
from sqlalchemy import or_
from sqlalchemy.orm import Query

from yui import UnitType
from yut import json_dump, copy_obj, get_attr, json_load, set_attr

_DATABASE_URI = None


def set_database_uri(db_uri):
    global _DATABASE_URI
    _DATABASE_URI = db_uri


def get_database_uri():
    return _DATABASE_URI


class Op(Enum):
    EQU = '='
    GE = '>='  # >=
    GT = '>'  # >
    LE = '<='  # <=
    LT = '<'  # <
    NEQ = '!='  # !=
    BETWEEN = '~'
    IN = '@'
    NOT_IN = '!@'  # not in
    LIKE = '*'
    NOT_LIKE = '!*'
    LIKE_IN = '**'  # like A or like B or like C ...

    def filter_q(self, query: Query, field, value) -> Query:
        if self == Op.LIKE_IN and isinstance(value, str):  # LIKE_IN 支持'',''分割的多个str自动转换
            value = value.split('|')
        d = {
            Op.EQU: lambda q, a, v: q.filter(a == v),
            Op.GE: lambda q, a, v: q.filter(a >= v),
            Op.GT: lambda q, a, v: q.filter(a > v),
            Op.LE: lambda q, a, v: q.filter(a <= v),
            Op.LT: lambda q, a, v: q.filter(a < v),
            Op.NEQ: lambda q, a, v: q.filter(a != v),
            Op.BETWEEN: lambda q, a, v: q.filter(a.between(v[0], v[1])),
            Op.IN: lambda q, a, v: q.filter(a.in_(v)),
            Op.NOT_IN: lambda q, a, v: q.filter(not a.in_(v)),
            Op.LIKE: lambda q, a, v: q.filter(a.like(f'%{v}%')),
            Op.NOT_LIKE: lambda q, a, v: q.filter(not a.like(f'%{v}%')),
            Op.LIKE_IN: lambda q, a, v: q.filter(or_(*[a.like(f'%{vv}%') for vv in v])),
        }
        return d[self](query, field, value)

    def query_df(self, data_frame: DataFrame, column_name: str, value) -> DataFrame:
        if self == Op.LIKE_IN and isinstance(value, str):  # LIKE_IN 支持逗号分割的多个str自动转换
            value = value.split('|')
        d = {
            Op.EQU: lambda df, a, v: df.query(f"{a} == @v"),
            Op.GE: lambda df, a, v: df.query(f"{a} >= @v"),
            Op.GT: lambda df, a, v: df.query(f"{a} > @v"),
            Op.LE: lambda df, a, v: df.query(f"{a} <= @v"),
            Op.LT: lambda df, a, v: df.query(f"{a} < @v"),
            Op.NEQ: lambda df, a, v: df.query(f"{a} != @v"),
            Op.LIKE: lambda df, a, v: df.query(f'{a}.str.contains(@v, na=False)'),
            Op.IN: lambda df, a, v: df.query(f'{a} in @v'),
            Op.BETWEEN: lambda df, a, v: df.query(f"@v[0] <= {a} <= @v[1]"),
            Op.LIKE_IN: lambda df, a, v: df.query(
                '|'.join([f'{a}.str.contains(@v[{i}],na=False)' for i, vv in enumerate(v)])),
        }
        return d[self](data_frame, column_name, value)


class ColumnSpec:
    def __init__(self, **kwargs):
        copy_obj(self, kwargs)
        self.name = get_attr(self, 'name')
        self.comment = get_attr(self, 'comment')
        self.dtype = get_attr(self, 'dtype')
        self.key = get_attr(self, 'key', self.name)
        self.label = get_attr(self, 'comment')

    def title(self):
        return self.comment if self.comment else self.name

    def perfect_column_width(self):
        cw, min_w, max_w = 80, 50, 500
        if not self.dtype:
            return cw
        p = r'.*\(([\d| ]*)[,|\)]'
        d_len = ''.join(re.findall(p, self.dtype))
        if d_len:
            d_len = int(d_len)
            cw = d_len * 10
        cw = min(max_w, cw)
        cw = max(min_w, cw)
        return cw

    def unit_type(self) -> UnitType:
        return get_attr(self, 'utype')

    def is_link(self):
        return get_attr(self, 'link_to') is not None

    def __repr__(self):
        s = ', '.join(["%s=%r" % (k, v) for k, v in self.__dict__.items()])
        return f'<ColumnSpec "{self.key}": {s}>'


def to_column_spec(o):
    if isinstance(o, ColumnSpec):
        return o
    if isinstance(o, dict):
        return ColumnSpec(**o)
    else:
        return ColumnSpec(**o.__dict__)


def set_attr_to_specs(specs, col_name, attr, value):
    sp = None
    if type(specs) is dict:
        sp = specs[col_name]
    else:
        ss = [s for s in specs if s.name == col_name]
        if len(ss) == 1:
            sp = ss[0]
    if sp:
        set_attr(sp, attr, value)


class QueryR:
    def __init__(self, dataframe, columns_specs):
        self._dataframe = dataframe
        self._column_specs = columns_specs

    def dataframe(self) -> DataFrame:
        return self._dataframe

    def column_specs(self):
        return self._column_specs

    def encode(self):
        """
        将query查询得到的结果（_result:DataFrame）转换为json，包含以下内容:
        'spec': 对应Selection的column_spec
        'data': 序列化+base64编码后的查询结果对象
        :return:
        """
        encoded_obj = base64.b64encode(pickle.dumps(self._dataframe)).decode('utf-8')
        return {'spec': json_dump(self._column_specs),
                'data': encoded_obj,
                }

    @staticmethod
    def decode(json):
        spec = json_load(json['spec'], cls=ColumnSpec)
        decoded_obj = base64.b64decode(json['data'].encode('utf-8'))  # base64.b64encode返回的是字节数据，需要转为utf-8字符串。
        df = pickle.loads(decoded_obj)
        return QueryR(df, spec)
