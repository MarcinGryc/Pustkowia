"""Jedyne źródło balansu przedmiotów, przeciwników i awansów."""
import time

ITEMS = {
    'knife': dict(name='Zardzewiały nóż', kind='weapon', icon='knife', description='Nie wygląda najlepiej. Wciąż spełnia swoją rolę.', attack=7, defense=0, price=30, sell=12),
    'club': dict(name='Metalowa pałka', kind='weapon', icon='club', description='Kawał rury i odrobina pewności siebie.', attack=12, defense=0, price=65, sell=26),
    'pistol': dict(name='Pistolet samoróbka', kind='weapon', icon='pistol', description='Złożony z odzyskanych części. Nie wymaga amunicji.', attack=20, defense=0, price=150, sell=60),
    'jacket': dict(name='Zniszczona kurtka', kind='armor', icon='armor', description='Pamięta lepszy świat. Chroni przed czymś więcej niż chłodem.', attack=0, defense=3, price=25, sell=10),
    'scrap_armor': dict(name='Pancerz ze złomu', kind='armor', icon='armor', description='Ciężki, niewygodny i zaskakująco skuteczny.', attack=0, defense=8, price=110, sell=44),
    'medkit': dict(name='Apteczka', kind='other', icon='medkit', description='Przywraca do 45 HP. W walce zużywa turę.', attack=0, defense=0, heal=45, price=25, sell=10),
    'scrap': dict(name='Złom', kind='other', icon='scrap', description='To, co dla jednych jest śmieciem, dla innych ma wartość.', attack=0, defense=0, price=8, sell=4),
    'electronics': dict(name='Części elektroniczne', kind='other', icon='electronics', description='Małe fragmenty dawnej cywilizacji.', attack=0, defense=0, price=20, sell=10),
}
ENEMIES = {
    'rat': dict(name='Zmutowany szczur', hp=24, attack=7, defense=0, gold=12, xp=20, icon='rat'),
    'ghoul': dict(name='Dziki ghul', hp=40, attack=11, defense=2, gold=22, xp=35, icon='ghoul'),
    'bandit': dict(name='Bandyta pustkowi', hp=52, attack=14, defense=3, gold=30, xp=45, icon='bandit'),
}
BASE_ATTACK = 6
BASE_HP = 100
SHOP = ['knife', 'club', 'pistol', 'jacket', 'scrap_armor', 'medkit']


def xp_threshold(level):
    return 100 * level


def new_state(nickname=None):
    return dict(nickname=nickname, level=1, gold=100, rank='Neutralna', hp=BASE_HP, xp=0,
                upgrades=dict(attack=0, defense=0, hp=0), upgrade_points=0, regen_at=time.time(),
                inventory={'knife': 1, 'jacket': 1, 'medkit': 2},
                equipment={'weapon': None, 'armor': None}, points=[],
                battle=None, last_battle=None, expedition=None, daily={}, location=None)


def max_hp(s):
    return BASE_HP + s.get('upgrades', {}).get('hp', (s['level'] - 1) * 12)


def stats(s):
    bonuses = s.get('upgrades', {})
    return dict(attack=BASE_ATTACK + bonuses.get('attack', 0) + ITEMS.get(s['equipment']['weapon'], {}).get('attack', 0),
                defense=bonuses.get('defense', 0) + ITEMS.get(s['equipment']['armor'], {}).get('defense', 0))
