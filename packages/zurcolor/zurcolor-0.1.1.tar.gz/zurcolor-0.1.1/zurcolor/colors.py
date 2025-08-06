def red(text: str) -> str:
    return f"\033[31m{text}\033[0m"

def green(text: str) -> str:
    return f"\033[32m{text}\033[0m"

def yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"

def blue(text: str) -> str:
    return f"\033[34m{text}\033[0m"

def black(text: str) -> str:
    return f"\033[30m{text}\033[0m"

def white(text: str) -> str:
    return f"\033[37m{text}\033[0m"

def purple(text: str) -> str:
    return f"\033[35m{text}\033[0m"

def cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m"

def red_bg(text: str) -> str:
    return f"\033[41m{text}\033[0m"

def green_bg(text: str) -> str:
    return f"\033[42m{text}\033[0m"

def yellow_bg(text: str) -> str:
    return f"\033[43m{text}\033[0m"

def blue_bg(text: str) -> str:
    return f"\033[44m{text}\033[0m"

def purple_bg(text: str) -> str:
    return f"\033[45m{text}\033[0m"

def cyan_bg(text: str) -> str:
    return f"\033[46m{text}\033[0m"

def white_bg(text: str) -> str:
    return f"\033[47m{text}\033[0m"

def bright(text: str) -> str:
    return f"\033[1m{text}\033[0m"

def dark(text: str) -> str:
    return f"\033[2m{text}\033[0m"

def italic(text: str) -> str:
    return f"\033[3m{text}\033[0m"

def underline(text: str) -> str:
    return f"\033[4m{text}\033[0m"

def blink(text: str) -> str:
    return f"\033[6m{text}\033[0m"

def invert(text: str) -> str:
    return f"\033[7m{text}\033[0m"

def pink(text: str) -> str:
    return f"\033[95m{text}\033[0m"

def pink_bg(text: str) -> str:
    return f"\033[105m{text}\033[0m"

def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"