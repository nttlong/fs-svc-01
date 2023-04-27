import datetime
import inspect
import json
import os
import typing
import uuid

import elasticsearch.exceptions
from elasticsearch import Elasticsearch
from typing import List
import pydantic
from enum import Enum


def get_all_index(client: Elasticsearch) -> List[str]:
    return list(client.indices.get_alias("*").keys())


def __well_form__(item):
    r = ["'", '"', ";", ":", ".", ",", ">", "<", "?", "+", "-", "*", "/", "%", "$", "#", "@", "\\", "!", "~",
         "`", "^", "]", "[", "(", ")"]
    ret = ""
    for x in item:
        if x in r:
            ret += f"\\{x}"
        else:
            ret += f"{x}"

    return ret


def __make_up_es_syntax_depriciate__(field_name: str, value):
    if '.' not in field_name:
        return {"term": {field_name: value}}
    else:
        path = ""
        items = field_name.split('.')
        for i in range(0, len(items) - 1):
            path += items[i] + "."
        path = path[:-1]
        return {
            "nested": {
                "path": items[0],
                "query": {
                    "term": {field_name: value}
                }
            }
        }


def __make_up_es_syntax__(field_name: str, value, is_match=False):
    assert isinstance(field_name, str)
    if type(value) == list:
        """
        "terms_set": {
      "programming_languages": {
        "terms": [ "c++", "java", "php" ],
        "minimum_should_match_field": "required_matches"
      }
    }
        """
        return {
            "terms_set": {
                field_name: {
                    "terms": value,
                    "minimum_should_match_script": {
                        "source": f"Math.min(params.num_terms, {len(value)})"
                    },
                }
            }

        }
    """
     return {
                    "terms":  {field_name: value},
                    "minimum_should _match": value.__len__()
                }
    """
    __key__ = "match" if is_match else "term"
    return {__key__: {field_name: value}}


def __make_up_es1__(field_name: str, value):
    items = field_name.split('.')
    if len(items) == 1: return {field_name: value}
    ptr = {}
    ret = ptr

    n = len(items)
    for i in range(0, n):
        index = n - i - 1
        ptr[items[index]] = {}
        ptr = ptr[items[index]]
    ptr[items[n - 1]] = {"value": value}
    return ret


def __check_is_painless_expr__(__es_expr__):
    return isinstance(__es_expr__, dict) and __es_expr__.get("script") and __es_expr__["script"].get(
        "script") and __es_expr__["script"]["script"].get("source")


