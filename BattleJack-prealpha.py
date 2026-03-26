# Jackson Hinks - MAR/26/2026 - Battle-Jack Pre-Alpha
# This is a very early prototype of a game idea I had where you are a blackjack chip in the center of the table,
# and you have to collect orbiting cards to build a blackjack hand, while also shooting lasers to destroy cards you don't want.
# The dealer is just a random target number from 15-21, so there is no actual dealer hand, but the player can win by beating that number without going over 21.
# Since this is my first time really creating a game using Python and Tkinter, I did have assistance from ChatGPT to help with the code stucture and my overall understanding of how to code a game.
# Other places I recieved help was from: Youtube, online forums, and the official Python documentation.

import tkinter as tk
import random
import math

# Basic blackjack card setup
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
values = {
    "A": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10
}

# Window setup
WIDTH = 900
HEIGHT = 600
center_x = WIDTH // 2
center_y = HEIGHT // 2

root = tk.Tk()
root.title("Battle-Jack")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

# Main game values
chip_radius = 35
player_angle = 270

player_money = 100
dealer_number = random.randint(15, 21)

player_hand = []
cards_on_screen = []
lasers = []

spawn_timer = 0
message = ""

# Extra little functions that are not really needed
def random_num():
    return random.randint(1, 10)

def weird_math(a, b):
    return (a + b) * 1

def old_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# This figures out the blackjack total of whatever hand gets passed into it.
# It uses the "values" dictionary up above to look up how much each card is worth.
# It also has the ace fixing logic, so if the total goes over 21 and there are aces,
# it turns one or more aces from 11 into 1 by subtracting 10 each time.
def get_hand_total(hand):
    total = 0
    aces = 0

    for card in hand:
        total += values[card]
        if card == "A":
            aces += 1

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total

# This starts a fresh round, but not a full game reset.
# So the player's money stays the same, but:
# - the hand gets cleared
# - the dealer gets a new random target number from 15-21
# - all cards and lasers on screen get wiped
# - the spawn timer resets
# Then it calls spawn_card() 5 times so the screen is not empty when the next round starts.
def reset_round():
    global player_hand, dealer_number, cards_on_screen, lasers, spawn_timer

    player_hand = []
    dealer_number = random.randint(15, 21)
    cards_on_screen = []
    lasers = []
    spawn_timer = 0

    for i in range(5):
        spawn_card()

# This makes one orbiting card.
# The rank is picked randomly from the blackjack ranks list.
# The angle is a random starting angle in radians, because math.cos() and math.sin()
# use radians instead of degrees.
# "distance" is how far away from the center the card starts.
# "turn_speed" controls how fast it rotates around the chip.
# "move_speed" controls how fast it slowly moves inward.
def make_card():
    card = {
        "rank": random.choice(ranks),
        "angle": random.uniform(0, 6.28),
        "distance": random.randint(220, 300),
        "turn_speed": random.uniform(0.01, 0.03),
        "move_speed": random.uniform(0.4, 0.8)
    }
    return card

# This just adds a new card to the screen if there are not too many already.
# It calls make_card() to build the dictionary for that card first.
def spawn_card():
    if len(cards_on_screen) < 8:
        cards_on_screen.append(make_card())

# Rotate the chip left
def turn_left(event=None):
    global player_angle
    player_angle -= 10

# Rotate the chip right
def turn_right(event=None):
    global player_angle
    player_angle += 10

# This shoots one laser in whatever direction the chip is currently facing.
# math.radians() converts the player's angle from degrees into radians,
# because cos() and sin() need radians.
# cos(angle) gives the horizontal direction, and sin(angle) gives the vertical direction.
# Those get used twice:
# 1. to place the laser starting point at the front of the chip
# 2. to set dx and dy so the laser actually moves that direction each frame
def shoot(event=None):
    angle = math.radians(player_angle)

    laser = {
        "x": center_x + math.cos(angle) * chip_radius,
        "y": center_y + math.sin(angle) * chip_radius,
        "dx": math.cos(angle) * 14,
        "dy": math.sin(angle) * 14,
        "life": 45
    }

    lasers.append(laser)

