# pip3 install rocketchat_API
from requests import sessions
from rocketchat_API.rocketchat import RocketChat
from getpass import getpass
import time
from colorama import Fore, Style

class bcolors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

# Constant
host_msg = 'silo-host'  
client_msg = 'silo-client' 
silo_msg = 'silo-game'
host_online_msg = host_msg + ':online'  
host_offline_msg =  host_msg + ':offline' 
host_ingame_msg =  host_msg + ':in_game'
game_start_msg = silo_msg + ':start' 
game_stop_msg = silo_msg + ':stop'   
general_room_id = 'eK5mSKwR3WBoPwcTC' #General channel

base_checker = '#'
checker_filler = '0'

# Silo game constant 
TOTAL_COL = 6
INIT_ROW = 3
WIN_HEIGHT = (TOTAL_COL * INIT_ROW) // 2
silo_arr = []
silo_player_active = {}
silo_non_player_active = {}
checker_row_move = [] 

# default player  
player_checker = bcolors.RED + base_checker + bcolors.ENDC 
non_player_checker = bcolors.BLUE + base_checker + bcolors.ENDC 

def get_input_within_range(min, max, input_text):
    user_input = 0
    while True:
        try:
            user_input = int(input(input_text))
            if user_input < min or user_input > max:
                print("Input invalid! Please try again.")
            else:
                break
        except:
            print("Input invalid! Please try again.")
            
    return user_input
                       
def get_connection():
    while True:
        username = input("Input username: ")
        password = getpass("Input password: ")
        try:
            with sessions.Session() as session:
                rocket = RocketChat(username, password, server_url='https://cst330.cs.usm.my', session=session)
            break
        except:
            print("Problem in signing in! Please try again.")
    return rocket

def establish_connection_based_role(rocket, player_type):
    global player_checker, non_player_checker
    room_id = ''
    chat_obj = rocket.channels_history(room_id=general_room_id, count = 1).json()['messages'][0]
    me_username = rocket.me().json()['username']

    if player_type == 1:
        set_online = True
        print("Player is host.")
        if chat_obj['msg'] == host_online_msg:
            if chat_obj['u']['username'] == me_username:
                print("Host instance has been created!")
                print("Terminate the previous session to continue.")
            else:
                print("There is already host online! Cannot proceed to be host.")
                print("Terminating...")
            set_online = False

        if set_online:
            rocket.chat_post_message(host_online_msg, room_id=general_room_id).json()
            print(me_username+' is online!')
            print("Waiting for client to connect...")
            wait_client = True

            while wait_client:
                time.sleep(13)
                get_client = rocket.im_list().json()['ims']
                for ims in get_client:
                    # print(ims['lastMessage']['msg'])
                    if ims['lastMessage']['msg'] == game_start_msg:
                        wait_client = False
                        room_id = ims['_id']
                        break

            print('Game start')
            print('Room id: {}'.format(room_id))
            rocket.chat_post_message(host_ingame_msg, room_id=general_room_id).json()

    elif player_type == 2:
        print("Player is client.")
        player_checker = bcolors.BLUE + base_checker + bcolors.ENDC 
        non_player_checker = bcolors.RED + base_checker + bcolors.ENDC 

        if chat_obj['msg'] == host_online_msg:
            print('Host is online!')
            host_username = chat_obj['u']['username']
            print()
            
            print("Preparing room...")
            room_id = rocket.im_create(username=host_username).json()['room']['_id']

            print('Room id: {}'.format(room_id))
            rocket.chat_post_message(game_start_msg, room_id=room_id).json()['success']
            print('Game start!')

        elif chat_obj['msg'] == host_ingame_msg:
            print("Host currently in game!")
            print("Please try again later.")
        else:
            print('No host available!')
    return room_id

def first_checker_setup():
    global silo_arr
    row_num = INIT_ROW
    col_num = TOTAL_COL
    for i in range(row_num):
        temp_arr = []
        for j in range(col_num):
            if (j % 2 != 0):
                temp_arr.append(player_checker)
            else:
                temp_arr.append(non_player_checker)
        silo_arr.append(temp_arr) 