class DocumentFields:
    def __init__(self, name: str = None):
        self.__name__ = name
        self.__es_expr__ = None
        self.__is_bool__ = False
        self.__value__ = None
        self.__has_set_value__ = None
        self.__minimum_number_should_match__ = None
        self.__norm__ = None
        self.__type__ = None
        self.__wrap_func__ = None
        self.__highlight_fields__ = []
        # self.is_equal = False

    def get_highlight_fields(self):
        ret = []
        for x in self.__highlight_fields__:
            ret += [DocumentFields(x)]
        return ret

    def set_type(self, str_type: str):
        self.__type__ = str_type
        return self

    def set_norms(self, enable: bool):
        """

        :param enable:
        :return:
        """
        """
        "properties": {
    "title": {
      "type": "text",
      "norms": false
    }
  }
        """
        self.__norm__ = enable
        return self

    def get_mapping(self):
        return {
            self.__name__:
                dict(

                    type=self.__type__,
                    norms=self.__norm__
                )
        }

    def set_minimum_should_match(self, value):
        self.__minimum_number_should_match__ = value
        self.__es_expr__["minimum_should_match"] = value

        return self

    def __neg__(self):
        ret = DocumentFields()
        ret.__es_expr__ = {
            "bool":
                {"must_not": self.__es_expr__}
        }
        return ret

    def startswith(self, item):
        ret = DocumentFields()
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """

            ret.__es_expr__ = {
                "regexp": {
                    self.__name__: {
                        "value": r"^" + item + ".*",
                        "flags": "ALL"
                    }
                }
            }
            return ret
        else:
            raise Exception("Not support")

    def endswith(self, item):
        ret = DocumentFields()
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """
            item = __well_form__(item)
            ret.__es_expr__ = {
                "regexp": {
                    self.__name__: f".*{item}$"
                }
            }
            return ret
        else:
            raise Exception("Not support")

    def __contains__(self, item):
        ret = DocumentFields()
        # self.__is_bool__ = True
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """
            import re
            item = __well_form__(item)

            ret.__es_expr__ = {
                "regexp": {
                    self.__name__: f".*{item}.*"
                }
            }
            return ret
        elif isinstance(item, list):
            """
            {
              "filtered": {
                "query": {
                  "match": { "title": "hello world" }
                },
                "filter": {
                  "terms": {
                    "tags": ["c", "d"]
                  }
                }
              }
            }
            """
            ret.__es_expr__ = {
                "terms": {
                    self.__name__: item
                }
            }
            self.__is_bool__ = True
            return ret
        else:
            raise Exception("Noty support")

    def contains(self, *args):
        ret = DocumentFields()
        values = args
        if isinstance(values, tuple):
            values = list(values)

        self.__is_bool__ = True
        ret.__es_expr__ = {
            "terms": {
                self.__name__: values
            }
        }
        return ret

    def __getattr__(self, item):
        if item.lower() == "id":
            item = "_id"
        if self.__name__ is not None:
            return DocumentFields(f"{self.__name__}.{item}")
        return DocumentFields(item)

    def __or__(self, other):
        ret = DocumentFields()
        if isinstance(other, DocumentFields):
            if self.__wrap_func__:
                left = {"bool": {"filter": self.__es_expr__}}
            elif self.__is_bool__:

                left = {"bool": self.__es_expr__}
            else:
                left = self.__es_expr__
            if other.__wrap_func__:
                right = {"bool": {"filter": other.__es_expr__}}
            elif other.__is_bool__:

                right = {"bool": other.__es_expr__}
            else:
                right = other.__es_expr__

            ret.__es_expr__ = {
                "should": [
                    left, right
                ]
            }
            ret.__is_bool__ = True
            ret.__highlight_fields__ = list(set(self.__highlight_fields__ + other.__highlight_fields__))
            return ret
        elif isinstance(other, dict):
            if not self.__is_bool__:

                left = self.__es_expr__
                right = other

                ret.__es_expr__ = {
                    "should": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
            else:
                left = {"bool": self.__es_expr__}
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
        else:
            raise Exception("invalid expr")

    def __and__(self, other):

        ret = DocumentFields()
        if isinstance(other, DocumentFields):
            if self.__wrap_func__:
                left = {"bool": {"filter": self.__es_expr__}}
            elif self.__is_bool__:

                left = {"bool": self.__es_expr__}
            else:
                left = self.__es_expr__
            if other.__wrap_func__:
                right = {"bool": {"filter": other.__es_expr__}}
            elif other.__is_bool__:
                right = {"bool": other.__es_expr__}
            else:
                right = other.__es_expr__

            ret.__es_expr__ = {
                "must": [
                    left, right
                ]
            }
            ret.__is_bool__ = True
            ret.__highlight_fields__ = list(set(self.__highlight_fields__ + other.__highlight_fields__))
            return ret
        elif isinstance(other, dict):
            if not self.__is_bool__:
                left = self.__es_expr__
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
            else:
                left = {"bool": self.__es_expr__}
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
        else:
            raise Exception("invalid expr")

    def __try_parse_date__(self, str_date):
        if not isinstance(str_date, str) or '+' not in str_date and str_date.__len__() >= 27:
            try:
                t = datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')

                return t, True
            except Exception as e:
                return None, False
        str_date_time = str_date.split('+')[0]
        try:
            t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
            tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
            ret = t + datetime.timedelta(tz.hour)
            return ret, True
        except Exception as e:
            return None, False

    def __eq__(self, other):

        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val

        if other is None:
            ret = DocumentFields()
            self.__is_bool__ = True

            ret.__es_expr__ = {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        elif isinstance(other, str):
            ret = DocumentFields()
            self.__is_bool__ = True
            # es_object = __make_up_es__(self.__name__, other)
            ret.__es_expr__ = __make_up_es_syntax__(self.__name__, other)
            return ret
        elif type(other) in [int, float, datetime.datetime, bool]:

            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}==params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            else:
                ret = DocumentFields()
                ret.__es_expr__ = {
                    "term": {
                        self.__name__: other
                    }
                }
                return ret
        elif isinstance(other, list):
            ret = DocumentFields()
            ret.__es_expr__ = {
                "terms": {
                    self.__name__: other
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __ne__(self, other):
        """

        :param other:
        :return:
        """
        """
        {
            "query" : {
                "constant_score" : {
                    "filter" : {
                        "bool": {
                            "must": {"exists": {"field": "<your_field_name_here>"}},
                            "must_not": {"term": {"<your_field_name_here>": ""}}
                        }
                    }
                }
            }
        }
        """
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if other is None:
            """
            {
              "query": {
                "bool": {
                  "must": {
                    "exists": {
                      "field": "myfield"
                    }
                  },
                  "must_not": {
                    "term": {
                      "myfield.keyword": ""
                    }
                  }
                }
              }
            }
            """
            ret = DocumentFields()
            self.__is_bool__ = True

            ret.__es_expr__ = {
                "bool": {
                    "must": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        if isinstance(other, str):
            ret = DocumentFields()
            self.__is_bool__ = True
            # es_object = __make_up_es__(self.__name__, other)
            ret.__es_expr__ = {
                "bool": {
                    "must_not": {
                        "match": {
                            self.__name__: other
                        }
                    }
                }
            }
            return ret
        else:
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}!=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "bool": dict(must_not=[{
                    "term": {
                        self.__name__: other

                    }
                }])
            }
            return ret

    def __matmul__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if other is None:
            ret = DocumentFields()
            self.__is_bool__ = True
            # es_object = __make_up_es__(self.__name__, other)
            ret.__es_expr__ = {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        elif isinstance(other, str):
            ret = DocumentFields()
            self.__is_bool__ = True
            # es_object = __make_up_es__(self.__name__, other)
            ret.__es_expr__ = __make_up_es_syntax__(self.__name__, other, is_match=True)
            return ret
        else:
            ret = DocumentFields()
            ret.__es_expr__ = {
                "term": {
                    self.__name__: other
                }
            }
            return ret

    def __lt__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}<params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "lt": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __le__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}<=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "lte": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __gt__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}>params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "gt": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __ge__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}>=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "gte": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def boost(self, value: float):
        if isinstance(self.__es_expr__, dict):
            self.__es_expr__["boost"] = value
        return self

    def __lshift__(self, other):
        if self.__name__ is None:
            raise Exception("Thous can not update expression")
        if other is not None:
            if type(other) not in [str, int, float, bool, datetime.datetime, dict, list]:
                raise Exception(
                    f"Thous can not update by non primitive type. {type(other)} is not in [str,str,int,float,bool,datetime.datetime,dict,list]")
        ret = DocumentFields(self.__name__)
        ret.__value__ = other
        ret.__has_set_value__ = True
        return ret

    def __repr__(self):
        if isinstance(self.__es_expr__, dict):
            jsonable = to_json_convertable(self.__get_expr__())
            return json.dumps(jsonable, indent=1)
        return self.__name__

    def __get_expr__(self):
        if isinstance(self.__es_expr__, dict):
            if self.__es_expr__.get('script') and isinstance(self.__es_expr__['script'].get('script'), dict) and \
                    self.__es_expr__['script']['script'].get('source'):
                ret = {
                    "bool": {
                        "filter": self.__es_expr__
                    }
                }
                return dict(query=ret)

            ret = self.__es_expr__
            if self.__name__ is not None:
                return {
                    "term": {
                        self.__name__: {
                            "value": self.__es_expr__
                        }
                    }
                }
            if self.__is_bool__:
                ret = {
                    "bool": ret
                }

            return dict(query=ret)
        return self.__name__

    def get_month(self):
        self.__wrap_func__ = "get_day_of_month"

        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getMonthValue()",
                    "lang": "painless"
                }
            }
        }

        return self

    def sub_string(self, start, end):
        self.__wrap_func__ = "sub_string"

        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.substring({start},{end})",
                    "lang": "painless"
                }
            }
        }
        return self

    def starts_with(self, words: str):

        """

        :param words:
        :return:
        """
        """
            {
              "query": {
                "match_phrase_prefix": {
                  "message": {
                    "query": "quick brown f"
                  }
                }
              }
            }
        """
        item = __well_form__(words)
        ret = DocumentFields()
        # ret.__wrap_func__ = "index_of"
        # ret.__is_bool__ = True
        ret.__es_expr__ = {
            "prefix": {
                self.__name__: words
            }

        }

        return ret

    def get_day_of_month(self):
        self.__wrap_func__ = "get_day_of_month"
        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getDayOfMonth()",
                    "lang": "painless"
                }
            }
        }

        return self

    def get_year(self):
        self.__wrap_func__ = "getYear"
        """
         {
              "query": {
                "bool" : {
                  "filter" : {
                   "script" : {
                      "script" : {
                        "source": "doc['timestampstring'].value.getHour() == 5",
                        "lang": "painless"
                      }
                    }
                  }
                }
              }
            }
        """
        k = "['" + self.__name__.replace('.', "']['") + "']"
        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getYear()",
                    "lang": "painless"
                }
            }
        }

        return self


def set_norms(field: DocumentFields, field_type: str, enable: bool) -> DocumentFields:
    return field.set_type(field_type).set_norms(enable)


def create_mapping(fields):
    properties = dict()
    for x in fields:
        if isinstance(x, DocumentFields):
            for k, v in x.get_mapping().items():
                properties[k] = v
    return dict(
        mappings=dict(
            properties=properties
        )
    )


"""
match_phraseBody = {
                "match_phrase": {
                    "content": {
                        "query": str_content,
                        "slop": 3,
                        "analyzer": "standard",
                        "zero_terms_query": "none",
                        "boost": 4.5
                    }
                }
            }