# This is the full restart.
# Unlike reset_round(), this one also resets the player's money and chip angle.
# Then it calls reset_round() to rebuild the actual round stuff.
def restart_game(event=None):
    global player_money, player_angle, message

    player_money = 100
    player_angle = 270
    message = ""
    reset_round()

# This checks the player's current blackjack total and decides what happens next.
# It calls get_hand_total() to get the total from the current hand.
#
# If the player goes over 21, it is a bust:
# - message changes
# - round resets
#
# If the player beats the dealer number without going over 21:
# - they win money based on their hand total
# - message changes
# - round resets
#
# Right now the dealer is just a random target number, so this function does not compare
# against an actual dealer hand, only dealer_number.
def check_hand():
    global player_money, message

    total = get_hand_total(player_hand)

    if total > 21:
        message = "Bust - new round"
        reset_round()
    elif total > dealer_number:
        gain = total * 100
        player_money += gain
        message = "You win! +" + str(gain)
        reset_round()

# This is the main update function for the game.
# It gets called over and over by game_loop().
#
# Main things it does:
# 1. handles card spawning with the timer
# 2. moves lasers
# 3. moves cards in a circular pattern inward
# 4. checks if a card touched the chip
# 5. checks if a laser hit a card
#
# Important math in here:
# - math.cos() and math.sin() are used to turn each card's angle + distance
#   into an actual x and y screen position
# - math.hypot() is used to get the distance from the card to the center chip,
#   which is how the game checks if the player collected the card
#
# It also calls check_hand() whenever the player collects a card, because that can
# instantly cause a win or a bust.
def update_game():
    global spawn_timer, cards_on_screen, lasers

    # Spawn cards every so often instead of all at once
    spawn_timer += 1
    if spawn_timer >= 40:
        spawn_timer = 0
        spawn_card()

    # Move all lasers forward based on dx and dy
    # life counts down so lasers disappear after a bit
    new_lasers = []
    for laser in lasers:
        laser["x"] += laser["dx"]
        laser["y"] += laser["dy"]
        laser["life"] -= 1

        if 0 <= laser["x"] <= WIDTH and 0 <= laser["y"] <= HEIGHT and laser["life"] > 0:
            new_lasers.append(laser)

    lasers = new_lasers

    # Move cards and check for hits/collisions
    remaining_cards = []

    for card in cards_on_screen:
        # This updates the card's angle and distance every frame,
        # which makes it circle around the chip while also moving inward
        card["angle"] += card["turn_speed"]
        card["distance"] -= card["move_speed"]

        # Convert the card's circular movement into real x/y screen coordinates
        x = center_x + math.cos(card["angle"]) * card["distance"]
        y = center_y + math.sin(card["angle"]) * card["distance"]

        # This checks how far the card is from the center chip
        # math.hypot() is basically distance formula
        distance_to_center = math.hypot(x - center_x, y - center_y)

        # If the card reaches the chip, the player collects it
        if distance_to_center <= chip_radius:
            player_hand.append(card["rank"])
            check_hand()
        else:
            got_shot = False

            # Check if any laser touches the card's hitbox
            # This is a simple box hit check, not perfect collision math
            for laser in lasers:
                if (x - 20 <= laser["x"] <= x + 20) and (y - 28 <= laser["y"] <= y + 28):
                    laser["life"] = 0
                    got_shot = True
                    break

            # If the card did not get collected or shot, keep it on screen
            if not got_shot:
                remaining_cards.append(card)

    cards_on_screen = remaining_cards

    # One more cleanup pass for lasers that got set to 0 life in collision checks
    lasers = [laser for laser in lasers if laser["life"] > 0]

