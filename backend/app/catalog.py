"""Jedyne źródło balansu przedmiotów, przeciwników i awansów."""
import time

ITEMS = {
    'knife': dict(name='Zardzewiały nóż', kind='weapon', icon='knife', description='Nie wygląda najlepiej. Wciąż spełnia swoją rolę.', attack=7, defense=0, price=30, sell=12),
    'club': dict(name='Metalowa pałka', kind='weapon', icon='club', description='Kawał rury i odrobina pewności siebie.', attack=12, defense=0, price=65, sell=26),
    'machete': dict(name='Maczeta', kind='weapon', icon='machete', description='Ciężkie ostrze do przedzierania się przez pustkowia. Nie wymaga amunicji.', attack=17, defense=0, price=100, sell=40),
    'chainsaw': dict(name='Piła mechaniczna', kind='weapon', icon='chainsaw', description='Ryk silnika i stalowe zęby. Nie zużywa nabojów.', attack=30, defense=0, price=260, sell=104),
    'pistol': dict(name='Pistolet', kind='weapon', icon='pistol', description='Poręczna broń palna. Każdy strzał zużywa 1 uniwersalny nabój.', attack=20, defense=0, uses_ammo=True, price=150, sell=60),
    'revolver': dict(name='Rewolwer', kind='weapon', icon='revolver', description='Niezawodny bęben i mocne uderzenie. Strzał kosztuje 1 nabój.', attack=26, defense=0, uses_ammo=True, price=230, sell=92),
    'ak47': dict(name='Kałach', kind='weapon', icon='ak47', description='Karabin, który przetrwał koniec świata. Atak zużywa 1 nabój.', attack=38, defense=0, uses_ammo=True, price=420, sell=168),
    'jacket': dict(name='Zniszczona kurtka', kind='armor', icon='armor', description='Pamięta lepszy świat. Chroni przed czymś więcej niż chłodem.', attack=0, defense=3, price=25, sell=10),
    'leather_jacket': dict(name='Skórzana kurtka', kind='armor', icon='leather_jacket', description='Gruba skóra i wzmocnione szwy. Dobry początek solidnej ochrony.', attack=0, defense=5, price=60, sell=24),
    'scrap_armor': dict(name='Pancerz ze złomu', kind='armor', icon='armor', description='Ciężki, niewygodny i zaskakująco skuteczny.', attack=0, defense=8, price=110, sell=44),
    'bulletproof_vest': dict(name='Kamizelka kuloodporna', kind='armor', icon='bulletproof_vest', description='Płyty balistyczne i wojskowe kieszenie. Chroni w każdej walce.', attack=0, defense=12, price=190, sell=76),
    'heavy_armor': dict(name='Ciężki pancerz', kind='armor', icon='heavy_armor', description='Pełna osłona z grubych płyt, hełmu i nagolenników.', attack=0, defense=18, price=320, sell=128),
    'exoskeleton': dict(name='Egzoszkielet', kind='armor', icon='exoskeleton', description='Wspomagany szkielet i szczelny pancerz. Szczyt technologii pustkowi.', attack=0, defense=28, price=650, sell=260),
    'ammo': dict(name='Nabój', kind='other', icon='ammo', description='Uniwersalna amunicja do pistoletu, rewolweru i kałacha. 1 strzał = 1 nabój.', attack=0, defense=0, price=3, sell=1),
    'grenade': dict(name='Granat', kind='other', icon='grenade', description='Jednorazowy rzut: 45 obrażeń bieżącemu przeciwnikowi, z pominięciem obrony. Zużywa turę.', attack=0, defense=0, damage=45, price=45, sell=18),
    'medkit': dict(name='Apteczka', kind='other', icon='medkit', description='Przywraca do 45 HP. W walce zużywa turę.', attack=0, defense=0, heal=45, price=25, sell=10),
    'scrap': dict(name='Złom', kind='other', icon='scrap', description='To, co dla jednych jest śmieciem, dla innych ma wartość.', attack=0, defense=0, price=8, sell=4),
    'electronics': dict(name='Części elektroniczne', kind='other', icon='electronics', description='Małe fragmenty dawnej cywilizacji.', attack=0, defense=0, price=20, sell=10),
}
ENEMIES = {
    'rat': dict(name='Zmutowany szczur', hp=24, attack=7, defense=0, gold=12, xp=20, icon='rat'),
    'ghoul': dict(name='Dziki ghul', hp=40, attack=11, defense=2, gold=22, xp=35, icon='ghoul'),
    'bandit': dict(name='Bandyta pustkowi', hp=52, attack=14, defense=3, gold=30, xp=45, icon='bandit'),
    'mutant': dict(name='Mutant', hp=90, attack=22, defense=5, gold=55, xp=80, icon='mutant'),
}
SETTLEMENTS = {
    'camp': dict(name='Obóz', bonus_kind='weapon', bonus_label='broń'),
    'settlement': dict(name='Osada', bonus_kind='armor', bonus_label='pancerze'),
    'city': dict(name='Miasto', bonus_kind='other', bonus_label='pozostałe przedmioty'),
}
BASE_ATTACK = 6
BASE_HP = 100
HP_PER_LEVEL = 12
SHOP = [key for key in ITEMS if key not in ('scrap', 'electronics')]


def sell_price(item_id, point):
    item = ITEMS[item_id]
    settlement = SETTLEMENTS.get(point.get('settlement', 'settlement'), SETTLEMENTS['settlement'])
    return round(item['sell'] * (1.1 if item['kind'] == settlement['bonus_kind'] else 1), 1)


def xp_threshold(level):
    return 100 * level


def new_state(nickname=None):
    return dict(nickname=nickname, level=1, gold=100, rank='Neutralna', hp=BASE_HP, xp=0,
                regen_at=time.time(),
                inventory={'knife': 1, 'jacket': 1, 'medkit': 2},
                equipment={'weapon': None, 'armor': None}, points=[],
                battle=None, last_battle=None, expedition=None, daily={}, location=None)


def max_hp(s):
    return BASE_HP + (s['level'] - 1) * HP_PER_LEVEL


def stats(s):
    return dict(attack=BASE_ATTACK + ITEMS.get(s['equipment']['weapon'], {}).get('attack', 0),
                defense=ITEMS.get(s['equipment']['armor'], {}).get('defense', 0))
