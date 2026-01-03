import os, sys
import colorama

EXE_EXT = ""
if sys.platform == "win32":
    colorama.just_fix_windows_console()
    EXE_EXT = ".exe"

class g:
    FILE = ""
    COMPILE_DATA = {
        "cc": "",
        "ld": "",
        "out": "",
        "in": "",

        "modules": {},
        "macros": {}
    }
    TO_BUILD = []
    BUILT_FILES = []
    OUT_FILES = []
    ERROR = False

def ERR(m):
    print(f"{colorama.Fore.RED}{m}{colorama.Style.RESET_ALL}")
    sys.exit(0);

def module_exists(module_name):
    return os.path.isdir(f"modules/{module_name}")

def get_modules():
    return [i for i in os.listdir("modules") if os.path.isdir(f"modules/{i}")]

def get_file_in_module(module):
    files = []
    for entry in os.listdir(f"modules/{module}"):
        if os.path.isfile(f"modules/{module}/{entry}") and entry.endswith(g.COMPILE_DATA["in"].strip()):
            files.append(entry)
        
        # TODO add folders

    return files

def convert_source_to_out(source): # source = module/file
    return source.replace("/", " ")

def build_file(file):
    if not os.path.isfile(f"modules/{file}"):
        ERR(f"File('{a}') does not exist.")

    if file not in g.BUILT_FILES:
        print(f"building: {file}")

        module = file[:file.index('/')]
        outfile = file.removesuffix(g.COMPILE_DATA['in'])
        outfile = outfile.replace('/', ' ').replace('\\', ' ')

        out = f"build/m_{module} {outfile}.o"
        args = g.COMPILE_DATA['modules'][module]['do'].replace('$I', f'\"modules/{file}\"').replace('$O', f'\"{out}\"')
        command = f"{g.COMPILE_DATA['cc']} {args}"

        print(command)
        output = os.system(command)

        if output != 0:
            g.ERROR = True
        else:
            g.BUILT_FILES.append(file)
            g.OUT_FILES.append(f'\"{out}\"')

def link():
    out = g.COMPILE_DATA['out']
    args = g.COMPILE_DATA['ld'][1].replace('$I', " ".join(g.OUT_FILES)).replace('$O', f'\"{out}\"')
    command = f"{g.COMPILE_DATA['ld'][0]} {args}"

    print(f"{colorama.Fore.CYAN}[LINK]{colorama.Style.RESET_ALL}")
    print(command)
    output = os.system(command)

    if output != 0:
        ERR("[LINK] failure")

try:
    g.FILE = [i.strip() for i in open("buildfile", "r").read().split("\n")]
except:
    ERR("No buildfile found.")

if not os.path.isdir("modules"):
    ERR("No modules directory.")
if not os.path.isdir("build"):
    ERR("No build directory.")

if len(sys.argv) > 1:
    g.TO_BUILD = sys.argv[1:]

    for a in g.TO_BUILD:
        if a == "*":
            continue

        if a in get_modules():
            continue

        found = False
        for mod in get_modules():
            files = get_file_in_module(mod)
            if a in [f"{mod}/{file}" for file in files]:
                found = True
                break
        
        if not found:
            ERR(f"File('{a}') does not exist.")