def get_checker_active():
    global silo_player_active, silo_non_player_active, silo_arr
    silo_player_active.clear()
    silo_non_player_active.clear()
    arr_row_len = len(silo_arr)
    arr_col_len = TOTAL_COL
    # Determine
    for i in range(arr_col_len):
        isFoundPlayer = False
        isFoundNotPlayer = False
        for j in reversed(range(arr_row_len)):
            if not silo_arr[j][i]: 
                continue
            if not isFoundPlayer and silo_arr[j][i] == player_checker:
                if i == TOTAL_COL - 1:
                    continue
                silo_player_active[str(i)] = j
                isFoundPlayer = True
            if not isFoundNotPlayer and silo_arr[j][i] == non_player_checker:
                if not i:
                    continue
                silo_non_player_active[str(i)] = j
                isFoundNotPlayer = True
            if isFoundPlayer and isFoundNotPlayer:
                break
    
def silo_print():
    print("\nGameboard:\n")
    for i in reversed(range(len(silo_arr))):
        for j in (range(len(silo_arr[0]))):
            elem = silo_arr[i][j]
            if elem==checker_filler:
                elem = ''
            print('', elem, end='\t')
        print('\n')
    for i in range(TOTAL_COL):
        print("({})".format(i+1), end='\t')
    print('\n\n')

def is_player_check_turn(turn_counter):
    is_player_turn = False
    if turn_counter % 2 == 0:
        is_player_turn = True
    return is_player_turn

def get_checker_move(col, start_row):
    global checker_row_move
    checker_row_move.clear()
    curr_row = start_row
    while True:
        try:
            temp = silo_arr[curr_row][col]
            if temp == checker_filler:
                break
            checker_row_move.append(curr_row)
            curr_row += 1
        except:
            break  

def checker_setup_update(move, turn_counter):
    global silo_arr
    is_player_update = 1
    if not is_player_check_turn(turn_counter):
        is_player_update *= -1 
    
    for move_row in checker_row_move:
        check_col = move
        check_row = move_row
        
        cell_occupied = True

        update_col = check_col + is_player_update
        for update_row in range(len(silo_arr)):
            if silo_arr[update_row][update_col] == checker_filler:
                cell_occupied = False
                silo_arr[update_row][update_col] = silo_arr[check_row][check_col]
                break

        if cell_occupied:
            add_arr_row = []
            for i in range (TOTAL_COL):
                add_arr_col = checker_filler
                if i == check_col + is_player_update:
                    add_arr_col = silo_arr[check_row][check_col]
                add_arr_row.append(add_arr_col)
            silo_arr.append(add_arr_row)

        silo_arr[check_row][check_col] = checker_filler
        get_checker_active()

def get_bot_move():
    print("Bot preparing for move ... ")
    # time.sleep(1)
    act_move = int(list(silo_non_player_active.keys())[0])
    move = act_move + 1
    target = move - 1 
    print("Chosen column '{}'".format(move))
    print("Moving {} <- {}...".format(target, move))
    # time.sleep(1)
    return act_move

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def get_player_move(active_list):
    flush_input()
    act_move = 0
    while True:
        try:
            print("Valid moves: ({})".format([int(val_move)+1 for val_move in list(active_list.keys())]))
            move = input("Make a valid move: ")
            if move == 'q':
                act_move = 'q'
                break
            move = int(move)
            act_move = move - 1
            target =  move + 1
            if str(act_move) not in (active_list.keys()):
                raise Exception
            print("Chosen column '{}'".format(move))
            print("Moving {} -> {}...".format(move, target))
            # time.sleep(1)
            break
        except:
            print("Input invalid! Please try again.")
        
    return act_move

def get_host_offline(rocket):
    rocket.chat_post_message(host_offline_msg, room_id=general_room_id).json()

def get_host_move(rocket, game_room_id):
    host_move = 0
    print('Waiting for host...')
    while True:
        time.sleep(12)
        history = rocket.im_history(room_id=game_room_id, count=1).json()['messages'][0]['msg']
        if history == game_stop_msg:
            print('The game has been stopped.')
            break
        history_game = history.split(':')
        if history_game[0] == host_msg:
            if history_game[1] == 'q':
                rocket.chat_post_message(game_stop_msg, room_id=game_room_id).json()
                print('Host has ended the game.')
                print('Thank you for playing!')
                break
            host_move = TOTAL_COL - int(history_game[1]) - 1
            print('Host move: {}'.format(host_move))
            break
    return host_move