"""


def query_string(fields: typing.List[DocumentFields], query: str):
    return {
        "query_string": {
            "fields": [x.__name__ for x in fields],
            "query": query
        }
    }


def match(field: DocumentFields, content: str, boost=None, slop=None):
    """

    :return:
    """
    ret = DocumentFields()
    __match_content__ = {
        "match": {
            field.__name__: {
                "query": content
                # "boost": 0.5

            }
        }
    }

    if boost is not None:
        __match_content__["match"][field.__name__]["boost"] = boost
    # if slop is not None:
    #     __match_content__["match"][field.__name__]["slop"] = slop
    ret.__es_expr__ = __match_content__
    return ret


def wildcard(field: DocumentFields, content: str):
    """
    :return:
    """
    """
    "query": {
          "bool": {
              "should": [
                {
                  "wildcard": { "Field1": "*" + term + "*" }
                },
                {
                  "wildcard": { "Field2": "*" + term + "*" }
                }
              ],
              "minimum_should_match": 1
          }
      }
    """
    ret = DocumentFields()
    __match_phrase__ = {
        "wildcard": {
            field.__name__: "*" + content + "*"
        }
    }

    ret.__es_expr__ = {
        "match_phrase": __match_phrase__
    }

    # ret.__es_expr__["boost"] = boost
    return ret


def match_phrase(field: DocumentFields, content: str, boost=None, slop=None,
                 analyzer="standard") -> DocumentFields:
    ret = DocumentFields()
    __match_phrase__ = {
        field.__name__: {
            "query": content,
            "analyzer": analyzer,
            "zero_terms_query": "none"
        }
    }
    if boost is not None:
        __match_phrase__[field.__name__]["boost"] = boost
    if slop is not None:
        __match_phrase__[field.__name__]["slop"] = slop
    ret.__es_expr__ = {
        "match_phrase": __match_phrase__
    }

    # ret.__es_expr__["boost"] = boost
    return ret


__cach__index__ = {}


def get_map(cls: type):
    ret = {}
    for k, v in cls.__annotations__.items():
        if v == str:
            ret[k] = "text"
        elif v == bool:
            ret[k] = "boolean"
        elif v == int:
            ret[k] = "long"
        elif v == float:
            ret[k] = "double"
        else:
            ret[k] = {"type": "nested"}
    return dict(
        mappings=dict(
            properties=ret
        )
    )


class SearchResultHits(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    @property
    def total(self) -> int:
        return self.get('total').get('value') or 0

    @property
    def hits(self) -> typing.List[dict]:
        return self.get('hits') or []

    @property
    def max_score(self) -> float:
        return self.get('max_score') or 0


class SearchResult(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    @property
    def hits(self) -> SearchResultHits:
        return SearchResultHits(self.get('hits') or {'value': 0})

    @property
    def took(self) -> int:
        return self.get('took') or 0

    @property
    def items(self):
        for x in self.hits.hits:
            yield ESDocumentObject(x)


def get_docs(client: Elasticsearch, index: str, doc_type: str = "_doc", limit=100, _from=0):
    res = client.search(index=index, doc_type="_doc", body={
        'size': limit,
        'from': _from,
        'query': {
            'match_all': {}
        }
    })
    if res.get("hits"):
        if res["hits"].get("hits"):
            for x in res["hits"]["hits"]:
                yield ESDocumentObject(x)
    return []


def select(client: Elasticsearch, index: str, doc_type: str = "_doc", fields=[], filter=None, sort=None, skip=0,
           limit=1000) -> SearchResult:
    _select_fields_ = []
    if isinstance(fields, dict):
        _select_fields_ = list(fields.keys())

    if isinstance(fields, tuple) or isinstance(fields, list):
        _fields_ = list(fields)
        for x in _fields_:
            if isinstance(x, DocumentFields):
                _select_fields_ += [x.__name__]
            elif isinstance(x, str):
                _select_fields_ += [x]
    """
        {
          "query": {
            "match": {
              "user.id": "kimchy"
            }
          },
          "fields": [
            "user.id",
            "http.response.*",         
            {
              "field": "@timestamp",
              "format": "epoch_millis" 
            }
          ],
          "_source": false
        }
    """
    _filter_ = None
    if isinstance(filter, dict):
        _filter_ = dict(query=filter)

    elif isinstance(filter, DocumentFields):
        _filter_ = filter.__get_expr__()
    _sort = None
    if sort is not None:
        if isinstance(sort, list):
            for x in sort:
                if isinstance(x, DocumentFields):
                    _sort += x.__get_expr__() + ","
                elif isinstance(x, str):
                    _sort += x + ","
    elif isinstance(sort, str):
        _sort = _sort[:-1]

    body = _filter_
    body["fields"] = _select_fields_
    body["from"] = skip * limit
    body["size"] = limit
    if fields is not None:
        body["_source"] = False
    ret = client.search(
        index=index, doc_type=doc_type, body=body, sort=_sort
    )

    return SearchResult(ret)


def get_map_struct(client: Elasticsearch, index: str):
    map = get_mapping(client, index)
    map_index = map[index]['mappings']

    def get_properties(data: dict, prefix=None):
        keys = data['properties'].keys()
        ret = {}
        for k in keys:
            info = data['properties'][k]
            if info.get('properties'):
                s = get_properties(info, k)
                for k, v in s.items():
                    ret[k] = v
            else:
                if prefix:
                    ret[f"{prefix}.{k}"] = data['properties'][k]
                else:
                    ret[f"{k}"] = data['properties'][k]
        return ret

    ret = get_properties(map_index)
    return ret


def search(client: Elasticsearch,
           index: str,
           filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None,
           sort=None,
           doc_type: str = "_doc",
           logic_filter=None) -> SearchResult:
    body = {}
    if isinstance(logic_filter, DocumentFields):
        if isinstance(filter, DocumentFields):
            filter = filter & logic_filter
        else:
            filter = logic_filter
    if isinstance(filter, dict):
        body = dict(query=filter)

    elif isinstance(filter, DocumentFields):
        body = filter.__get_expr__()

    body["from"] = skip * limit
    body["size"] = limit
    if len(excludes) > 0:
        body["_source"] = {
            "excludes": [x.__name__ for x in excludes]
        }
    """
    __highlight = {
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"],
                "fields": {
                    "content": {}
                }
            }
    """
    if highlight:
        """
        "highlight": {
    "require_field_match": "false",
    "fields": {
      "title": {},
      "email": {}
    }
  }
        """
        fields = {}
        for x in highlight:
            fields[x.__name__] = {}
        __highlight = {
            "require_field_match": False,
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
            "fields": fields
        }
        body["highlight"] = __highlight
    _sort = "_score:desc,"
    if sort is not None:
        if isinstance(sort, list):
            for x in sort:
                if isinstance(x, DocumentFields):
                    _sort += x.__get_expr__() + ","
                elif isinstance(x, str):
                    _sort += x + ","

    _sort = _sort[:-1]
    #
    # body["aggs"]= {
    #     "keywords" : {
    #         "significant_text" : {
    #             "field" : "content",
    #             "filter_duplicate_text": True,
    #             "min_doc_count":1
    #             }
    #         }
    # }
    ret = client.search(index=index, doc_type=doc_type, body=body, sort=_sort)
    return SearchResult(ret)


docs = DocumentFields()


def is_index_exist(client: Elasticsearch, index: str):
    return client.indices.exists(index)


class ESDocumentObject(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def get(self, key):

        if isinstance(key, DocumentFields):
            items = key.__name__split('.')
            ret = self
            for x in items:
                ret = dict.get(ret, x)
                if isinstance(ret, dict):
                    ret = ESDocumentObject(ret)
                if ret is None:
                    return None

            return ret
        else:
            return dict.get(self, key)

    def __getattr__(self, item):
        if isinstance(item, str) and item.lower() == "id":
            item = "_id"
        ret_val = self.get(item)
        if isinstance(ret_val, dict):
            return ESDocumentObject(**self.get(item))
        else:
            return ret_val

    def __setattr__(self, key, value):
        if isinstance(key, str) and key.lower() == "id":
            key = "_id"
        if isinstance(value, dict):
            dict.update(self, {key: ESDocumentObject(value)})

        else:
            dict.update(self, {key: value})

    def to_pydantic(self) -> pydantic.BaseModel:
        return pydantic.BaseModel(self)


class ESDocumentObjectInfo:
    """
    {'_index': 'long-test-2011-11',
 '_type': '_doc',
 '_id': '56330233-59f2-48b9-b213-72e75f9f9b28',
 '_version': 4,
 '_seq_no': 3,
 '_primary_term': 1,
 'found': True,
 '_source': {'user_name': 'root',
  'password': 'tes',
  'tags': ['a', 'b', 'c', 'd']}}
    """

    def __init__(self, data):
        """

        :param data:
        """
        self.__data__ = data

    @property
    def __index__(self) -> str:
        return self.__data__["_index"]

    @property
    def id(self) -> str:
        return self.__data__["_id"]

    @property
    def doc_type(self) -> str:
        return self.__data__["_type"]

    @property
    def source(self) -> ESDocumentObject:
        return ESDocumentObject(self.__data__["_source"])


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> ESDocumentObjectInfo:
    try:
        ret = client.get(index=index, id=id, doc_type=doc_type)
        return ESDocumentObjectInfo(data=ret)
    except elasticsearch.exceptions.NotFoundError as e:
        return None


def __convert_exception__(e):
    if isinstance(e, elasticsearch.RequestError):
        if e.status_code == 400 and e.error == "mapper_parsing_exception":
            if len(e.args) > 2:
                erros = e.args[2]
                if isinstance(erros.get('error'), dict):
                    if erros.get('error').get('root_cause') and isinstance(e.args[2].get('error').get('root_cause'),
                                                                           list) and len(
                        e.args[2].get('error').get('root_cause')) > 0:
                        if e.args[2].get('error').get('root_cause')[0].get('reason'):
                            return Exception(e.args[2].get('error').get('root_cause')[0].get('reason'))
    return e


def create_doc(client: Elasticsearch, index: str, body, id: str = None, doc_type: str = "_doc"):
    id = id or str(uuid.uuid4())
    try:
        res = client.create(index=index, doc_type=doc_type, id=id, body=body)
        res["_source"] = body
        return ESDocumentObjectInfo(res)
    except elasticsearch.RequestError as e:
        e1 = __convert_exception__(e)
        raise e1


def update_doc_by_id(client: Elasticsearch, index: str, id: str, data, doc_type: str = "_doc"):
    data_update = data
    if isinstance(data, DocumentFields):
        if data.__has_set_value__ is None:
            raise Exception(
                f"Hey!\n what the fu**king that?\n.thous should call {data.__name__} << {{your value}} ")
        data_update = {
            data.__name__: data.__value__
        }
    if isinstance(data, dict):
        data_update = data
    elif isinstance(data, tuple):
        data_update = {}

        for x in data:
            if isinstance(x, DocumentFields):
                if x.__has_set_value__ is None:
                    raise Exception(
                        f"Hey!\n what the fu**king that?\n.thous should call {x.__name__} << {{your value}} ")
                data_update[x.__name__] = x.__value__
    try:
        ret_update = client.update(
            index=index,
            id=id,
            doc_type=doc_type,
            body=dict(
                doc=data_update
            )

        )
        return data_update
    except elasticsearch.exceptions.NotFoundError as e:
        return None


def create_index(client: Elasticsearch, index: str, body: typing.Union[dict, type]):
    if client.indices.exists(index=index):
        return
    if inspect.isclass(body) and body not in [str, datetime.datetime, int, bool, float, int]:
        ret = client.indices.create(index=index, body=get_map(body))
    else:
        ret = client.indices.create(index=index, body=body)
    return ret


def delete_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):
    try:
        ret = client.delete(index=index, id=id, doc_type=doc_type)
        return ret
    except elasticsearch.exceptions.NotFoundError as e:
        return None


class __expr_type_enum__(Enum):
    CALL = 1
    """
    Function call
    """
    OPER = 2
    """
    Operand
    """
    LOGI = 3


__map__ = {
    "$and": dict(name="__and__", _type=__expr_type_enum__.LOGI),
    "$or": dict(name="__or__", _type=__expr_type_enum__.LOGI),
    "$contains": dict(name="contains", _type=__expr_type_enum__.CALL),
    "$first": dict(name="startswith", _type=__expr_type_enum__.CALL),
    "$last": dict(name="endswith", _type=__expr_type_enum__.CALL),
    "$not": dict(name="__neg__", _type=__expr_type_enum__.OPER),
    "$eq": dict(name="__matmul__", _type=__expr_type_enum__.OPER),
    "$lt": dict(name="__lt__", _type=__expr_type_enum__.OPER),
    "$lte": dict(name="__le__", _type=__expr_type_enum__.OPER),
    "$gt": dict(name="__gt__", _type=__expr_type_enum__.OPER),
    "$gte": dict(name="__ge__", _type=__expr_type_enum__.OPER),
    "$ne": dict(name="__ne__", _type=__expr_type_enum__.OPER)
}


def __all_primitive__(x):
    if type(x) in [str, int, float, bool, datetime.datetime]:
        return True
    elif isinstance(x, list):
        for v in x:
            if not __all_primitive__(v):
                return False
        return True


def nested(prefix: str, filter):
    ret = {}
    if isinstance(filter, dict):
        for k, v in filter.items():
            _k = k
            _v = v
            if k[:1] != "$":
                _k = f"{prefix}.{_k}"
            if isinstance(v, dict):
                _v = nested(prefix, _v)
            elif isinstance(v, list):
                _v = [nested(prefix, x) for x in _v]
            ret[_k.lower()] = _v
            return ret
    return filter


def __build_search__(fields, content,suggest_handler=None):
    """

    :param fields:
    :param content:
    :return:
    """
    """
    "query": {
    "multi_match" : {
      "query" : "this is a test",
      "fields" : [ "subject^3", "message" ] 
    }
  }
    """
    ret = DocumentFields()
    match_fields = []
    if callable(suggest_handler):
        content= content+" "+suggest_handler(content)
    else:
        return
    for x in fields:
        match_fields+=[x,f"{x}_seg^2",f"{x}_bm25_seg^1"]
    ret.__es_expr__ = {
        "multi_match": {
            "fields": fields,
            "query": content
        }
    }
    ret.__highlight_fields__ = fields
    return ret


def __apply_function__(function_name, field_name, owner_caller=None, args=None,suggest_handler=None):
    if function_name == "$$day":
        ret = DocumentFields(field_name)
        return ret.get_day_of_month()
    elif function_name == "$$month":
        ret = DocumentFields(field_name)
        return ret.get_month()
    elif function_name == "$$year":
        ret = DocumentFields(field_name)
        return ret.get_year()
    elif function_name == "$$first":
        ret = DocumentFields(field_name)
        return ret.startswith
    elif function_name == "$$last":
        ret = DocumentFields(field_name)
        return ret.endswith
    elif function_name == "$$contains":
        ret = DocumentFields(field_name)
        return ret.__contains__
    elif function_name == "$$search":
        fields = field_name['$fields']
        content = field_name['$value']
        return __build_search__(fields, content,suggest_handler)
    else:
        raise NotImplemented("error")


def create_filter_from_dict(expr: dict, owner_caller=None, op=None,suggest_handler=None):
    global __map__

    if isinstance(expr, dict):
        funcs = [x for x in expr.keys() if x.startswith('$$')]
        if op is not None and len(funcs) > 0 and expr["$value"] is not None:
            func_name = funcs[0]
            fx = __apply_function__(func_name, expr[func_name])
            if callable(fx) and not isinstance(fx, DocumentFields):
                fx = fx(expr["$value"])
                if func_name in ["$$first", "$$last", "$$contains"]:
                    return fx
            _op = op["name"]
            if _op == "__matmul__":
                _op = "__eq__"
            if hasattr(fx, _op):
                return getattr(fx, _op)(expr["$value"])

        for k, v in expr.items():
            if k[0:2] == "$$":
                ret = __apply_function__(k, v, owner_caller,suggest_handler=suggest_handler)
                if callable(ret) and not isinstance(ret, DocumentFields):
                    ret = ret(expr["$value"])
                    return ret
                elif op and op.get("name"):
                    _op = op.get("name")
                    if _op == "__matmul__":
                        _op = "__eq__"

                    caller = getattr(ret, _op)
                    ret = caller(expr["$value"])
                    return ret
                else:
                    # caller = getattr(ret, "__eq__")
                    # ret = caller(expr["$value"])
                    return ret
            elif k != "$value" and k[0:1] == "$":
                if not __map__.get(k):
                    raise Exception(f"{k} is Unknown")
                if __map__.get(k):
                    map_name = __map__[k]["name"]
                    map_type: __expr_type_enum__ = __map__[k]["_type"]

                    if isinstance(v, list):
                        if __all_primitive__(v) and map_type == __expr_type_enum__.CALL:
                            ret = getattr(owner_caller, map_name)(*v)
                            return ret
                        else:
                            ret = create_filter_from_dict(v[0],suggest_handler=suggest_handler)
                            if len(v) > 1:
                                for i in range(1, len(v)):
                                    next = create_filter_from_dict(v[i],suggest_handler=suggest_handler)
                                    if map_type == __expr_type_enum__.LOGI:
                                        ret = getattr(ret, map_name)(next)
                                    else:
                                        # if owner_caller is not None:
                                        #     ret = getattr(owner_caller, method_name)(next)
                                        # else:
                                        raise NotImplemented
                            return ret
                    elif isinstance(v, dict):
                        ret = create_filter_from_dict(v, op=__map__[k],suggest_handler=suggest_handler)
                        return ret
                    elif isinstance(v, str):
                        ret = getattr(owner_caller, map_name)(*v)
                        return ret


                    elif isinstance(v, str) and k == "$contains":
                        ret = getattr(owner_caller, "__contains__")(v)
                        return ret
                    else:
                        if map_type == __expr_type_enum__.OPER:
                            if isinstance(v, dict):
                                ret = create_filter_from_dict(v,suggest_handler=suggest_handler)
                                ret = getattr(ret, map_name)()
                                return ret
                            elif isinstance(owner_caller, DocumentFields):
                                handler = getattr(owner_caller, map_name)
                                ret = handler(v)
                                return ret
                            else:
                                raise NotImplemented
                        else:
                            raise NotImplemented

            else:
                if isinstance(v, dict):
                    ret = DocumentFields(k)
                    ret = create_filter_from_dict(v, ret,suggest_handler=suggest_handler)
                    return ret
                elif k == "$value" and op is not None and len([x for x in expr.keys() if x.startswith('$$')]) > 0:

                    ret = __apply_function__(k, v, owner_caller)
                    if callable(ret) and not isinstance(ret, DocumentFields):
                        ret = ret(expr["$value"])
                        return ret
                    elif op and op.get("name"):
                        _op = op.get("name")
                        if _op == "__matmul__":
                            _op = "__eq__"

                        caller = getattr(ret, _op)
                        ret = caller(expr["$value"])
                        return ret
                    else:
                        # caller = getattr(ret, "__eq__")
                        # ret = caller(expr["$value"])
                        return ret
                else:
                    ret = DocumentFields(k)
                    if op is not None:
                        _op = op["name"]
                        if _op == "__matmul__" and not isinstance(v, str):
                            _op = "__eq__"
                        if hasattr(ret, _op):
                            return getattr(ret, _op)(v)

                    ret = ret == v
                    return ret

    elif op is not None and isinstance(expr, dict) and expr["$value"]:
        lf = DocumentFields(list(expr.keys())[0])
        vf = expr[list(expr.keys())[0]]
        op_name = op["name"]
        if op_name == "__matmul__":
            op_name = "__eq__"
        return getattr(lf, op_name)(vf)

    else:
        raise NotImplemented


def is_exist(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> bool:
    return client.exists(index=index, id=id, doc_type=doc_type)


def count(client: Elasticsearch, index: str):
    ret = client.count(index=index)
    return ret.get('count', 0)


def clone_index(client: Elasticsearch, from_index, to_index, segment_size=100):
    total_docs = count(client=client, index=from_index)

    i = 0
    while i < total_docs:
        ret_docs = get_docs(client, from_index, limit=segment_size, _from=i)
        for x in ret_docs:
            i += 1
            if not is_exist(client=client, index=to_index, id=x._id, doc_type=x._type):
                create_doc(
                    client=client,
                    index=to_index,
                    body=x._source,
                    id=x._id,
                    doc_type=x._type

                )

        print(f"{i}/{total_docs}")
    print("xong")


def put_mapping(client: Elasticsearch, index, body):
    return client.indices.put_mapping(
        index=index,
        body=body.get('mappings', body),
        ignore=400
    )


def get_mapping(client: Elasticsearch, index):
    try:
        return client.indices.get_mapping(
            index=index,
            allow_no_indices=True
        )
    except elasticsearch.exceptions.NotFoundError as e:
        return None


def similarity_settings(client: Elasticsearch, index: str, field_name: str, algorithm_type: str, b_value, k1_value):
    try:
        settings = client.indices.get_settings(index=index)
        settings_index = settings[index]
        if settings_index.get('settings') and settings_index['settings'].get('index') and settings_index['settings'][
            'index'].get('similarity') and settings_index['settings']['index']['similarity'].get('bm25_similarity'):
            client.indices.put_mapping(
                index=index,
                body=
                {
                    "properties": {
                        field_name: {
                            "type": "text",
                            "similarity": "bm25_similarity",
                            "fielddata": True
                        },
                        f"{field_name}_lower": {
                            "type": "text",
                            "similarity": "bm25_similarity",
                            "fielddata": True
                        }

                    }
                }
            )


    except elasticsearch.exceptions.NotFoundError as e:
        client.indices.create(index=index)

    # settings[index]['settings']['index']['similarity']['bm25_similarity']
    client.indices.close(index=index)
    settings = {
        "index": {
            "similarity": {
                "bm25_similarity": {
                    "type": algorithm_type,
                    "b": b_value,  # b gần về 0 sẽ bỏ qua độ dài của câu
                    "k1": k1_value
                }
            }
        }
    }
    client.indices.put_settings(index=index, body=settings)
    client.indices.put_mapping(
        index=index,
        body=
        {
            "properties": {
                field_name: {
                    "type": "text",
                    "similarity": "bm25_similarity",
                    "fielddata": True
                }

            }
        }
    )
    client.indices.open(index=index)


import bson


def to_json_convertable(data):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = to_json_convertable(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [to_json_convertable(x)]
        return ret
    elif isinstance(data, bson.ObjectId):
        return data.__str__()
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    else:
        return data


def es_func_get_day(field):
    """

    :return:
    """

    if isinstance(field, DocumentFields):
        """
       "script": {
            "script": "doc.readingTimestamp.date.getHourOfDay() >= 9 && doc.readingTimestamp.date.getHourOfDay() <= 18"
          } 
        """
        ret = dict(
            script={
                f"doc.{DocumentFields.__name__}.date.dayOfMonth"
            }
        )


def text_lower(filter):
    if isinstance(filter, dict):
        ret = {}
        for k, v in filter.items():
            if isinstance(v, str):
                ret[k] = v.lower()
            elif isinstance(v, dict):
                ret[k] = text_lower(v)
            elif isinstance(v, list):
                ret[k] = []
                for x in v:
                    ret[k] += [text_lower(x)]
            else:
                ret[k] = v
        return ret
    elif isinstance(filter, str):
        return filter.lower()
    else:
        return filter


def create_dict_from_key_path_value(field_path: str, value):
    if not "." in field_path:
        return {
            field_path: value
        }
    else:

        index = field_path.index(".")
        a = field_path[0:index]
        b = field_path[index + 1:]
        ret = create_dict_from_key_path_value(b, value)
        return {
            a: ret
        }


def update_data_fields(client: Elasticsearch, index: str, id: str, field_path=None, field_value=None, keys_values=None,
                       doc_type="_doc"):
    try:

        keys_values = keys_values or {
            field_path: field_value
        }
        data = {}
        has_data = False
        for k, v in keys_values.items():
            if k != "_id":
                has_data = True
                d = create_dict_from_key_path_value(k, v)
                data = {**data, **d}
        if has_data:
            client.update(
                index=index,
                id=id,
                body={
                    "doc": data

                },
                doc_type=doc_type
            )
        return True

    except elasticsearch.exceptions.NotFoundError as e:
        return False


def flattern_dict(data, prefix=None):
    if not isinstance(data, dict):
        raise Exception("data must be dict")
    ret = {}
    for k, v in data.items():
        if isinstance(v, dict):
            if prefix:
                s = flattern_dict(v, f"{prefix}.{k}")
            else:
                s = flattern_dict(v, k)
            ret = {**ret, **s}
        else:
            if prefix:
                ret = {**ret, **{f"{prefix}.{k}": v}}
            else:
                ret = {**ret, **{k: v}}
    return ret


def update_by_conditional(
        client: Elasticsearch,
        index: str,
        data_update,
        conditional,
        doc_type="_doc"
):
    _data_update = to_json_convertable(data_update)
    body = {}

    if isinstance(conditional, DocumentFields):
        body = conditional.__get_expr__()
    if isinstance(conditional, dict):
        body = dict(query=conditional)
    inline_script = ""
    h = flattern_dict(_data_update)
    """
    {
      "script": {
        "inline": "ctx._source.student.hobbies.add(params.hobby); ctx._source.student.phone.add(params.phone)",
        "lang": "painless",
        "params": {
          "hobby": "cricket",
          "phone" : "122-33-4567"
        }
      }
    }
    """
    params = {
        "___obj___": dict()
    }
    for k, v in h.items():
        txt = ""
        p_k = k.replace('.', '_')
        items = k.split('.')
        if items.__len__() > 1:
            k1 = ""
            for x in items[:-1]:
                k1 += "." + x
                txt += f"if(ctx._source{k1}==null)\r\n {{\r\nctx._source{k1}=[:];\r\n}}\r\n"

        txt += f"ctx._source.{k}=params.{p_k};\r\n"

        inline_script += txt
        # inline_script += f"ctx._source.{k}=params.{p_k};"
        params[p_k] = v

    body["script"] = {
        "inline": inline_script,
        "lang": "painless",
        "params": params
    }

    ret = client.update_by_query(
        index=index,
        doc_type=doc_type,
        body=body

    )
    return ret.get("updated") or 0


def delete_by_conditional(client: Elasticsearch, index: str, conditional, doc_type="_doc"):
    body = {}

    if isinstance(conditional, DocumentFields):
        body = conditional.__get_expr__()
    if isinstance(conditional, dict):
        body = dict(query=conditional)
    ret = client.delete_by_query(
        index=index,
        body=body, doc_type=doc_type

    )

    return ret.get("deleted") or 0


import uuid


def __is_date__(str_date):
    try:
        datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        return True
    except Exception as e:
        return False
    str_date_time = str_date.split('+')[0]
    try:
        t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
        tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
        ret = t + datetime.timedelta(tz.hour)
        return True
    except Exception as e:
        return False


def __is_valid_uuid__(value):
    try:
        uuid.UUID(value)

        return True
    except ValueError:
        return False


def is_content_text(text):
    if isinstance(text, str) and not __is_date__(text) and not __is_valid_uuid__(text):
        return True
    return False


def convert_to_vn_predict_seg(data, handler, segment_handler,clear_accent_mark_handler):
    def add_more_content(data, handler, segment_handler,clear_accent_mark_handler):
        if isinstance(data, dict):
            ret = {}
            for k, v in data.items():
                x, y, z = add_more_content(v, handler, segment_handler,clear_accent_mark_handler)
                if y and y != x:
                    ret[f"{k}_vn_predict"] = y
                if z:
                    ret[f"{k}_bm25_seg"] = z
                ret[k] = x
            return ret, None, None
        elif isinstance(data, str):
            if not " " in data:
                return data, None, None
            if __is_valid_uuid__(data):
                return data, None, None
            elif __is_date__(data):
                return data, None, None
            else:
                vn_none_accent_content = clear_accent_mark_handler(data.lower())
                predict_content = handler(data)

                return data, predict_content, segment_handler(predict_content) + "/n" + segment_handler(data)+"/n"+ vn_none_accent_content
        elif isinstance(data, list):
            n_list = []
            for item in data:
                x, y, z = add_more_content(item, handler, segment_handler,clear_accent_mark_handler)
                if y and y != x:
                    n_list += [y]
                if z:
                    n_list += [z]
                n_list += [x]
            return n_list, None, None
        else:
            return data, None, None

    ret, _, _ = add_more_content(data, handler, segment_handler,clear_accent_mark_handler)
    return ret
