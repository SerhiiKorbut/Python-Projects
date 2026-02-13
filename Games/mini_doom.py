import os
import math
import time
import sys

# ================== Settings ==================
W, H = 100, 40
FOV = 0.66
MAX_DEPTH = 20.0
MOVE_SPEED = 2.8
ROT_SPEED = 2.2

# ================== Map ==================
world_map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,0,0,1,1,1,0,0,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,1,0,1,1,0,1,1,1,1,0,0,0,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

WALL_CHARS = " .,:;~=+*#$&%@█"[::-1]

# ================== Terminal ==================
if os.name == 'nt':
    os.system('cls')
    os.system(f'mode con: cols={W} lines={H+3}')
    import msvcrt
else:
    os.system('clear')
    sys.stdout.write(f"\x1b[8;{H+3};{W}t\x1b[?25l")
    import termios, tty, select

pos_x, pos_y = 1.5, 1.5
dir_x, dir_y = 1.0, 0.0
plane_x, plane_y = 0.0, FOV

# ================== Input ==================
def get_key():
    if os.name == 'nt':
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                second = msvcrt.getch()
                if ch == b'\xe0':
                    if second == b'H': return 'up'
                    if second == b'P': return 'down'
                    if second == b'M': return 'right'
                    if second == b'K': return 'left'
                return ''
            else:
                return ch.decode('utf-8', errors='ignore').lower()
        return ''
    else:
        import select, sys
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return ''

# ================== RAYCASTING ==================
def cast_rays():
    buffer = [[" " for _ in range(W)] for _ in range(H)]
    for x in range(W):
        camera_x = 2 * x / W - 1
        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(pos_x)
        map_y = int(pos_y)

        delta_dist_x = abs(1/ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1/ray_dir_y) if ray_dir_y != 0 else 1e30

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

        hit = False
        side = 0
        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            if map_x < 0 or map_x >= len(world_map[0]) or map_y < 0 or map_y >= len(world_map):
                break
            if world_map[map_y][map_x]:
                hit = True

        if hit:
            perp_dist = (side_dist_x - delta_dist_x) if side == 0 else (side_dist_y - delta_dist_y)
            if perp_dist < 0.1: perp_dist = 0.1
            line_h = int(H / perp_dist)
            draw_start = max(0, H//2 - line_h//2)
            draw_end = min(H-1, H//2 + line_h//2)

            shade = min(len(WALL_CHARS)-1, int(perp_dist))
            char = WALL_CHARS[shade]
            if side: char = char.lower()

            color = "\x1b[91m" if not side and perp_dist < 6 else "\x1b[31m" if not side else "\x1b[90m"
            reset = "\x1b[0m" if os.name != 'nt' else ""

            for y in range(draw_start, draw_end):
                buffer[y][x] = color + char + reset

    # FLoor and ceiling
    for y in range(H):
        for x in range(W):
            if buffer[y][x] == " ":
                buffer[y][x] = ("\x1b[44m \x1b[0m" if y < H//2 else "\x1b[42m \x1b[0m") if os.name != 'nt' else ("░" if y < H//2 else "▒")

    # Weapon test
    # gun = ["   ▄███▄   ", "   ▀███▀   "]
    # for i, c in enumerate(gun[int(time.time()*3)%2]):
    #   if 0 <= W//2 - 6 + i < W:
    #       buffer[H-4][W//2 - 6 + i] = c

    return buffer

# ================== Main Process ==================
print("ASCII DOOM | WASD + Q/E or arrows | ESC — exit")
time.sleep(2)

old_settings = None
if os.name != 'nt':
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

try:
    dt = 0.033
    while True:
        key = get_key()

        # Exit
        if key in ('\x1b', '\x03'):  # ESC or Ctrl+C
            break

        # Looking around
        rot = 0
        if key in ('e', 'right'): rot = ROT_SPEED * dt
        if key in ('q', 'left'):  rot = -ROT_SPEED * dt
        if rot:
            old_dir_x = dir_x
            dir_x = dir_x * math.cos(rot) - dir_y * math.sin(rot)
            dir_y = old_dir_x * math.sin(rot) + dir_y * math.cos(rot)
            old_plane_x = plane_x
            plane_x = plane_x * math.cos(rot) - plane_y * math.sin(rot)
            plane_y = old_plane_x * math.sin(rot) + plane_y * math.cos(rot)

        # Moving
        move = 0
        strafe = 0
        if key in ('w', 'up'): move = MOVE_SPEED * dt
        if key in ('s', 'down'): move = -MOVE_SPEED * dt
        if key == 'a': strafe = -MOVE_SPEED * dt
        if key == 'd': strafe = MOVE_SPEED * dt

        # Check collisions
        if move:
            nx = pos_x + dir_x * move
            ny = pos_y + dir_y * move
            if world_map[int(pos_y)][int(nx)] == 0:  # X
                pos_x = nx
            if world_map[int(ny)][int(pos_x)] == 0:  # Y
                pos_y = ny

        if strafe:
            nx = pos_x + dir_y * strafe
            ny = pos_y - dir_x * strafe
            if world_map[int(ny)][int(nx)] == 0:
                pos_x, pos_y = nx, ny


        # Drawing
        screen = cast_rays()
        print("\x1b[H" + "\n".join("".join(row) for row in screen))
        time.sleep(max(0, dt - 0.005))

finally:
    if os.name != 'nt' and old_settings:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write("\x1b[?25h\x1b[0m")
    print("\n\n..")