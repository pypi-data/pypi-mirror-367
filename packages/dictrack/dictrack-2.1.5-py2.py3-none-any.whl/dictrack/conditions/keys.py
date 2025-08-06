# -*- coding: UTF-8 -*-

import operator

import six
from dictor import dictor

from dictrack.conditions.base import BaseCondition
from dictrack.utils.utils import str_to_operator, typecheck, valid_obj, valid_type


class KeyExists(BaseCondition):
    def __init__(self, key, *args, **kwargs):
        self._key = key

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return "<KeyExists (key={})>".format(self.key)

    def __getstate__(self):
        return {"cls": self.__class__, "key": self.key}

    def __setstate__(self, state):
        self._key = state["key"]

    @property
    def key(self):
        return self._key

    @typecheck()
    def check(self, data, *args, **kwargs):
        result = dictor(data, self.key, default=BaseCondition.DEFAULT)

        return result != BaseCondition.DEFAULT


class KeyNotExists(KeyExists):
    def __repr__(self):
        base_repr = super(KeyNotExists, self).__repr__()
        return base_repr.replace("KeyExists", self.__class__.__name__)

    @typecheck()
    def check(self, data, *args, **kwargs):
        return not super(KeyNotExists, self).check(data, *args, **kwargs)


class KeyValueComparison(KeyExists):
    def __init__(self, key, value, op=operator.eq, *args, **kwargs):
        super(KeyValueComparison, self).__init__(key, *args, **kwargs)

        valid_obj(
            op,
            (
                operator.eq,
                operator.ne,
                operator.lt,
                operator.le,
                operator.gt,
                operator.ge,
            ),
        )
        self._op = op
        self._value = value

    def __eq__(self, other):
        return (
            self.key == other.key and self.value == other.value and self.op == other.op
        )

    def __hash__(self):
        key_hash = hash(self.key)
        value_hash = hash(self.value)
        op_hash = hash(self.op)

        return hash(str(key_hash) + str(value_hash) + str(op_hash))

    def __repr__(self):
        return "<KeyValueComparison (key={} operator={} value={})>".format(
            self.key, self.op.__name__, self.value
        )

    def __getstate__(self):
        state = super(KeyValueComparison, self).__getstate__()
        state["op"] = self._op.__str__()
        state["value"] = self.value

        return state

    def __setstate__(self, state):
        super(KeyValueComparison, self).__setstate__(state)

        self._op = str_to_operator(state["op"])
        self._value = state["value"]

    @property
    def op(self):
        return self._op

    @property
    def value(self):
        return self._value

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not super(KeyValueComparison, self).check(data, *args, **kwargs):
            return False

        result = dictor(data, self.key)

        return self.op(result, self.value)


class KeyValueEQ(KeyValueComparison):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueEQ, self).__init__(key, value, operator.eq, *args, **kwargs)

    def __repr__(self):
        base_repr = super(KeyValueEQ, self).__repr__()
        return base_repr.replace("KeyValueComparison", self.__class__.__name__)


class KeyValueNE(KeyValueEQ):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueNE, self).__init__(key, value, *args, **kwargs)
        self._op = operator.ne


class KeyValueLT(KeyValueEQ):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueLT, self).__init__(key, value, *args, **kwargs)
        self._op = operator.lt


class KeyValueLE(KeyValueEQ):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueLE, self).__init__(key, value, *args, **kwargs)
        self._op = operator.le


class KeyValueGT(KeyValueEQ):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueGT, self).__init__(key, value, *args, **kwargs)
        self._op = operator.gt


class KeyValueGE(KeyValueEQ):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueGE, self).__init__(key, value, *args, **kwargs)
        self._op = operator.ge


class KeyValueContained(KeyExists):
    def __init__(self, key, value, case_sensitive=True, *args, **kwargs):
        super(KeyValueContained, self).__init__(key, *args, **kwargs)

        valid_type(value, six.string_types)
        self._value = value
        self._case_sensitive = case_sensitive

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __hash__(self):
        key_hash = hash(self.key)
        value_hash = hash(self.value)

        return hash(str(key_hash) + str(value_hash))

    def __repr__(self):
        return "<KeyValueContained (key={} value={} case_sensitive={})>".format(
            self.key, self.value, self._case_sensitive
        )

    def __getstate__(self):
        state = super(KeyValueContained, self).__getstate__()
        state["value"] = self.value
        state["case_sensitive"] = self._case_sensitive

        return state

    def __setstate__(self, state):
        super(KeyValueContained, self).__setstate__(state)

        self._value = state["value"]
        self._case_sensitive = state["case_sensitive"]

    @property
    def value(self):
        return self._value

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not super(KeyValueContained, self).check(data, *args, **kwargs):
            return False

        result = dictor(data, self.key)
        if not self._case_sensitive:
            return self.value.lower() in result.lower()

        return self.value in result


