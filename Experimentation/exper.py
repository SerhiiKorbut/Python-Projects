import random
import time
import json 

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

        # Personality traits and archetypes
        archetypes = {
            "aggressive": {"aggression": 0.9, "social": 0.3, "greedy": 0.4, "cautious": 0.2},
            "bully":      {"aggression": 0.8, "social": 0.4, "greedy": 0.2, "cautious": 0.3},
            "merchant":   {"aggression": 0.2, "social": 0.6, "greedy": 0.9, "cautious": 0.6},
            "loner":      {"aggression": 0.4, "social": 0.1, "greedy": 0.3, "cautious": 0.7},
            "diplomat":   {"aggression": 0.1, "social": 0.9, "greedy": 0.2, "cautious": 0.5},
            "strategist": {"aggression": 0.5, "social": 0.7, "greedy": 0.4, "cautious": 0.8},
            "trickster":  {"aggression": 0.6, "social": 0.8, "greedy": 0.7, "cautious": 0.3},
            "pacifist":   {"aggression": 0.0, "social": 0.9, "greedy": 0.3, "cautious": 0.6},
            "hoarder":    {"aggression": 0.3, "social": 0.2, "greedy": 1.0, "cautious": 0.5},
            "wanderer":   {"aggression": 0.2, "social": 0.4, "greedy": 0.2, "cautious": 0.7},
        }

        atype_name, atype = random.choice(list(archetypes.items()))
        self.archetype_name = atype_name
        self.aggression = atype["aggression"]
        self.social = atype["social"]
        self.greedy = atype["greedy"]
        self.cautious = atype["cautious"]

        self.relationships = {}
        self.memory = []
        self.guild = None 

    def is_alive(self):
        return self.hp > 0

    def remember(self, event):
        self.memory.append(event)
        if len(self.memory) > MAX_MEMORY:
            self.memory.pop(0)

    def change_relation(self, other, amount):
        self.relationships[other] = self.relationships.get(other, 0) + amount
        self.relationships[other] = max(-100, min(100, self.relationships[other]))

    # Choose goal based on personality and current state
    def choose_goal(self):
        weights = {}

        weights["rest"] = max(0, (100 - self.energy) / 10) * self.cautious

        weights["work"] = max(0, (20 - self.gold)) * self.greedy

        weights["explore"] = self.energy / 20 * (1 - self.cautious)

        weights["socialize"] = self.social * (self.energy / 30)

        weights["trade"] = self.greedy * (self.gold / 30)

        weights["guild"] = 0.1 

        # If relationships are bad, more likely to socialize (to improve them) or aggressive (to vent)
        worst_relation = min(self.relationships.values(), default=0)
        if worst_relation < -30:
            weights["socialize"] += abs(worst_relation) * self.aggression

        return weighted_choice(weights)


    def act(self, world):
        if not self.is_alive():
            return f"{self.name} is dead."
        
        # Check if should leave guild
        leave_msg = self.consider_leaving_guild()
        if leave_msg:
            return leave_msg

        goal = self.choose_goal()

        if goal == "rest":
            self.energy += 30
            self.hp = min(self.max_hp, self.hp + 10)
            return f"{self.name} rests"

        elif goal == "work":
            earned = random.randint(3, 8)
            self.gold += earned
            self.energy -= 20
            return f"{self.name} works hard and earned {earned} gold"

        elif goal == "explore":
            self.energy -= 25
            if random.random() < 0.3:
                self.level += 1
                self.max_hp += 10
                self.attack += 2
                self.defense += 1
                return f"{self.name} levels up to {self.level}"
            return f"{self.name} explores the world"

        elif goal == "socialize":
            other = world.get_random_npc(exclude=self)
            if not other:
                return f"{self.name} didn't find anyone to socialize with"

            hostility = self.relationships.get(other.name, 0)
            roll = random.random()
            # Provocation
            if roll < self.aggression * 0.4:
                self.change_relation(other.name, -15)
                other.change_relation(self.name, -5)
                return f"{self.name} provokes conflict with {other.name}"

            # Aggression
            if hostility < -20 and roll < self.aggression * 1.5:
                self.change_relation(other.name, -10)
                other.change_relation(self.name, -10)
                return f"{self.name} argues with {other.name}"

            # Positive social interaction
            if roll < self.social:
                self.change_relation(other.name, +10)
                other.change_relation(self.name, +10)
                return f"{self.name} has a nice talk with {other.name}"

            return f"{self.name} talks with {other.name}"

        elif goal == "trade":
            other = world.get_random_npc(exclude=self)
            if not other:
                return f"{self.name} didn't find anyone to trade with"

            # How much to trade based on greed and current gold
            amount = min(5, self.gold)
            if amount <= 0:
                return f"{self.name} wants to trade but has no gold"

            # Transfer gold
            self.gold -= amount
            other.gold += amount

            # Improve relations due to trade
            self.change_relation(other.name, +5)
            other.change_relation(self.name, +5)

            # Remember the trade
            self.remember(f"traded with {other.name}")
            other.remember(f"traded with {self.name}")

            return f"{self.name} trades with {other.name} and gives {amount} gold"

        elif goal == "guild":
            if not self.is_alive():
                return f"{self.name} is dead and cannot act with guild"

            if self.guild:
                other = world.get_random_npc(exclude=self)
                if other and not other.guild:
                    self.guild.add_member(other)
                    return f"{self.name} invites {other.name} to guild {self.guild.name}"
                else:
                    return f"{self.name} checks guild {self.guild.name}"
            else:
                # chance to create a new guild
                guild_name = f"Guild_{self.name}_{world.tick}"
                new_guild = Guild(guild_name)
                new_guild.add_member(self)
                world.guilds.append(new_guild)
                return f"{self.name} creates a new guild {guild_name}"



        return f"{self.name} idles"

    def consider_leaving_guild(self):
            """Chance to leave the guild"""
            if not self.guild:
                return False

            guild_name = self.guild.name  # save name in advance

            # chance of random departure (small)
            if random.random() < 0.01:  # 1% chance per tick
                self.guild.remove_member(self)
                return f"{self.name} leaves guild {guild_name} randomly"

            # check for bad relationships within guild
            if self.guild:
                for member in self.guild.members:
                    if member != self:
                        relation = self.relationships.get(member.name, 0)
                        if relation < -50:
                            self.guild.remove_member(self)
                            return f"{self.name} leaves guild {guild_name} due to conflict with {member.name}"

            return False



