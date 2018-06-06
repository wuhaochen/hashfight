#/usr/bin/env python2

import hashlib
import random
import sys
from collections import Counter


class HashShip(object):

    p = property_mapping = dict()
    p['EM_DAMAGE'] = '0'
    p['EM_RESIST'] = '1'
    p['HE_DAMAGE'] = '2'
    p['HE_RESIST'] = '3'
    p['KI_DAMAGE'] = '4'
    p['KI_RESIST'] = '5'
    p['EXP_DAMAGE'] = '6'
    p['EXP_RESIST'] = '7'
    p['PSY_DAMAGE'] = '8'
    p['PSY_RESIST'] = '9'
    p['HP'] = 'a'
    p['SHIELD'] = 'b'
    p['EVASE'] = 'c'
    p['FIRE_RATE'] = 'd'
    p['HIT_RATE'] = 'e'
    p['CRITICAL'] = 'f'

    def __init__(self, design):
        self._design = design
        self.meta_property = Counter(
            hashlib.sha512(self._design).hexdigest())
        self.remaining_hp = self.hp

    def get_meta(self, category):
        index = self.property_mapping[category]
        return self.meta_property[index]

    def get_resist(self, category):
        meta = self.get_meta(category + '_RESIST')
        return min(0.04 * meta, 1)

    def get_damage(self, category):
        meta = self.get_meta(category + '_DAMAGE')
        return max(meta - 5, 0) ** 2

    @property
    def hp(self):
        meta = self.get_meta('HP')
        return 4000 * meta + 5000

    @property
    def shield(self):
        meta = self.get_meta('SHIELD')
        return meta + 1

    @property
    def evasive_rate(self):
        meta = self.get_meta('EVASE')
        return 0.05 * meta

    @property
    def fire_rate(self):
        meta = self.get_meta('FIRE_RATE')
        return 1000 / (meta + 1)

    @property
    def hit_rate(self):
        meta = self.get_meta('HIT_RATE')
        return 0.1 * meta

    @property
    def critical_rate(self):
        meta = self.get_meta('CRITICAL')
        return 0.04 * meta


def hit(attacker, defender):
    true_hit_rate = min(0.5 + attacker.hit_rate - defender.evasive_rate, 1)
    if random.random() > true_hit_rate:
        return (0, 'The attack missed.')

    raw_damage = 0
    damage_modifier = random.uniform(0.9, 1.1)
    damage_types = ('EM', 'HE', 'KI', 'EXP', 'PSY')
    for damage_type in damage_types:
        attack = attacker.get_damage(damage_type)
        resist = defender.get_resist(damage_type)
        raw_damage += attack * (1 - resist)

    critical = ''
    critical_rate = attacker.critical_rate
    if random.random() <= critical_rate:
        if random.random() <= 0.2:
            damage_modifier *= 3
            critical = 'super critical'
        else:
            damage_modifier *= 2
            critical = 'critical'

    final_damage = max(raw_damage * damage_modifier
                       - defender.shield, 0)
    return (final_damage, critical + ' dealt %.2f damage.'
            % final_damage)


def battle(shipa, shipb):
    ship_a = HashShip(shipa)
    ship_b = HashShip(shipb)
    ahit = 0
    bhit = 0
    time = 0
    battle_log = ''
    while True:
        time += 1
        if time // ship_a.fire_rate > ahit:
            ahit += 1
            damage, info = hit(ship_a, ship_b)
            ship_b.remaining_hp -= damage
            battle_log += ('%s->%s: %s %.2f hp remains.\n'
                           % (shipa, shipb, info, ship_b.remaining_hp))
        if time // ship_b.fire_rate > bhit:
            bhit += 1
            damage, info = hit(ship_b, ship_a)
            ship_a.remaining_hp -= damage
            battle_log += ('%s->%s: %s %.2f hp remains.\n'
                           % (shipb, shipa, info, ship_a.remaining_hp))
        if ship_a.remaining_hp <= 0 or ship_b.remaining_hp <= 0:
            break
    if ship_a.remaining_hp <=0 and ship_b.remaining_hp > 0:
        battle_log += '%s wins!\n' % shipb
    elif ship_b.remaining_hp <=0 and ship_a.remaining_hp > 0:
        battle_log += '%s wins!\n' % shipa
    else:
        battle_log += 'Both ship destroyed at the same time!'

    return battle_log


def main(argv):
    print battle(argv[1], argv[2])
    
if __name__ == "__main__":
    main(sys.argv)
