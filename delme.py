import re

def format_motion_commands(command:str):
    pattern = re.compile(r'(?P<x>x-?\d+(\.\d+)?|X-?\d+(\.\d+)?|)?(?P<y>y-?\d+(\.\d+)?|Y-?\d+(\.\d+)?|)?(?P<z>z-?\d+(\.\d+)?|Z-?\d+(\.\d+)?|)?')
    match = pattern.fullmatch(command)
    if not match:
        return None

    match_dict = {}
    for key, value in match.groupdict().items():
        if value == '':
            match_dict[key] = '0'.format(key.lower())
        else:
            match_dict[key] = value[1:]
    
    motion_commands = 'xyz {} {} {}'.format(match_dict['x'], match_dict['y'], match_dict['z'])

    return motion_commands
    
while True:
    teststring = input("Enter a motion command: ")
    teststring = teststring.strip().lower()
    output = format_motion_commands(teststring)
    if output:
        # print(output.groupdict())
        print(output)
    else:
        print("Invalid command")

