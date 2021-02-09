from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver import ActionChains
import time

pi = input('pi? [y / n]: ') == 'y'
noflag = input('use flags? [y / n]: ') == 'n'
level = int(input('level? '))
clickable = 'cell size24 hd_closed'
number = 'cell size24 hd_opened hd_type'
ticket = ' cell-ticket'
flag = 'cell size24 hd_closed hd_flag'
loose = 'top-area-face zoomable hd_top-area-face-lose'
wonwon = 'top-area-face zoomable hd_top-area-face-win'
wins = 0
losses = 0
total = 0
lastchance = 0
chances = 0
clicks = 0
mines = 0
width, height = 9, 9
if level == 2:
    width = 16
    height = 16
if level == 3:
    width = 30
    height = 16
if level == 4:
    width = int(input('width? '))
    height = int(input('height? '))
    mines = int(input('mines? '))

print(f'level: {level} ({width}x{height})')
driver = webdriver.Chrome()
# driver.set_window_size(1280, 720)
driver.get('https://minesweeper.online/')

# login
if pi:
    btn = driver.find_element_by_xpath('//*[@id="header"]/nav/div/div/button')
    btn.click()
    found = False
    while not found:
        found = True
        try:
            btn = driver.find_element_by_xpath('//*[@id="nav_link_sign_in"]/a')
        except:
            found = False
    btn.click()
else:
    btn = None
    found = False
    while not found:
        found = True
        try:
            btn = driver.find_element_by_xpath('//*[@id="header"]/div/div/div/button[2]')
            btn.click()
        except:
            found = False
found = False
while not found:
    found = True
    try:
        input = driver.find_element_by_xpath('//*[@id="sign_in_username"]')
        input.send_keys('gewuerz.nudel@gmail.com')
    except:
        found = False
input = driver.find_element_by_xpath('//*[@id="sign_in_password"]')
input.send_keys('raspberry')
found = False
while not found:
    found = True
    try:
        btn = driver.find_element_by_xpath('//*[@id="S66"]/div/div/form/div[3]/button[2]')
        btn.click()
    except:
        found = False
if level < 4:
    found = False
    while not found:
        found = True
        try:
            btn = driver.find_element_by_xpath(f'//*[@id="homepage"]/div[2]/div[{level}]/a/div')
            btn.click()
        except:
            found = False
else:  # custom game
    found = False
    while not found:
        found = True
        try:
            btn = driver.find_element_by_xpath('//*[@id="homepage"]/div[2]/div[1]/a/div')
            btn.click()
        except:
            found = False
    found = False
    while not found:
        found = True
        try:
            btn = driver.find_element_by_xpath('//*[@id="level_select_4"]/span')
            btn.click()
        except:
            found = False
    found = False
    while not found:
        found = True
        try:
            input = driver.find_element_by_xpath('//*[@id="custom_width"]')
            input.clear()
            input.send_keys(str(width))
        except:
            found = False
    input = driver.find_element_by_xpath('//*[@id="custom_height"]')
    input.clear()
    input.send_keys(str(height))
    input = driver.find_element_by_xpath('//*[@id="custom_mines"]')
    input.clear()
    input.send_keys(str(mines))
    btn = driver.find_element_by_xpath('//*[@id="C40_content"]/form/button')
    btn.click()

'''
-11 - -19: ignorieren
-1: leer, clickbar
0: leer
1 - 8: nummer
9: flag
10: mine
11: fehler
'''


def find_cells():
    while True:
        check = driver.find_elements_by_xpath('//*[@id="A43"]')
        if len(check) > 0:
            return [[check[0].find_element_by_id(f'cell_{x}_{y}') for x in range(width)] for y in range(height)]


def to_num(cells):
    field = [[-1 for i in range(width)] for j in range(height)]
    for y in range(height):
        for x in range(width):
            cell = cells[y][x].get_attribute('class')
            if str(cell).startswith(number):
                if str(cell).endswith(ticket):
                    field[y][x] = int(str(cell)[29:len(str(cell)) - len(ticket)])
                else:
                    field[y][x] = int(str(cell)[29:])
            elif str(cell) == flag:
                field[y][x] = 9
    return field


