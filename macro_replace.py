### call `python ./macro_replace` to translate a file at `./input.c`
### call `python ./macro_replace PATH.c` to translate a file at `PATH.c` 

import os
import sys
import time
import json

ast = {}            # Clang's AST
macros = {}         # macro definition information
# expansions = {}     # macro expansion trace

'''
Load in .c file
Defaults to input.c but you can pass in a different path
'''
fp = './input.c'
if (len(sys.argv) > 1):
    for arg in sys.argv:
        if (arg[-2:] == ".c"):
            fp = arg

'''
Generate wave trace and clang AST
'''
with open(fp, 'r+') as cfile:
    source = cfile.read()
    cfile.seek(0, 0)
    if (cfile.readline() != "#pragma wave trace(enable)\n"):
        cfile.seek(0, 0)
        cfile.write('#pragma wave trace(enable)\n' + source)
    os.system(f'wave -t {fp[:-1]}trace {fp} >/dev/null')
    os.system(f'clang -Xclang -ast-dump=json -fsyntax-only {fp} > {fp[:-1]}ast')
    cfile.close()
time.sleep(0.01) # idk if this is needed or not

'''
Loads in the AST of the last function (e.g. main)

Basically, this script only really works with single-function files
'''
with open(f'{fp[:-1]}ast', 'r') as afile:
    ast = json.load(afile)
    ast = ast['inner'][-1]['inner']
    afile.close()

def PrintDict(d):
    for _, k in enumerate(d):
        print(k, '\t', d[k])
    print('\n')

'''
I'm really sorry, these next three functions are named really poorly
'''
def FIND(inp, out, line, file=0):
    for i in inp:
        if (('range' in i) and
            ('spellingLoc' in i['range']['begin']) and
            ('line' in i['range']['begin']['spellingLoc']) and
            (i['range']['begin']['spellingLoc']['line'] == line) and
            (not ('file' in i['range']['begin']['spellingLoc']))
            ):
            out.append(i['type']['qualType'])
        if ('inner' in i):
            FIND(i['inner'], out, line, file)
def GETARGS(inp, out):
    for i in inp:
        # if this block is based on a single macro expansion (e.g. begin/end offset is the same)
        if (('range' in i)
            and ('spellingLoc' in i['range']['begin'])
            and ('expansionLoc' in i['range']['begin'])
            and ('spellingLoc' in i['range']['end'])
            and ('expansionLoc' in i['range']['end'])
            and ('offset' in i['range']['begin']['spellingLoc'])
            # and ('offset' in i['range']['begin']['expansionLoc'])
            and ('offset' in i['range']['end']['spellingLoc'])
            # and ('offset' in i['range']['end']['expansionLoc'])
            and ('isMacroArgExpansion' in i['range']['begin']['expansionLoc'])
            and ('isMacroArgExpansion' in i['range']['end']['expansionLoc'])

            and (i['range']['begin']['spellingLoc']['offset'] == i['range']['end']['spellingLoc']['offset'])
            ):
            out[i['range']['begin']['spellingLoc']['offset']] = i['type']['qualType']
        elif ('inner' in i):
            GETARGS(i['inner'], out)
def CORRESPOND(inp, out, dline, rline, rcol):
    okey = f'{rline}:{rcol}'
    for i in inp:
        if (('range' in i)
            and ('spellingLoc' in i['range']['begin'])
            and ('expansionLoc' in i['range']['begin'])
            and ('line' in i['range']['begin']['spellingLoc'])
            and ('line' in i['range']['begin']['expansionLoc'])
            and ('col' in i['range']['begin']['expansionLoc'])
            and ('line' in i['range']['end']['spellingLoc'])
            and ('line' in i['range']['end']['expansionLoc'])
            and ('col' in i['range']['end']['expansionLoc'])
            and (int(i['range']['begin']['spellingLoc']['line']) == int(dline))
            and (int(i['range']['begin']['expansionLoc']['line']) == int(rline))
            and (int(i['range']['begin']['expansionLoc']['col']) == int(rcol))
            and (int(i['range']['end']['spellingLoc']['line']) == int(dline))
            and (int(i['range']['end']['expansionLoc']['line']) == int(rline))
            and (int(i['range']['end']['expansionLoc']['col']) == int(rcol))
            # and (not ('file' in i['range']['begin']['spellingLoc']))
            ):
            argdict = {}
            GETARGS(i['inner'], argdict)
            if not (okey in out):
                out[okey] = {
                    'fntype': i['type']['qualType'],
                    'argtype': argdict
                }
        elif ('inner' in i):
            CORRESPOND(i['inner'], out, dline, rline, rcol)