class Combat:
    @staticmethod
    def duel(a: NPC, b: NPC):
        log = [f"⚔ Duel: {a.name} vs {b.name}"]
        turn = 0

        while a.is_alive() and b.is_alive():
            attacker, defender = (a, b) if turn % 2 == 0 else (b, a)
            damage = max(1, attacker.attack - defender.defense + random.randint(-2, 2))
            defender.hp -= damage
            log.append(
                f"{attacker.name} hits {defender.name} for {damage} damage "
                f"(HP {defender.hp}/{defender.max_hp})"
            )
            turn += 1
            time.sleep(0.2)

        winner = a if a.is_alive() else b
        loser = b if winner == a else a

        winner.change_relation(loser.name, -20)
        loser.change_relation(winner.name, -40)

        log.append(f"🏆 Winner: {winner.name}")
        return log


class World:
    def __init__(self):
        self.tick = 0
        self.npcs = []
        self.guilds = []
        self.history = []  
        self.event_log = [] 

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
                        if npc.guild and other.guild and npc.guild == other.guild:
                            continue
                        return npc, other

        return None

    def get_npc_by_name(self, name):
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None

    def world_tick(self):
        self.tick += 1
        print(f"\n=== WORLD TICK {self.tick} ===")

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

        # check for guild wars
        self.check_guild_wars()

        self.save_state(f"world_state_tick.json")
        self.save_log()  # update text log

        # conduct battles between warring guilds
        for guild in self.guilds:
            for enemy_guild in guild.enemies:
                # get alive members of both guilds
                alive_members = [m for m in guild.members if m.is_alive()]
                alive_opponents = [m for m in enemy_guild.members if m.is_alive()]

                if not alive_members or not alive_opponents:
                    continue  # skip if no alive members

                # choose random fighter and opponent
                member = random.choice(alive_members)
                opponent = random.choice(alive_opponents)

                print("\n".join(Combat.duel(member, opponent)))
                member.energy -= 20
                opponent.energy -= 20

                if not any(m.is_alive() for m in enemy_guild.members):
                    guild.enemies.remove(enemy_guild)
                    enemy_guild.enemies.remove(guild)
                    print(f"🏳️ Guild {guild.name} defeats guild {enemy_guild.name} and the war ends!")

    def save_state(self, filename="world_state.json"):
        data = {
            "tick": self.tick,
            "npcs": [],
            "guilds": [],
        }

        for npc in self.npcs:
            data["npcs"].append({
                "name": npc.name,
                "hp": npc.hp,
                "max_hp": npc.max_hp,
                "gold": npc.gold,
                "level": npc.level,
                "energy": npc.energy,
                "guild": npc.guild.name if npc.guild else None,
                "relationships": npc.relationships,
                "archetype": npc.archetype_name,
                "traits": {  # <-- new fields
                    "aggression": npc.aggression,
                    "social": npc.social,
                    "greedy": npc.greedy,
                    "cautious": npc.cautious
                }
            })

        for guild in self.guilds:
            data["guilds"].append({
                "name": guild.name,
                "members": [m.name for m in guild.members],
                "enemies": [e.name for e in guild.enemies]
            })

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save_log(self, filename="world_log.txt"):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.event_log))


    def run(self):
        print("World started...")
        while True:
            self.world_tick()
            time.sleep(TICK_DURATION)
    
    def check_guild_wars(self):
        """Check if there is reason for war between guilds"""
        for guild in self.guilds:
            for member in guild.members:
                for other in self.npcs:
                    if other.guild and other.guild != guild:
                        relation = member.relationships.get(other.name, 0)
                        if relation <= -40 and other.guild not in guild.enemies:
                            # start war
                            guild.declare_war(other.guild)
                            print(f"🔥 Guild {guild.name} declares war on guild {other.guild.name}")