def add_num(local_field, posx, posy, searched):
    offsets = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    searched[posy][posx] = True
    for offset in offsets:
        x = posx + offset[0]
        y = posy + offset[1]
        if 0 <= x < width and 0 <= y < height:
            cell = cells[y][x].get_attribute('class')
            strcell = str(cell)
            if strcell.startswith(number):
                if str(cell).endswith(ticket):
                    local_field[y][x] = int(str(cell)[29:len(str(cell)) - len(ticket)])
                else:
                    local_field[y][x] = int(str(cell)[29:])
                if local_field[y][x] != -1 and (not searched[y][x]):
                    local_field, searched = add_num(local_field, x, y, searched)
    return local_field, searched


def right_click(x, y):
    global clicks, field
    if field[y][x] == -1:
        clicks += 1
        c = driver.find_element_by_id(f'cell_{x}_{y}')
        actions = ActionChains(driver)
        actions.context_click(c).perform()


def click(x, y):
    global losses, total, wins, field, cells, lastchance, clicks, chances
    if field[y][x] == -1:
        clicks += 1
        found = False
        while not found:
            found = True
            try:
                c = driver.find_element_by_id(f'cell_{x}_{y}')
            except NoSuchElementException:
                found = False
        oldclass = cells[y][x].get_attribute('class')
        c.click()
        cell = oldclass
        for i in range(10):
            cell = cells[y][x].get_attribute('class')
            if cell != oldclass:
                break
            time.sleep(.1)
        if str(cell).startswith(number):
            if str(cell).endswith(ticket):
                field[y][x] = int(str(cell)[29:len(str(cell)) - len(ticket)])
            else:
                field[y][x] = int(str(cell)[29:])
            if field[y][x] == 11:
                losses += 1
                total += 1
                print(f'[{total}] loose {wins}:{losses} ({lastchance}% | {chances} chances)')
                clicks = 0
                restart()
                time.sleep(1)
                return
            if field[y][x] == 0:
                s = [[False for x in range(width)] for y in range(height)]
                field, s = add_num(field, x, y, s)


def both_click(posx, posy):
    global field, clicks
    if 0 < field[posy][posx] < 9:
        clicks += 1
        found = False
        while not found:
            found = True
            try:
                c = driver.find_element_by_id(f'cell_{posx}_{posy}')
                c.click()
            except:
                found = False
        for y in range(posy - 1, posy + 2):
            for x in range(posx - 1, posx + 2):
                if 0 <= y < height and 0 <= x < width:
                    if field[y][x] == -1:
                        cell = cells[y][x].get_attribute('class')
                        while not str(cell).startswith(number):
                            cell = cells[y][x].get_attribute('class')
                        if str(cell).endswith(ticket):
                            field[y][x] = int(str(cell)[29:len(str(cell)) - len(ticket)])
                        else:
                            field[y][x] = int(str(cell)[29:])
                        if field[y][x] == 0:
                            s = [[False for x in range(width)] for y in range(height)]
                            field, s = add_num(field, x, y, s)


