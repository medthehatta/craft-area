import random
from collections import Counter
import operator
from functools import partial

from formal_vector import FormalVector

from chance import definitely
from chance import uniform
from chance import weighted
from chance import percent_left


class DamageVector(FormalVector):

    _ZERO = "Damage.zero"


class Damage:

    none = DamageVector.zero()
    basic = DamageVector.named("Damage.basic")
    explosive = DamageVector.named("Damage.explosive")


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


_battle_entities = {}


def battle_entity(
    name,
    initiative,
    attacks=definitely(Damage.none),
    defends=definitely(Damage.none),
    one_time=False,
    can_initiate=True,
):
    entity = {
        "name": name,
        "initiative": initiative,
        "attacks": attacks,
        "defends": defends,
        "one_time": one_time,
        "can_initiate": can_initiate,
    }
    _battle_entities[name] = entity
    return entity


def select_at_least_one_of_each(items, num_min, num_max=None, rng=None):
    num_max = num_max or num_min
    rng = rng or random.Random()
    if num_min < len(items):
        raise ValueError(
            "num_min cannot be smaller than the number of items"
        )

    num = (
        num_min if num_min == num_max else
        rng.randint(num_min, num_max)
    )

    # First we will take one of each item, so no need to actually select those
    # algorithmically
    num_remaining = num - len(items)

    # Now randomly select num_remaining from our options
    selections = Counter(items + rng.choices(items, k=num_remaining))

    return selections


def extract_pct(pct, items, rng=None):
    max_num_float = pct/100 * len(items)
    # If we have a moderately large fraction of 1, just clamp the max to 1.
    # If we have a very small fraction, it will be truncated to 0.
    if 0.1 < max_num_float < 1:
        max_num = 1
    else:
        max_num = int(max_num_float)

    num = rng.randint(0, max_num)
    return rng.sample(items, num)


def random_fleet(num_min, num_max=None, has_types=None, rng=None):
    has_types = has_types or [
        entity for entity in _battle_entities.values()
        if entity["can_initiate"]
    ]
    possibilities = [t["name"] for t in has_types]
    return select_at_least_one_of_each(
        possibilities,
        num_min=num_min,
        num_max=num_max,
        rng=rng,
    )


def produce_damage(fleet_entries, rng=None):
    rng = rng or random.Random()
    attacks = {
        entity_name: [
            _battle_entities[entity_name]["attacks"].resolve(rng)
            for _ in range(num)
        ]
        for (entity_name, num) in fleet_entries.items()
    }
    return {
        "damage": DamageVector.sum(
            DamageVector.sum(a) for a in attacks.values()
        ),
        "attacks": attacks,
    }


def produce_defense(fleet_entries, rng=None):
    rng = rng or random.Random()
    defenses = {
        entity_name: [
            _battle_entities[entity_name]["defends"].resolve(rng)
            for _ in range(num)
        ]
        for (entity_name, num) in fleet_entries.items()
    }
    return {
        "damage": DamageVector.sum(
            DamageVector.sum(a) for a in defenses.values()
        ),
        "defenses": defenses,
    }


basic_unit_type = battle_entity(
    "basic_unit",
    initiative=50,
    attacks=hit60(100*Damage.basic),
    defends=hit95(100*Damage.basic),
)


exploding_unit_type = battle_entity(
    "exploding_unit",
    initiative=20,
    attacks=hit80(500*Damage.explosive),
    one_time=True,
)


module_structure = battle_entity(
    "module_structure",
    initiative=99,
    defends=hit99(1000*Damage.basic),
    can_initiate=False,
)