class Guild:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.enemies = []  

    def declare_war(self, other_guild):
        if other_guild not in self.enemies:
            self.enemies.append(other_guild)
        if self not in other_guild.enemies:
            other_guild.enemies.append(self)

    def add_member(self, npc):
        if npc not in self.members:
            self.members.append(npc)
            npc.guild = self

    def remove_member(self, npc):
        if npc in self.members:
            self.members.remove(npc)
            npc.guild = None

    def is_member(self, npc):
        return npc in self.members

    def __str__(self):
        return f"Guild {self.name} ({len(self.members)} members)"


if __name__ == "__main__":
    world = World()

    names = [
        "Kai", "Lyn", "Aron", "Mira", "Tess",
        "Rin", "Noah", "Elia", "Sora", "Vex",
        "Luca", "Faye", "Orin", "Zara", "Talon",
        "Milo", "Lyra", "Dante", "Iris", "Vera",
        "Cyrus", "Nina", "Alaric", "Selene", "Juno",
        "Kara", "Rafael", "Vanya", "Esme", "Oberon",
        "Talia", "Eamon", "Fiora", "Lucien", "Sylas",
        "Aurea", "Corin", "Isolde", "Niko", "Thane",
        "Lyric", "Maris", "Cassian", "Elowen", "Gideon",
        "Sable", "Orla", "Quinn", "Ronan", "Seraph",
        "Vesper", "Xander", "Yara", "Zephyr", "Alden",
        "Briar", "Calla", "Dorian", "Eira", "Fenris"
    ]

    for name in names:
        world.add_npc(NPC(name))
        for npc in world.npcs:
            for other in world.npcs:
                if other != npc:
                    # some randomness so conflicts can arise immediately
                    npc.relationships[other.name] = random.randint(-5, 5)


    world.run()