for index, instruction in enumerate(g.FILE):
    line = index + 1
    line_str = str(instruction)
    instruction = instruction.split()

    for index2, i in enumerate(list(instruction)):
        if ";" in i:
            instruction = instruction[:index2] + [i[:i.index(';')]]

    instruction = [i for i in instruction if i != '']

    if len(instruction) == 0:
        continue

    if len(instruction) <= 1:
        ERR(f"buildfile:{line}: directive expects >=1 arguments, got {len(instruction) - 1}.")

    if instruction[0] == "?cc":
        if len(instruction) != 2:
            ERR(f"buildfile:{line}: directive expects ==1 arguments, got {len(instruction) - 1}.")

        g.COMPILE_DATA["cc"] = instruction[1]

    elif instruction[0] == "?ld":
        if len(instruction) < 2:
            ERR(f"buildfile:{line}: directive expects >= 2 arguments, got {len(instruction) - 1}.")

        linker, do = instruction[1], " ".join(instruction[2:])
        prev_do = str(do)

        while "$" in do.replace("$I", "").replace("$O", ""):
            for m in g.COMPILE_DATA["macros"].keys():
                do = do.replace(f"${m}", g.COMPILE_DATA["macros"][m]['macro'])
            
            if "$" in do.replace("$I", "").replace("$O", "") and prev_do == do:
                ERR(f"buildfile:{line}: linker config contains an undefined or recursive macro.")

            prev_do = str(do)

        g.COMPILE_DATA["ld"] = [linker, do]

    elif instruction[0] == "?in":
        if len(instruction) != 2:
            ERR(f"buildfile:{line}: directive expects ==1 arguments, got {len(instruction) - 1}.")

        g.COMPILE_DATA["in"] = instruction[1]

    elif instruction[0] == "?out":
        if len(instruction) != 2:
            ERR(f"buildfile:{line}: directive expects ==1 arguments, got {len(instruction) - 1}.")

        g.COMPILE_DATA["out"] = instruction[1]

    elif instruction[0] == "?macro":
        if len(instruction) < 3:
            ERR(f"buildfile:{line}: directive expects >=3 arguments, got {len(instruction) - 1}.")
        
        name, macro = instruction[1], " ".join(instruction[2:])
        if name in g.COMPILE_DATA["macros"].keys():
            ERR(f"buildfile:{line}: macro '{name}' redefinition, previously defined in buildfile:{g.COMPILE_DATA['macros'][name]['line']}.")

        g.COMPILE_DATA["macros"][name] = {"line": line, "macro": macro}

    elif module_exists(instruction[0]):
        if len(instruction) < 2:
            ERR(f"buildfile:{line}: directive expects >=2 arguments, got {len(instruction) - 1}.")
        
        name, do = instruction[0], " ".join(instruction[1:])
        if name in g.COMPILE_DATA["modules"].keys():
            ERR(f"buildfile:{line}: module config '{name}' redefinition, previously defined in buildfile:{g.COMPILE_DATA['modules'][name]['line']}.")

        prev_do = str(do)

        while "$" in do.replace("$I", "").replace("$O", ""):
            for m in g.COMPILE_DATA["macros"].keys():
                do = do.replace(f"${m}", g.COMPILE_DATA["macros"][m]['macro'])
            
            if "$" in do.replace("$I", "").replace("$O", "") and prev_do == do:
                ERR(f"buildfile:{line}: module config '{name}' contains an undefined or recursive macro.")

            prev_do = str(do)

        g.COMPILE_DATA["modules"][name] = {"line": line, "do": do}

    else:
        ERR(f"buildfile:{line}: invalid instruction '{instruction[0]}'.")

for module in get_modules():
    if module not in g.COMPILE_DATA["modules"].keys():
        ERR(f"buildfile: no definition for module '{module}' found.")

for field in g.COMPILE_DATA.keys():
    if g.COMPILE_DATA[field] == "":
        ERR(f"buildfile: no definition for field '{field}' found.")

for a in g.TO_BUILD:
    if a == "*":
        print(f"{colorama.Fore.CYAN}[BUILD] *{colorama.Style.RESET_ALL}")
        files = []
        for mod in get_modules():
            files += [f"{mod}/{f}" for f in get_file_in_module(mod)]

        for file in files:
            build_file(file)

        continue

    print(f"{colorama.Fore.CYAN}[BUILD] {a}{colorama.Style.RESET_ALL}")

    if a in get_modules():
        files = get_file_in_module(a)
        for file in files:
            build_file(f"{a}/{file}")
    else:
        build_file(f"{a}")

if not g.ERROR:
    g.OUT_FILES = [f"\"build/{i}\"" for i in os.listdir("build")]
    link()

else:
    ERR("[BUILD] failure")