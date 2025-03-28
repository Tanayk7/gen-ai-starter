# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
# print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')

def gprint(string: str):
    print('\n\x1b[6;30;42m' + string + '\x1b[0m\n')

def yprint(string: str):
    print('\n\x1b[6;30;43m' + string + '\x1b[0m\n')