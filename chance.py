import operator
import random


def _resolve(obj, rng):
    if isinstance(obj, BaseChance):
        return obj.resolve(rng)
    else:
        return obj


def _format_pct(fraction):
    pct = 100 * fraction
    if pct >= 100:
        return f"{pct:.3n}%"
    elif pct < 10:
        return f"{pct:.1n}%"
    else:
        return f"{pct:.2n}%"


def _weighted_repr(outcomes, weights=None):
    if weights is None:
        weights = [1]*len(outcomes)
    total = sum(weights)
    display = " | ".join(
            f"{it} ({_format_pct(w/total)}))"
            for (it, w) in zip(outcomes, weights)
    )
    return f"<Chances: {display}>"


#
# Foundations
#


class BaseChance:

    def resolve(self, rng=None):
        raise NotImplementedError("Override me")

    def __neg__(self):
        return VariadicChance(operator.neg, self)

    def __not__(self):
        return VariadicChance(operator.not_, self)

    def __add__(self, other):
        return VariadicChance(operator.add, self, other)

    def __sub__(self, other):
        return VariadicChance(operator.sub, self, other)

    def __mul__(self, other):
        return VariadicChance(operator.mul, self, other)

    def __truediv__(self, other):
        return VariadicChance(operator.truediv, self, other)

    def __floordiv__(self, other):
        return VariadicChance(operator.floordiv, self, other)


class VariadicChance(BaseChance):

    def __init__(self, func, *args, rng=None):
        self.func = func
        self.args = args
        self.rng = rng

    def __repr__(self):
        funcname = self.func.__name__
        return f"{funcname}(*{self.args})"

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        return self.func(*[_resolve(a, rng) for a in self.args])


class SeqChance(BaseChance):

    def __init__(self, func, seq, rng=None):
        self.func = func
        self.seq = seq
        self.rng = rng

    def __repr__(self):
        funcname = self.func.__name__
        return f"{funcname}({self.seq})"

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        return self.func([a.resolve(rng) for a in self.seq])


class DictChance(BaseChance):

    def __init__(self, func, dic, rng=None):
        self.func = func
        self.dic = dic
        self.rng = rng

    def __repr__(self):
        funcname = self.func.__name__
        return f"{funcname}({self.dic})"

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        return self.func({k: v.resolve(rng) for (k, v) in self.dic.items()})


#
# User-facing
#


class Definitely(BaseChance):

    def __init__(self, value, rng=None):
        self.value = value

    def __repr__(self):
        return _weighted_repr([self.value])

    def resolve(self, rng=None):
        return _resolve(self.value, rng)


class EquallyLikely(BaseChance):

    def __init__(self, *items, rng=None):
        self.items = items
        self.rng = rng

    def __repr__(self):
        return _weighted_repr(self.items)

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        outcome = rng.choice(self.items)
        return _resolve(outcome, rng)


class WeightedChances(BaseChance):

    def __init__(self, outcomes, weights, rng=None):
        self.outcomes = outcomes
        self.weights = weights
        self.rng = rng

    def __repr__(self):
        return _weighted_repr(self.outcomes, self.weights)

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        outcome = rng.choices(self.outcomes, weights=self.weights)
        return _resolve(outcome, rng)


class PercentChanceToOccur(BaseChance):

    def __init__(self, percent_chance, yes, no, rng=None):
        self.percent_chance = percent_chance
        self.yes = yes
        self.no = no
        self.rng = rng

    def __repr__(self):
        return _weighted_repr([self.yes, self.no])

    def resolve(self, rng=None):
        rng = rng or self.rng or random.Random()
        chance = percent_chance/100
        if rng.random() <= chance:
            outcome = self.yes
        else:
            outcome = self.no

        return _resolve(outcome, rng)


#
# Helper aliases
#


definitely = Definitely
uniform = EquallyLikely
weighted = WeightedChances
percent_left = PercentChanceToOccur