with open(f'{fp[:-1]}trace', 'r') as tfile:
    wstr = f'{os.getcwd()}/{fp}'
    current = tfile.readline()
    rl = 0
    rc = 0
    ref = 0
    ln = 0
    def_offset = 0
    while current != '':
        ### If New Expansion
        if (current[0] != ' '):
            current = current.split(f'{wstr}:', 1)[1].split(':', 2)
            rl = current[0]
            rc = current[1]
            ref = ':'.join(current[0:2])
            # expansions[ref] = {
            #     'deps': []
            # }
        ### If Expansion Dependency
        elif (len(current.split(': see macro definition: ')) == 2):
            current = current.split(f'{wstr}:', 1)[1].split(':')
            ln = int(current[0])
            # expansions[ref]['deps'].append(ln)
            if not (ln in macros):
                macros[ln] = {
                    'name': current[-1][1:-1].split('(')[0],
                    'type': {},
                    'value': '',
                    'const': 'const ',
                    'args': []
                }
            def_offset = 0
            current = current[-1].split('(', 1)
            if len(current) > 1:
                current = current[-1][:-2].split(',')
                macros[ln]['args'] = current
        ### If Non-function-like Macro
        elif (def_offset == 2 and len(macros[ln]['args']) == 0):
            x = []
            FIND(ast, x, ln)
            macros[ln]['type'] = list(set(x))
            macros[ln]['value'] = current.strip()
        ### If Function-like Macro
        elif (def_offset == 3 and len(macros[ln]['args']) > 0):
            x = []
            CORRESPOND(ast, macros[ln]['type'], ln, rl, rc)

        current = tfile.readline()
        def_offset = def_offset + 1

    ### Set to const only if not redefined
    k = list(macros.keys())
    for i in range(len(k) - 1):
        for j in range(i+1, len(k)):
            if (macros[k[i]]['name'] == macros[k[j]]['name']):
                macros[k[i]]['const'] = ''
                macros[k[j]]['const'] = ''

    PrintDict(macros)
    # PrintDict(expansions)
    
output = []
with open(f'{fp}', 'r') as cfile:
    output = cfile.readlines()
    cfile.close()

line_expansions = {}
col_expansions = {}
for i in range(len(output) - 1, -1, -1):
    if ((i + 1) in macros):
        m = macros[i + 1]

        ### Replace Constant Defintion Macros
        if (len(m['args']) == 0 and len(m['type']) > 0):
            output[i] = f"{m['const']}{m['type'][0]} {m['name']} = {m['value']};\n"

        ### Replace Simple Function-like Macros
        if (len(m['args']) > 0 and len(m['type']) > 0):
            has_invalid = 0 # If there are typesignatures we can't parse, we need to keep the original macro definition

            # Build macro's function signatures
            my_types = []
            for _, typedefs in enumerate(m['type']):
                signature = [f"{m['type'][typedefs]['fntype']}"]
                for at in m['type'][typedefs]['argtype']:
                    signature.append(m['type'][typedefs]['argtype'][at])
                if (len(signature) == len(m['args']) + 1):
                    my_types.append(signature)
                else:
                    has_invalid = 1

            # Handle case where function can't be converted
            if (has_invalid and len(my_types)):
                output.insert(i+1, '\n')
                if ((i + 1) in line_expansions):
                    line_expansions[i+1] = line_expansions[i+1] + 1
                else:
                    line_expansions[i+1] = 1

            # Replace Basic Function-like Macros
            for it, sig in enumerate(my_types):
                # Generate argument definitions
                alist = ''
                for fdsa, asdf in enumerate(m['args']):
                    alist += f"{sig[fdsa + 1]} {asdf}, "

                # Insert Function Declaration
                fdef = f"{sig[0]} {m['name']}_{it}({alist[:-2]}) {{ return {output[i].split(')', 1)[-1].split('//')[0].strip()}; }}\n"
                if (it == 0):
                    output[i+it+has_invalid] = fdef
                else:
                    output.insert(i+1, fdef)
                    if ((i + 1) in line_expansions):
                        line_expansions[i+1] = line_expansions[i+1] + 1
                    else:
                        line_expansions[i+1] = 1
                
                # Replace macros with corresponding function calls if they exist
                for _, loc in enumerate(m['type']):
                    if (m['type'][loc]['fntype'] == sig[0]):
                        does_match = True
                        for iteration_variable, thekey in enumerate(m['type'][loc]['argtype']):
                            if (m['type'][loc]['argtype'][thekey] != sig[iteration_variable + 1]):
                                does_match = False
                        if (does_match):
                            location = loc.split(':')
                            location[0] = int(location[0])
                            location[1] = int(location[1])
                            ogy = location[0]
                            ogx = location[1]
                            updates = [ex for ex in list(line_expansions.keys()) if ex <= location[0]]
                            for up in updates:
                                location[0] = location[0] + line_expansions[up]
                            if (ogy in col_expansions):
                                for xs in col_expansions[ogy]:
                                    if xs < ogx:
                                        location[1] = location[1] + col_expansions[ogy][xs]
                            newout = output[location[0] - 1][location[1]-1:].split('(',1)
                            print(location, newout)
                            oglen = len(newout[0]) + 1
                            newout[0] = f"{m['name']}_{it}"
                            newlen = len(newout[0]) + 1
                            if (ogy in col_expansions):
                                col_expansions[ogy][ogx] = newlen - oglen
                            else:
                                col_expansions[ogy] = { ogx: newlen - oglen}
                            combine = output[location[0] - 1][:location[1]-1] + '('.join(newout)

                            output[location[0] - 1] = combine

with open(f'{fp[:-1]}0.c', 'w') as out:
    out.writelines(output)
    out.close()
