import random
import time
import os
import sys

# -----------------------
# Colors
# -----------------------
class Colors:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

# -----------------------
# Utils
# -----------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def input_int(prompt, min_value=None, max_value=None):
    """Safe input of an integer with boundary checking (returns None if cancelled)."""
    while True:
        try:
            s = input(prompt)
            if s.strip() == "":
                return None
            val = int(s)
            if min_value is not None and val < min_value:
                print(f"{Colors.RED}Value must be >= {min_value}{Colors.RESET}")
                continue
            if max_value is not None and val > max_value:
                print(f"{Colors.RED}Value must be <= {max_value}{Colors.RESET}")
                continue
            return val
        except ValueError:
            print(f"{Colors.RED}Enter an integer.{Colors.RESET}")

# -----------------------
# Balance storage
# -----------------------
BALANCE_FILE = "balance.txt"
COLLECTION_FILE = "collection.txt"
BOOST_FILE = "boost.txt"

def load_balance(default=1000):
    try:
        if os.path.exists(BALANCE_FILE):
            with open(BALANCE_FILE, "r", encoding="utf-8") as f:
                s = f.read().strip()
                return int(s)
    except Exception:
        pass
    return default

def save_balance(balance):
    try:
        with open(BALANCE_FILE, "w", encoding="utf-8") as f:
            f.write(str(int(balance)))
    except Exception as e:
        print(f"{Colors.RED}Failed to save balance: {e}{Colors.RESET}")

