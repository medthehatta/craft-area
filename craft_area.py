import random
from collections import Counter
import operator
from functools import partial

from formal_vector import FormalVector

from chance import definitely
from chance import uniform
from chance import weighted
from chance import percent_left


class Damage:

    none = FormalVector.zero()
    basic = FormalVector.named("basic")
    explosive = FormalVector.named("explosive")


def hit(pct, type_):
    return percent_left(pct, type_, Damage.none)


hit10 = partial(hit, 10)
hit20 = partial(hit, 20)
hit25 = partial(hit, 25)
hit30 = partial(hit, 30)
hit33 = partial(hit, 33)
hit40 = partial(hit, 40)
hit50 = partial(hit, 50)
hit60 = partial(hit, 60)
hit70 = partial(hit, 70)
hit75 = partial(hit, 75)
hit80 = partial(hit, 80)
hit90 = partial(hit, 90)
hit95 = partial(hit, 95)
hit99 = partial(hit, 99)
hit100 = definitely


def unit_type(
    name,
    initiative,
    attacks=definitely(Damage.none),
    defends=definitely(Damage.none),
    one_time=False,
):
    return {
        "name": name,
        "initiative": initiative,
        "attacks": attacks,
        "defends": defends,
        "one_time": one_time,
    }


basic_unit_type = unit_type(
    "basic",
    initiative=50,
    attacks=hit60(100*Damage.basic),
    defends=hit95(100*Damage.basic),
    one_time=False,
)


exploding_unit_type = unit_type(
    "exploding",
    initiative=20,
    attacks=hit80(500*Damage.explosive),
    defends=definitely(Damage.none),
    one_time=True,
)


all_types = [basic_unit_type, exploding_unit_type]


def random_fleet(num_min, num_max=None, has_types=None, rng=None):
    has_types = has_types or all_types
    num_max = num_max or num_min
    rng = rng or random.Random()
    if num_min < len(has_types):
        raise ValueError(
            "num_min cannot be smaller than the length of has_types"
        )

    num = (
        num_min if num_min == num_max else
        rng.randint(num_min, num_max)
    )

    type_names = list(set(t["name"] for t in has_types))

    # First we will take one of each type, so no need to actually select those
    # algorithmically
    num_remaining = num - len(has_types)

    # Now randomly select num_remaining from our options
    selections = dict(
        Counter(type_names + rng.choices(type_names, k=num_remaining))
    )

    return {"size": num, "types": type_names, "fleet": selections}