class KeyValueNotContained(KeyValueContained):
    def __repr__(self):
        base_repr = super(KeyValueNotContained, self).__repr__()
        return base_repr.replace("KeyValueContained", self.__class__.__name__)

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not KeyExists.check(self, data, *args, **kwargs):
            return False

        return not KeyValueContained.check(self, data, *args, **kwargs)


class KeyValueInList(KeyExists):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueInList, self).__init__(key, *args, **kwargs)

        valid_type(value, (list, tuple))
        self._value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __hash__(self):
        key_hash = hash(self.key)
        value_hash = hash(tuple(self.value))

        return hash(str(key_hash) + str(value_hash))

    def __repr__(self):
        return "<KeyValueInList (key={} value={})>".format(self.key, self.value)

    def __getstate__(self):
        state = super(KeyValueInList, self).__getstate__()
        state["value"] = self.value

        return state

    def __setstate__(self, state):
        super(KeyValueInList, self).__setstate__(state)
        self._value = state["value"]

    @property
    def value(self):
        return self._value

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not super(KeyValueInList, self).check(data, *args, **kwargs):
            return False

        result = dictor(data, self.key)

        return result in self.value


class KeyValueNotInList(KeyValueInList):
    def __repr__(self):
        base_repr = super(KeyValueNotInList, self).__repr__()
        return base_repr.replace("KeyValueInList", self.__class__.__name__)

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not KeyExists.check(self, data, *args, **kwargs):
            return False

        return not KeyValueInList.check(self, data, *args, **kwargs)


class KeyValueListHasItem(KeyExists):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueListHasItem, self).__init__(key, *args, **kwargs)

        valid_type(value, (int, str))
        self._value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __hash__(self):
        key_hash = hash(self.key)
        value_hash = hash(self.value)

        return hash(str(key_hash) + str(value_hash))

    def __repr__(self):
        return "<KeyValueListHasItem (key={} value={})>".format(self.key, self.value)

    def __getstate__(self):
        state = super(KeyValueListHasItem, self).__getstate__()
        state["value"] = self.value

        return state

    def __setstate__(self, state):
        super(KeyValueListHasItem, self).__setstate__(state)
        self._value = state["value"]

    @property
    def value(self):
        return self._value

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not super(KeyValueListHasItem, self).check(data, *args, **kwargs):
            return False

        result = dictor(data, self.key)

        return self.value in result


class KeyValueListNotHasItem(KeyValueListHasItem):
    def __repr__(self):
        base_repr = super(KeyValueListNotHasItem, self).__repr__()
        return base_repr.replace("KeyValueListHasItem", self.__class__.__name__)

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not KeyExists.check(self, data, *args, **kwargs):
            return False

        return not KeyValueListHasItem.check(self, data, *args, **kwargs)


class KeyValueListIntersectList(KeyExists):
    def __init__(self, key, value, *args, **kwargs):
        super(KeyValueListIntersectList, self).__init__(key, *args, **kwargs)

        valid_type(value, (list, tuple))
        self._value = value

    def __eq__(self, other):
        return self.key == other.key and self.value == other.value

    def __hash__(self):
        key_hash = hash(self.key)
        value_hash = hash(tuple(self.value))

        return hash(str(key_hash) + str(value_hash))

    def __repr__(self):
        return "<KeyValueListIntersectList (key={} value={})>".format(
            self.key, self.value
        )

    def __getstate__(self):
        state = super(KeyValueListIntersectList, self).__getstate__()
        state["value"] = self.value

        return state

    def __setstate__(self, state):
        super(KeyValueListIntersectList, self).__setstate__(state)
        self._value = state["value"]

    @property
    def value(self):
        return self._value

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not super(KeyValueListIntersectList, self).check(data, *args, **kwargs):
            return False

        result = dictor(data, self.key)

        return bool(set(self.value) & set(result))


class KeyValueListNotIntersectList(KeyValueListIntersectList):
    def __repr__(self):
        base_repr = super(KeyValueListNotIntersectList, self).__repr__()
        return base_repr.replace("KeyValueListIntersectList", self.__class__.__name__)

    @typecheck()
    def check(self, data, *args, **kwargs):
        if not KeyExists.check(self, data, *args, **kwargs):
            return False

        return not KeyValueListIntersectList.check(self, data, *args, **kwargs)
