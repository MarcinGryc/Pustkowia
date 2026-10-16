"""Jedyne źródło balansu przedmiotów, przeciwników i awansów."""
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
HP_PER_LEVEL = 12
SHOP = ['club', 'pistol', 'scrap_armor', 'medkit', 'jacket']


def xp_threshold(level):
    return 100 * level


def new_state():
    return dict(level=1, gold=100, rank='Neutralna', hp=BASE_HP, xp=0,
                inventory={'knife': 1, 'jacket': 1, 'medkit': 2},
                equipment={'weapon': 'knife', 'armor': 'jacket'}, points=[],
                battle=None, last_battle=None, expedition=None, daily={}, location=None)


def max_hp(s):
    return BASE_HP + (s['level'] - 1) * HP_PER_LEVEL


def stats(s):
    return dict(attack=BASE_ATTACK + ITEMS.get(s['equipment']['weapon'], {}).get('attack', 0),
                defense=ITEMS.get(s['equipment']['armor'], {}).get('defense', 0))
