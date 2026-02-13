import random
import time

TICK_DURATION = 0.1
MAX_MEMORY = 5


def weighted_choice(choices: dict):
    total = sum(choices.values())
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices.items():
        if upto + weight >= r:
            return choice
        upto += weight
    return random.choice(list(choices.keys()))


class NPC:
    def __init__(self, name):
        self.name = name
        self.level = random.randint(1, 3)
        self.gold = random.randint(5, 20)
        self.energy = 100

        self.max_hp = 50 + self.level * 10
        self.hp = self.max_hp
        self.attack = 5 + self.level * 2
        self.defense = 2 + self.level

        # ЛИЧНОСТЬ (ключевой момент)
        archetypes = {
            "aggressive": {"aggression": 0.9, "social": 0.3, "greedy": 0.4, "cautious": 0.2},
            "bully":      {"aggression": 0.8, "social": 0.4, "greedy": 0.2, "cautious": 0.3},
            "merchant":   {"aggression": 0.2, "social": 0.6, "greedy": 0.9, "cautious": 0.6},
            "loner":      {"aggression": 0.4, "social": 0.1, "greedy": 0.3, "cautious": 0.7},
            "diplomat":   {"aggression": 0.1, "social": 0.9, "greedy": 0.2, "cautious": 0.5},
        }

        atype = random.choice(list(archetypes.values()))
        self.aggression = atype["aggression"]
        self.social = atype["social"]
        self.greedy = atype["greedy"]
        self.cautious = atype["cautious"]

        self.relationships = {}
        self.memory = []

    def is_alive(self):
        return self.hp > 0

    def remember(self, event):
        self.memory.append(event)
        if len(self.memory) > MAX_MEMORY:
            self.memory.pop(0)

    def change_relation(self, other, amount):
        self.relationships[other] = self.relationships.get(other, 0) + amount
        self.relationships[other] = max(-100, min(100, self.relationships[other]))

    # 🔥 ВЗВЕШЕННЫЙ ВЫБОР ЦЕЛИ
    def choose_goal(self):
        weights = {}

        # отдых
        weights["rest"] = max(0, (100 - self.energy) / 10) * self.cautious

        # работа
        weights["work"] = max(0, (20 - self.gold)) * self.greedy

        # исследование
        weights["explore"] = (
            self.energy / 20
            * (1 - self.cautious)
        )

        # социалка
        weights["socialize"] = self.social * (self.energy / 30)

        # если есть сильные враги — выше шанс конфликта
        worst_relation = min(self.relationships.values(), default=0)
        if worst_relation < -30:
            weights["socialize"] += abs(worst_relation) * self.aggression

        return weighted_choice(weights)

    def act(self, world):
        if not self.is_alive():
            return f"{self.name} мёртв"

        goal = self.choose_goal()

        if goal == "rest":
            self.energy += 30
            self.hp = min(self.max_hp, self.hp + 10)
            return f"{self.name} отдыхает"

        elif goal == "work":
            earned = random.randint(3, 8)
            self.gold += earned
            self.energy -= 20
            return f"{self.name} работает и зарабатывает {earned} золота"

        elif goal == "explore":
            self.energy -= 25
            if random.random() < 0.3:
                self.level += 1
                self.max_hp += 10
                self.attack += 2
                self.defense += 1
                return f"{self.name} повышает уровень до {self.level}"
            return f"{self.name} исследует мир"

        elif goal == "socialize":
            other = world.get_random_npc(exclude=self)
            if not other:
                return f"{self.name} не нашёл собеседника"

            hostility = self.relationships.get(other.name, 0)
            roll = random.random()
            # провокация без причины
            if roll < self.aggression * 0.2:
                self.change_relation(other.name, -15)
                other.change_relation(self.name, -5)
                return f"{self.name} провоцирует конфликт с {other.name}"

            # агрессия влияет на вероятность конфликта
            if hostility < -20 and roll < self.aggression:
                self.change_relation(other.name, -10)
                other.change_relation(self.name, -10)
                return f"{self.name} агрессивно конфликтует с {other.name}"

            # позитив
            if roll < self.social:
                self.change_relation(other.name, +10)
                other.change_relation(self.name, +10)
                return f"{self.name} приятно общается с {other.name}"

            return f"{self.name} нейтрально общается с {other.name}"

        return f"{self.name} бездействует"


class Combat:
    @staticmethod
    def duel(a: NPC, b: NPC):
        log = [f"⚔ Дуэль: {a.name} vs {b.name}"]
        turn = 0

        while a.is_alive() and b.is_alive():
            attacker, defender = (a, b) if turn % 2 == 0 else (b, a)
            damage = max(1, attacker.attack - defender.defense + random.randint(-2, 2))
            defender.hp -= damage
            log.append(
                f"{attacker.name} бьёт {defender.name} на {damage} урона "
                f"(HP {defender.hp}/{defender.max_hp})"
            )
            turn += 1
            time.sleep(0.2)

        winner = a if a.is_alive() else b
        loser = b if winner == a else a

        winner.change_relation(loser.name, -20)
        loser.change_relation(winner.name, -40)

        log.append(f"🏆 Победитель: {winner.name}")
        return log


class World:
    def __init__(self):
        self.tick = 0
        self.npcs = []

    def add_npc(self, npc):
        self.npcs.append(npc)

    def get_random_npc(self, exclude=None):
        candidates = [n for n in self.npcs if n != exclude and n.is_alive()]
        return random.choice(candidates) if candidates else None

    def check_conflicts(self):
        for npc in self.npcs:
            for other_name, relation in npc.relationships.items():
                if relation <= -40 and npc.energy > 30:
                    other = self.get_npc_by_name(other_name)
                    if other and other.is_alive():
                        return npc, other
        return None

    def get_npc_by_name(self, name):
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None

    def world_tick(self):
        self.tick += 1
        print(f"\n=== ТИК МИРА {self.tick} ===")

        conflict = self.check_conflicts()
        if conflict:
            a, b = conflict
            print("\n".join(Combat.duel(a, b)))
            a.energy -= 20
            b.energy -= 20
            return

        self.npcs.sort(key=lambda n: n.name)
        for npc in self.npcs:
            print(npc.act(self))

    def run(self):
        print("Мир запущен...")
        while True:
            self.world_tick()
            time.sleep(TICK_DURATION)


if __name__ == "__main__":
    world = World()

    names = [
        "Kai", "Lyn", "Aron", "Mira", "Tess",
        "Rin", "Noah", "Elia", "Sora", "Vex"
    ]

    for name in names:
        world.add_npc(NPC(name))

    world.run()
