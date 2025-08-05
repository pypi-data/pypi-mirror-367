from sty import fg

colored = lambda c_code, o_str: fg(c_code) + o_str + fg.rs

RED_COLOR = 196
GREEN_COLOR = 46
YELLOW_COLOR = 190
PINK_COLOR = 200
CYAN_COLOR = 51
SUCCESS_NOTIF = colored(GREEN_COLOR, '[*]')
ACTION_NOTIF = colored(CYAN_COLOR, '[*]')
INFO_NOTIF = colored(YELLOW_COLOR, '[*]')
ERROR_NOTIF = colored(RED_COLOR, '[-]')