def get_client_move(rocket, game_room_id):
    client_move = 0
    print('Waiting for client...')
    wait_for_client = True
    while wait_for_client:
        time.sleep(12)
        get_latest_msg = rocket.im_list().json()['ims']
        for ims in get_latest_msg:
            if ims['_id'] == game_room_id:
                latest_msg = ims['lastMessage']['msg']
                if latest_msg == game_stop_msg:
                    print('The game has been stopped.')
                    wait_for_client = False
                latest_msg = latest_msg.split(':')
                if latest_msg[0] == client_msg:
                    if latest_msg[1] == 'q':
                        rocket.chat_post_message(game_stop_msg, room_id=game_room_id).json()
                        print('Client has ended the game.')
                        print('Thank you for playing!')
                    else:
                        client_move = TOTAL_COL - int(latest_msg[1]) - 1
                        print('Client move: {}'.format(client_move))
                    wait_for_client = False
    return client_move
    
def pvp_send_move(rocket, game_room_id, player_type, active_list):
    isNotEnd = True
    base_msg = host_msg if player_type == 1 else client_msg
    move = get_player_move(active_list)
    send_move = base_msg + ':' + str(move)
    rocket.chat_post_message(send_move, room_id=game_room_id).json()
    if move == 'q':
        print('Game is stopped!')
        isNotEnd = False
    return (isNotEnd, move)

def silo_game_start():
    global silo_arr, silo_player_active, silo_non_player_active, checker_row_move

    # game variable
    game_room_id = ''
    player_type = 0
    turn_counter = 0
    isVictor = ''
    isGame = True

    print("Silo start!")
    input_text = "Please input game mode, (1) PVP (2) PVComp: "
    game_mode = get_input_within_range(1,2, input_text)
    if game_mode == 1:
        print('PVP mode has been selected!') 
        rocket = get_connection()
        input_text = "Please input player type, (1) Host (2) Client: "
        player_type = get_input_within_range(1,2, input_text)
        game_room_id = establish_connection_based_role(rocket, player_type)
    elif game_mode == 2:
        print('PVComp mode has been selected!')

    first_checker_setup()
    get_checker_active()

    while isGame:
        if game_mode == 1:
            if not game_room_id:
                break
        if not turn_counter:
            silo_print()
            if player_type == 2:
                print("Waiting for host to initiate...")
                turn_counter += 1

        isPlayer = is_player_check_turn(turn_counter)

        active_list = silo_player_active if isPlayer else silo_non_player_active
        print("Player turn ('{}')".format(player_checker) if isPlayer else "Opponent turn ('{}')".format(non_player_checker))

        isMove = False
        if active_list:
            if isPlayer:                
                if game_mode == 1:
                    isGame,move = pvp_send_move(rocket, game_room_id, player_type, active_list)
                    if not isGame:
                        break
                else:
                    move = get_player_move(active_list)
            else:
                if game_mode == 1:
                    if player_type == 2:
                        move = get_host_move(rocket, game_room_id)
                    else:
                        move = get_client_move(rocket, game_room_id) 

                    if not move:
                        isGame = False
                        break
                else:
                    move = get_bot_move()

            if move == 'q':
                print('The game has been stopped!')
                isGame = False
                break
            else:
                get_checker_move(move, active_list[str(move)])
                checker_setup_update(move, turn_counter)

            silo_print()
            turn_counter += 1
            isMove = True

        if not active_list:
            if isPlayer:
                list_lim = TOTAL_COL - 1
                win_text = 'Player win'
                win_checker = player_checker
            else:
                list_lim = 0
                win_text = 'Opponent win'
                win_checker = non_player_checker

            row = 0
            while True:
                try:
                    if silo_arr[row][list_lim] == win_checker:
                        row += 1
                    else:
                        break
                except:
                    break
            
            if row == WIN_HEIGHT:
                isGame = False
                print(win_text)
                isVictor = win_checker
            else:
                if not isMove:
                    print("No available move at the moment. Skipping turn...")
                    turn_counter += 1

    if isVictor == player_checker:
        print("Congratulation, you win!")
    elif isVictor == non_player_checker:
        if game_room_id:
            rocket.chat_post_message(game_stop_msg, room_id=game_room_id).json()
        print("You lose this time. Don't give up!")
        
                
    if game_room_id:
        if player_type == 1:
            get_host_offline(rocket)

    print("Silo game end.")

if __name__ == "__main__":
    silo_game_start()   