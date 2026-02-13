import random

WORDS = [
    "apple","about","other","which","there","their","world","music","light","sight",
    "night","right","thing","could","would","sweet","spice","stone","grass","water",
    "river","ocean","shore","earth","storm","cloud","above","below","after","again",
    "house","heart","dream","peace","power","speed","quick","laugh","smile","happy",
    "angry","brave","crazy","smart","sharp","blunt","bring","check","close",
    "catch","carry","clean","clear","climb","count","cover","dance","drink","drive",
    "eager","early","enter","every","enemy","error","equal","faith","fancy","fault",
    "fever","field","final","first","floor","flame","fresh","front","frost","fruit",
    "giant","globe","glory","grace","great","green","group","guard","guess","guide",
    "habit","happy","harsh","hatey","heavy","honey","honor","human","humor","ideal",
    "image","issue","ivory","jelly","judge","juice","jumpy","karma","knife","known",
    "label","laser","later","laugh","learn","leave","level","light","limit","local",
    "logic","loner","loose","lucky","magic","major","match","metal","miner","model",
    "month","moral","mouse","movie","music","nasty","never","night","noble","noise",
    "oasis","occur","offer","often","order","other","outer","paint","panel","paper",
    "party","peace","phase","phone","photo","piece","pilot","place","plain","plane",
    "plant","plate","point","power","press","price","pride","print","prove","punch",
    "queen","quick","quiet","radio","raise","reach","react","ready","realm","refer",
    "relax","reply","right","rival","river","robot","rough","round","route","royal",
    "ruler","salty","scale","scene","scope","score","scout","sense","serve","share",
    "sharp","sheep","sheet","shift","shine","shirt","shock","shoot","short","sight",
    "since","skill","sleep","slice","slide","small","smart","smoke","snake","solar",
    "sound","space","spare","speak","speed","spell","spice","spike","spine","spite",
    "sport","stage","stamp","stand","steam","steel","stone","store","storm","story",
    "straw","style","sugar","sunny","super","sweet","swift","sword","table","taste",
    "teach","teeth","thank","theme","there","thick","thief","thing","think","third",
    "those","three","throw","tight","tiger","timer","title","today","topic","torch",
    "total","touch","tower","track","trade","train","treat","trend","trial","tribe",
    "trick","trust","truth","twice","uncle","union","until","upper","upset",
    "urban","usual","vapor","value","vital","vivid","voice","voter","wagon","water",
    "weary","weird","whale","wheat","wheel","where","which","while","white","whole",
    "whose","woman","world","worry","worth","wound","write","wrong","yield","young",
    "youth","zebra","zeros","zones","winds","flock","crane","bliss","charm","flute",
    "ridge","flash","prism","amber","cabin","cargo","crown","demon","fable","forge",
    "glare","grind","hatch","ivory","jewel","linen","mimic","naval","nylon","orbit",
    "piano","quill","ranch","scrap","shear","tango","umbra","vocal","woven","xenon"
]

def color_letter(letter, color):
    colors = {
        "green": "\033[42m\033[30m",  
        "yellow": "\033[43m\033[30m", 
        "gray": "\033[100m\033[37m", 
        "reset": "\033[0m"
    }
    return f"{colors[color]} {letter.upper()} {colors['reset']}"

def compare_words(secret, guess):
    result = []
    secret_temp = list(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            result.append(("green", guess[i]))
            secret_temp[i] = None 
        else:
            result.append((None, guess[i]))

    for i in range(5):
        if result[i][0] is None:
            if guess[i] in secret_temp:
                result[i] = ("yellow", guess[i])
                secret_temp[secret_temp.index(guess[i])] = None
            else:
                result[i] = ("gray", guess[i])

    return result

def play():
    secret = random.choice(WORDS)
    attempts = 6

    print("Wordle!")
    print("6 attempts.\n")

    for attempt in range(1, attempts + 1):
        while True:
            guess = input().lower()
            if len(guess) == 5 and guess.isalpha():
                break
            print("Type a word with 5 letters.")

        result = compare_words(secret, guess)

        for color, letter in result:
            print(color_letter(letter, color), end=" ")
        print("")

        if guess == secret:
            print("Congrats! You guessed :", secret.upper())
            return

    print("You lose.")
    print("The word was:", secret.upper())

play()