# -----------------------
# Casino Core
# -----------------------
class Casino:
    def __init__(self, start_balance=1000):
        self.balance = load_balance(start_balance)

    def add_chips(self, amount):
        self.balance += amount

    def remove_chips(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

    def show_balance(self):
        print(f"{Colors.CYAN}Your balance: {Colors.YELLOW}{self.balance} chips{Colors.RESET}")

# -----------------------
# Slots 🎰
# -----------------------
SLOT_SYMBOLS = [
    ("🍒", 40),   # frequent
    ("🍋", 30),
    ("🔔", 20),
    ("⭐", 8),
    ("💎", 2),    # rare
]

REWARD_MULTIPLIERS = {
    "🍒": 3,
    "🍋": 5,
    "🔔": 10,
    "⭐": 20,
    "💎": 50,
}

def weighted_choice(symbols):
    total = sum(w for s, w in symbols)
    r = random.randint(1, total)
    for symbol, weight in symbols:
        r -= weight
        if r <= 0:
            return symbol
    # на всякий случай:
    return symbols[-1][0]

def spin_animation_simple(spin_count=12, delay=0.07):
    """Slot animation: single line, no extra lines on screen."""
    for _ in range(spin_count):
        reel = [random.choice([s for s, w in SLOT_SYMBOLS]) for _ in range(3)]
        line = " | ".join(reel)
        sys.stdout.write("\r" + line + "   ")  # overwrite line
        sys.stdout.flush()
        time.sleep(delay)

    sys.stdout.write("\r" + " " * 20)  # clear line
    sys.stdout.flush()
    sys.stdout.write("\r")  # return to start


def play_slots(casino: Casino):
    clear()
    print(f"{Colors.BOLD}{Colors.MAGENTA}=== SLOTS ==={Colors.RESET}\n")
    casino.show_balance()
    print("Enter bet (empty input - cancel).")

    bet = input_int("Bet: ", min_value=1)
    if bet is None:
        print("Cancelled.")
        return

    if bet <= 0:
        print(f"{Colors.RED}Bet must be greater than zero.{Colors.RESET}")
        return

    if not casino.remove_chips(bet):
        print(f"{Colors.RED}Not enough chips!{Colors.RESET}")
        return

    print("\nSpinning the reels...")
    # simulating spin, can vary
    spin_animation_simple(spin_count=14, delay=0.06)
    time.sleep(0.1)

    # final result on 3 reels
    result = [weighted_choice(SLOT_SYMBOLS) for _ in range(3)]
    print(f"\n{Colors.BOLD}{' | '.join(result)}{Colors.RESET}\n")

    # win logic: three same - win, otherwise - loss
    if result[0] == result[1] == result[2]:
        sym = result[0]
        mult = REWARD_MULTIPLIERS.get(sym, 0)
        win = bet * mult
        casino.add_chips(win)
        print(f"{Colors.GREEN}Jackpot! Three {sym} - you won {win} chips (x{mult})!{Colors.RESET}")
    else:
        # partial win with two matches
        two_same = (result[0] == result[1]) or (result[1] == result[2]) or (result[0] == result[2])
        if two_same:
            # small return 50% of bet
            ret = bet // 2
            casino.add_chips(ret)
            print(f"{Colors.YELLOW}Two matching symbols - returned {ret} chips.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Oops - you lost your bet.{Colors.RESET}")

# -----------------------
# Roulette 🎡
# -----------------------
ROULETTE_NUMBERS = list(range(37))  # 0-36
ROULETTE_RED = {
    1,3,5,7,9,12,14,16,18,
    19,21,23,25,27,30,32,34,36
}
ROULETTE_BLACK = set(ROULETTE_NUMBERS) - ROULETTE_RED - {0}

ROULETTE_WHEEL = [
    0,
    32,15,19,4,21,2,25,17,34,6,
    27,13,36,11,30,8,23,10,5,24,
    16,33,1,20,14,31,9,22,18,29,
    7,28,12,35,3,26
]

def roulette_animation_single_line(spin_time=3.0):
    """Roulette animation on single line"""
    start_idx = random.randint(0, len(ROULETTE_WHEEL)-1)
    t_start = time.time()
    delay = 0.01

    final_num = None

    while True:
        # central number + left/right "window"
        window = [ROULETTE_WHEEL[(start_idx + i) % len(ROULETTE_WHEEL)] for i in range(-3, 4)]
        line = ""
        for i, n in enumerate(window):
            if n in ROULETTE_RED:
                color = "\033[41m"
            elif n in ROULETTE_BLACK:
                color = "\033[40m"
            else:
                color = "\033[42m"
            if i == 3:
                line += f"{color}{Colors.BOLD}[{n:2d}]{Colors.RESET} "
            else:
                line += f"{color} {n:2d} {Colors.RESET} "
        sys.stdout.write("\r" + line)
        sys.stdout.flush()

        time.sleep(delay)

        elapsed = time.time() - t_start
        if elapsed > spin_time:
            final_num = window[3]
            break
        delay += 0.002
        start_idx = (start_idx + 1) % len(ROULETTE_WHEEL)

    sys.stdout.write("\n")
    return final_num

def play_roulette(casino: Casino):
    clear()
    print(f"{Colors.BOLD}{Colors.GREEN}=== ROULETTE ==={Colors.RESET}\n")
    casino.show_balance()

    print("Bets:")
    print("1 - Red (x2)")
    print("2 - Black (x2)")
    print("3 - Exact number (0-36) (x36)")
    print("Empty input - cancel.\n")

    bet_type = input("Bet type: ").strip()
    if bet_type == "":
        print("Cancelled.")
        return

    if bet_type not in ("1", "2", "3"):
        print(f"{Colors.RED}Invalid choice.{Colors.RESET}")
        return

    bet = input_int("Bet (chips): ", min_value=1)
    if bet is None:
        print("Cancelled.")
        return

    if not casino.remove_chips(bet):
        print(f"{Colors.RED}Not enough chips!{Colors.RESET}")
        return

    chosen_number = None

    if bet_type == "3":
        chosen_number = input_int("Enter number (0-36): ", 0, 36)
        if chosen_number is None:
            print("Cancelled.")
            casino.add_chips(bet)
            return

    print("\nWheel is spinning...\n")
    result = roulette_animation_single_line()
    color = (
        f"{Colors.RED}RED{Colors.RESET}" if result in ROULETTE_RED
        else f"{Colors.BLUE}BLACK{Colors.RESET}" if result in ROULETTE_BLACK
        else f"{Colors.GREEN}GREEN (0){Colors.RESET}"
    )

    print(f"Result: {Colors.BOLD}{result}{Colors.RESET} - {color}\n")

    # ---- Win logic ----
    if bet_type == "1":  # red
        if result in ROULETTE_RED:
            win = bet * 2
            casino.add_chips(win)
            print(f"{Colors.GREEN}You won {win} chips!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Loss.{Colors.RESET}")

    elif bet_type == "2":  # black
        if result in ROULETTE_BLACK:
            win = bet * 2
            casino.add_chips(win)
            print(f"{Colors.GREEN}You won {win} chips!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Loss.{Colors.RESET}")

    elif bet_type == "3":  # exact number
        if result == chosen_number:
            win = bet * 36
            casino.add_chips(win)
            print(f"{Colors.GREEN}Exact hit! +{win} chips!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Wrong number.{Colors.RESET}")

# -----------------------
# Work
# -----------------------

def work_job(casino: Casino):
    clear()
    print(f"{Colors.BOLD}{Colors.CYAN}=== WORK ==={Colors.RESET}\n")
    print("You can earn chips by completing tasks.\n")
    
    # List of texts for retyping
    texts = [
        "Python Casino Challenge: type this exactly!",
        "The quick brown fox jumps over the lazy dog.",
        "Work hard, play hard!",
        "I love coding in Python and making games!",
        "Copying this text is forbidden!"
    ]
    
    jobs = ["text", "math"]
    job_type = random.choice(jobs)
    
    if job_type == "text":
        # Choose random text and insert invisible characters
        original = random.choice(texts)
        invisible_text = ""
        for c in original:
            invisible_text += c + ("\u200B" if random.random() < 0.1 else "")  # insert invisible character randomly
        print(f"{Colors.YELLOW}{invisible_text}{Colors.RESET}")
        print("(Type the text completely, copying will not work!)")
        attempt = input("Enter text: ")
        
        # Check for invisible characters
        if "\u200B" in attempt:
            penalty = min(10, casino.balance)
            if penalty > 0:
                casino.remove_chips(penalty)
                print(f"{Colors.RED}You tried to copy the text! Penalty {penalty} chips.{Colors.RESET}")
            else:
                print(f"{Colors.RED}You tried to copy the text! But no chips to penalize.{Colors.RESET}")
        elif attempt.strip() == original:
            reward = random.randint(5, 20)
            casino.add_chips(reward)
            print(f"{Colors.GREEN}Excellent! You earned {reward} chips.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Text entered incorrectly, no chips awarded.{Colors.RESET}")
    
    elif job_type == "math":
        # Generate math problem
        difficulty = random.randint(1,3)  # 1 - easy, 2 - medium, 3 - hard
        if difficulty == 1:
            a,b = random.randint(1,620), random.randint(1,420)
            answer = a + b
            print(f"What is {a} + {b}?")
        elif difficulty == 2:
            a,b = random.randint(10,150), random.randint(1, 90)
            answer = a*b
            print(f"What is {a}*{b} - ? (find the number for whole result)")
        else:
            a,b,c,d = random.randint(10,100), random.randint(5,60), random.randint(1,120), random.randint(1,60)
            answer = (a*b + c*d)
            print(f"Hard problem: ({a}*{b}) + ({c}*{d}) - ?")
        
        attempt = input_int("Answer: ")
        if attempt == answer:
            reward = random.randint(5, 15)
            casino.add_chips(reward)
            print(f"{Colors.GREEN}Correct! You earned {reward} chips.{Colors.RESET}")
        else:
            print(f"{Colors.RED}Wrong. Correct answer: {answer}. No chips awarded.{Colors.RESET}")

# -----------------------
# Helper functions
# -----------------------
def press_enter_to_continue():
    input("\nPress Enter to continue...")


def load_collection():
    if not os.path.exists(COLLECTION_FILE):
        return set()
    with open(COLLECTION_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_collection(collection):
    with open(COLLECTION_FILE, "w", encoding="utf-8") as f:
        for item in sorted(collection):
            f.write(item + "\n")

def load_boost():
    try:
        if os.path.exists(BOOST_FILE):
            with open(BOOST_FILE, "r") as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def save_boost(val):
    with open(BOOST_FILE, "w") as f:
        f.write(str(val))

# -----------------------
# Chests, artifacts, collection
# -----------------------

CHEST_PRICE = 250
BOOST_PRICE = 600   # +10% to legendary (one-time)
LEGENDARY_BASE_CHANCE = 5   # %
EPIC_CHANCE = 15            # %
RARE_CHANCE = 30            # %
COMMON_CHANCE = 50          # %

ARTIFACTS = {
    "COMMON": [
        "Lucky Talisman", "Old Amulet", "Rusty Coin",
        "Cracked Stone", "Raven Feather", "Piece of Amber"
    ],
    "RARE": [
        "Silver Cube", "Blade of Wind",
        "Guardian's Eye", "Harmony Crystal"
    ],
    "EPIC": [
        "Titan's Seal", "Blazing Sphere",
        "Fracture Sphere", "Song of Storm"
    ],
    "LEGENDARY": [
        "Heart of Ancient", "Crown of Infinity",
        "Key of Absolute Zero", "Fragment of Creator"
    ]
}

def open_chest(casino: Casino, collection: set, boost_value: int):
    if casino.balance < CHEST_PRICE:
        print(f"{Colors.RED}Not enough chips! Need {CHEST_PRICE}.{Colors.RESET}")
        return boost_value

    casino.remove_chips(CHEST_PRICE)

    # chances
    legendary_chance = LEGENDARY_BASE_CHANCE + boost_value
    boost_value = 0  # boost is one-time

    roll = random.randint(1, 100)

    if roll <= legendary_chance:
        rarity = "LEGENDARY"
    elif roll <= legendary_chance + EPIC_CHANCE:
        rarity = "EPIC"
    elif roll <= legendary_chance + EPIC_CHANCE + RARE_CHANCE:
        rarity = "RARE"
    else:
        rarity = "COMMON"

    item = random.choice(ARTIFACTS[rarity])
    new = item not in collection
    collection.add(item)

    print(f"\nYou got an item: {Colors.BOLD}{item}{Colors.RESET}")
    print(f"Rarity: {Colors.YELLOW}{rarity}{Colors.RESET}")

    if new:
        print(f"{Colors.GREEN}New item in collection!{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}You already have this item.{Colors.RESET}")

    save_collection(collection)
    save_boost(boost_value)

    return boost_value

def chest_menu(casino: Casino):
    while True:  # <-- Menu now works until exit
        clear()
        print(f"{Colors.MAGENTA}{Colors.BOLD}=== CHESTS AND COLLECTION ==={Colors.RESET}\n")

        collection = load_collection()
        boost_value = load_boost()

        print(f"Items in collection: {len(collection)}")
        print(f"One-time boost for legendary: {boost_value}%")
        print(f"Chest price: {CHEST_PRICE} chips")
        print(f"Boost price +10%: {BOOST_PRICE} chips\n")

        print("1 - Open chest")
        print("2 - Buy +10% legendary boost (one-time)")
        print("3 - Show collection")
        print("Empty input - go back")

        choice = input("\nChoose action: ").strip()

        if choice == "":
            # exit chest menu
            return

        elif choice == "1":
            boost_value = open_chest(casino, collection, boost_value)
            press_enter_to_continue()

        elif choice == "2":
            if casino.balance < BOOST_PRICE:
                print(f"{Colors.RED}Not enough chips!{Colors.RESET}")
            else:
                casino.remove_chips(BOOST_PRICE)
                boost_value += 10
                save_boost(boost_value)
                print(f"{Colors.GREEN}Boost purchased! Legendary chance now: +{boost_value}%{Colors.RESET}")
            press_enter_to_continue()

        elif choice == "3":
            if not collection:
                print("Collection is empty.")
            else:
                print("\nYour items:")
                for item in sorted(collection):
                    print(f"- {item}")
            press_enter_to_continue()

        else:
            print("Unknown command.")
            press_enter_to_continue()


# -----------------------
# Main menu
# -----------------------
def main_menu():
    casino = Casino(start_balance=1000)
    try:
        while True:
            clear()
            print(f"{Colors.BOLD}{Colors.CYAN}=== PYTHON CASINO ==={Colors.RESET}\n")
            casino.show_balance()
            print("\nAvailable options:")
            print("1 - Slots 🎰")
            print("2 - Roulette 🎡")
            print("3 - Work 💼")
            print("4 - Load balance from file")
            print("5 - Save and exit")
            print("6 - Exit without saving")
            print("7 - Chests and collection 📦")

            choice = input("\nChoose option: ").strip()

            if choice == "1":
                play_slots(casino)
                press_enter_to_continue()
            elif choice == "2":
                play_roulette(casino)
                press_enter_to_continue()
            elif choice == "3":
                work_job(casino)
                press_enter_to_continue() 
            elif choice == "4":
                # Reload balance from file (if exists)
                if os.path.exists(BALANCE_FILE):
                    casino.balance = load_balance(casino.balance)
                    print(f"{Colors.GREEN}Balance loaded from {BALANCE_FILE}.{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}File {BALANCE_FILE} not found.{Colors.RESET}")
                press_enter_to_continue()
            elif choice == "5":
                save_balance(casino.balance)
                print(f"{Colors.GREEN}Balance saved to {BALANCE_FILE}. Goodbye!{Colors.RESET}")
                break
            elif choice == "6":
                confirm = input("Exit without saving? (y/N): ").lower()
                if confirm == "y":
                    print("Exit without saving. Goodbye!")
                    break
                else:
                    print("Cancelled.")
                    press_enter_to_continue()
            elif choice == "7":
                chest_menu(casino)
            else:
                print(f"{Colors.RED}Invalid choice. Try again.{Colors.RESET}")
                time.sleep(0.7)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")

# -----------------------
# Entry point
# -----------------------
if __name__ == "__main__":
    main_menu()