def restart():
    global field, cells, lastchance, chances, clicks
    lastchance = 0
    chances = 0
    clicks = 0
    field = [[-1 for x in range(width)] for y in range(height)]
    driver.find_element_by_xpath('//*[@id="top_area_face"]').click()
    time.sleep(.1)
    while True:
        click(width // 2, height // 2)
        if lost():
            restart()
        else:
            break


def lost():
    face = driver.find_element_by_xpath('//*[@id="top_area_face"]')
    return face.get_attribute('class') == loose


def won():
    face = driver.find_element_by_xpath('//*[@id="top_area_face"]')
    return face.get_attribute('class') == wonwon


def satisfied(posx, posy):
    mines = 0
    for y in range(posy - 1, posy + 2):
        for x in range(posx - 1, posx + 2):
            if 0 <= y < height and 0 <= x < width:
                if field[y][x] == 9:
                    mines += 1
    return mines == field[posy][posx]


def round_click(posx, posy):
    global field
    if noflag:
        clicked = False
        for y in range(posy - 1, posy + 2):
            for x in range(posx - 1, posx + 2):
                if 0 <= y < height and 0 <= x < width:
                    if field[y][x] == -1:
                        click(x, y)
                        clicked = True
        return clicked
    else:
        both_click(posx, posy)
        return True


def place_flags(posx, posy):
    clicked = False
    clear = 0
    for y in range(posy - 1, posy + 2):
        for x in range(posx - 1, posx + 2):
            if 0 <= y < height and 0 <= x < width:
                if field[y][x] == -1 or field[y][x] == 9:
                    clear += 1
    if field[posy][posx] == clear:
        for y in range(posy - 1, posy + 2):
            for x in range(posx - 1, posx + 2):
                if 0 <= y < height and 0 <= x < width:
                    if field[y][x] == -1:
                        if not noflag:
                            right_click(x, y)
                        field[y][x] = 9
                        clicked = True
    return clicked


def validate():
    vals = [[[] for x in range(width)] for y in range(height)]
    for y in range(height):
        for x in range(width):
            if 0 < field[y][x] < 9:
                flags = 0
                for yy in range(y - 1, y + 2):
                    for xx in range(x - 1, x + 2):
                        if 0 <= yy < height and 0 <= xx < width:
                            if field[yy][xx] == 9:
                                flags += 1
                clear = 0
                for yy in range(y - 1, y + 2):
                    for xx in range(x - 1, x + 2):
                        if 0 <= yy < height and 0 <= xx < width:
                            if field[yy][xx] == -1:
                                clear += 1
                if clear != 0:
                    num = (field[y][x] - flags) * 100 // clear
                    for yy in range(y - 1, y + 2):
                        for xx in range(x - 1, x + 2):
                            if 0 <= yy < height and 0 <= xx < width:
                                if field[yy][xx] == -1:
                                    vals[yy][xx].append(num)
    odds = [[100 for x in range(width)] for y in range(height)]
    for y in range(height):
        for x in range(width):
            if len(vals[y][x]) > 0:
                odd = 0
                for val in vals[y][x]:
                    odd += val
                odd = odd // len(vals[y][x])
                odds[y][x] = odd
    return odds


found = False
while not found:
    found = True
    try:
        cells = find_cells()
    except:
        found = False
field = [[-1 for x in range(width)] for y in range(height)]
while True:
    click(width // 2, height // 2)
    time.sleep(.1)
    if lost():
        restart()
    else:
        break

while True:
    # field = to_num(cells)
    placed = False
    # place flags
    for y in range(height):
        for x in range(width):
            if 0 < field[y][x] < 9:
                if place_flags(x, y):
                    placed = True

    # click empty
    for y in range(height):
        for x in range(width):
            if 0 < field[y][x] < 9:
                if satisfied(x, y):
                    round_click(x, y)
                    placed = True
    # update ignored tiles
    for y in range(height):
        for x in range(width):
            if -1 < field[y][x] < 9:
                ignore = True
                for yy in range(y - 1, y + 2):
                    for xx in range(x - 1, x + 2):
                        if 0 <= yy < height and 0 <= xx < width:
                            if field[yy][xx] == -1:
                                ignore = False
                if ignore:
                    field[y][x] = -field[y][x] - 10

    # click best hope
    if not placed:
        if won():
            wins += 1
            total += 1
            found = False
            string = 'BV3: -1'
            while not found:
                found = True
                try:
                    div = driver.find_element_by_xpath('//*[@id="R35"]/div[1]')
                    string = div.text
                except:
                    found = False
            i = string.index('3BV: ')
            j = string.index('\n', i + 5)
            print(f'[{total}] win {wins}:{losses} (effi: {clicks}:{string[i + 5:j]})')
            clicks = 0
            restart()
            continue
        values = validate()
        least = 100
        point = (-1, -1)
        for y in range(height):
            for x in range(width):
                if 0 < values[y][x] < least:
                    least = values[y][x]
                    point = (x, y)
        if point != (-1, -1):
            lastchance = least
            chances += 1
            click(point[0], point[1])
        else:
            found = False
            for y in range(height):
                for x in range(width):
                    if field[y][x] == -1:
                        click(x, y)
                        lastchance = least
                        chances += 1
                        found = True
                        break
                if found:
                    break