# This draws everything fresh each frame.
# It starts with canvas.delete("all"), which clears the old frame.
# Then it redraws:
# - the text/UI
# - the orbiting cards
# - the lasers
# - the center chip
# - the direction line
#
# It also calls get_hand_total() so the current player total can be shown on screen.
# The card and laser positions use the same circular math as update_game():
# cos(angle) for x and sin(angle) for y.
def draw_game():
    canvas.delete("all")

    player_total = get_hand_total(player_hand)

    # Top info
    canvas.create_text(
        20, 20,
        anchor="nw",
        text="Money: $" + str(player_money),
        fill="white",
        font=("Arial", 18, "bold")
    )

    canvas.create_text(
        WIDTH // 2, 20,
        text="Battle-Jack (pre-alpha)",
        fill="white",
        font=("Arial", 22, "bold")
    )

    canvas.create_text(
        WIDTH - 20, 20,
        anchor="ne",
        text="Dealer Number: " + str(dealer_number),
        fill="white",
        font=("Arial", 18, "bold")
    )

    # Bottom hand info
    canvas.create_text(
        WIDTH // 2, HEIGHT - 25,
        text="Player Total: " + str(player_total) + "    Hand: " + " ".join(player_hand),
        fill="white",
        font=("Arial", 14)
    )

    # Controls
    canvas.create_text(
        20, HEIGHT - 20,
        anchor="sw",
        text="A / D = Rotate   Space = Shoot   R = Full Restart",
        fill="white",
        font=("Arial", 12)
    )

    # Small message at the top
    if message != "":
        canvas.create_text(
            WIDTH // 2, 50,
            text=message,
            fill="white",
            font=("Arial", 14, "bold")
        )

    # Draw the orbiting cards
    for card in cards_on_screen:
        x = center_x + math.cos(card["angle"]) * card["distance"]
        y = center_y + math.sin(card["angle"]) * card["distance"]

        canvas.create_rectangle(
            x - 20, y - 28, x + 20, y + 28,
            fill="white", outline="white", width=2
        )
        canvas.create_text(
            x, y,
            text=card["rank"],
            fill="black",
            font=("Arial", 16, "bold")
        )

    # Draw lasers
    for laser in lasers:
        canvas.create_line(
            laser["x"], laser["y"],
            laser["x"] - laser["dx"] * 0.8,
            laser["y"] - laser["dy"] * 0.8,
            fill="white",
            width=3
        )

    # Draw the chip in the center
    canvas.create_oval(
        center_x - chip_radius, center_y - chip_radius,
        center_x + chip_radius, center_y + chip_radius,
        fill="black", outline="white", width=3
    )

    canvas.create_oval(
        center_x - 20, center_y - 20,
        center_x + 20, center_y + 20,
        fill="gray30", outline="white", width=2
    )

    canvas.create_oval(
        center_x - 6, center_y - 6,
        center_x + 6, center_y + 6,
        fill="white", outline="white"
    )

    # Draw the aiming line based on the chip angle
    # Again this uses radians + cos/sin to point outward from the center
    angle = math.radians(player_angle)
    line_x = center_x + math.cos(angle) * (chip_radius + 14)
    line_y = center_y + math.sin(angle) * (chip_radius + 14)

    canvas.create_line(
        center_x, center_y,
        line_x, line_y,
        fill="white",
        width=4
    )

# This is the Tkinter game loop.
# It calls update_game() first so positions and logic change,
# then draw_game() so the new frame gets shown,
# then root.after(30, game_loop) tells Tkinter to call this again about 30 ms later.
# That is what keeps the game running without using a normal while loop.
def game_loop():
    update_game()
    draw_game()
    root.after(30, game_loop)

# Start the first round
reset_round()

root.bind("a", turn_left)
root.bind("d", turn_right)
root.bind("<space>", shoot)
root.bind("r", restart_game)

game_loop()
root.mainloop()