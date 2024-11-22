import os
import sys
import time
import json

ast = {}            # Clang's AST
macros = {}         # macro definition information
expansions = {}     # macro expansion trace
defines = {}

def PrintDict(d):
    for _, k in enumerate(d):
        print(k, '\t', d[k])
    print('\n')

'''
I'm really sorry, these next three functions are named really poorly
'''
def FIND(inp, out, line, spath, epath):
    if (spath == epath):
        for i in inp:
            if (('range' in i) and
                ('spellingLoc' in i['range']['begin']) and
                ('line' in i['range']['begin']['spellingLoc']) and
                (i['range']['begin']['spellingLoc']['line'] == line) and
                (not ('file' in i['range']['begin']['spellingLoc']))
                ):
                out.append(i['type']['qualType'])
            if ('inner' in i):
                FIND(i['inner'], out, line, spath, epath)
    else:
        for i in inp:
            if (('range' in i) and
                ('spellingLoc' in i['range']['begin']) and
                ('line' in i['range']['begin']['spellingLoc']) and
                (i['range']['begin']['spellingLoc']['line'] == line) and
                ('file' in i['range']['begin']['spellingLoc']) and
                (i['range']['begin']['spellingLoc']['file'] == spath)
                ):
                out.append(i['type']['qualType'])
            if ('inner' in i):
                FIND(i['inner'], out, line, spath, epath)
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
def CORRESPOND(inp, out, dline, rline, rcol, spath, epath, okey):
    if (spath == epath):
        for i in inp:
            if (('range' in i)
                and ('spellingLoc' in i['range']['begin'])
                and ('expansionLoc' in i['range']['begin'])
                and ('spellingLoc' in i['range']['end'])
                and ('expansionLoc' in i['range']['end'])
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
                # and ('file' in i['range']['begin']['spellingLoc'])
                # and (i['range']['begin']['spellingLoc']['file'] == spath)
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
                CORRESPOND(i['inner'], out, dline, rline, rcol, spath, epath, okey)
    else:
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
                and ('file' in i['range']['begin']['spellingLoc'])
                and (i['range']['begin']['spellingLoc']['file'] == spath)
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
                CORRESPOND(i['inner'], out, dline, rline, rcol, spath, epath, okey)

'''
Load in .c file
Defaults to input.c but you can pass in a different path
'''
here = os.getcwd()
fp = f'{here}/input'
outdir = f'{here}/output'
if (len(sys.argv) == 3):
    fp = arg[1]
    outdir = arg[2]
os.system(f'rm -rf {outdir}')
os.system(f'cp -r {fp} {outdir}')

'''
Generate wave trace and clang AST
'''
for (dpath, dnames, fnames) in os.walk(outdir):
    for f in fnames:
        current_file = f'{dpath}/{f}'
        with open(current_file, 'r+') as myfile:
            source = myfile.read()
            myfile.seek(0, 0)
            if (myfile.readline() != "#pragma wave trace(enable)\n"):
                myfile.seek(0, 0)
                myfile.write('#pragma wave trace(enable)\n' + source)
            myfile.close()
    # print(dpath, fnames)
    for f in fnames:
        current_file = f'{dpath}/{f}'
        with open(current_file, 'r+') as myfile:
            os.system(f'wave -t {current_file}.trace {current_file} >/dev/null')
            os.system(f'clang -Xclang -ast-dump=json -fsyntax-only {current_file} > {current_file}.ast')
            myfile.close()
        
        with open(f'{current_file}.ast', 'r') as afile:
            ast[current_file] = json.load(afile)
            ast[current_file] = [i for i in ast[current_file]['inner'] if
                i['range']['begin']
                and 'inner' in i
                and (
                    (
                        'includedFrom' in i['loc']
                        and 'file' in i['loc']
                        and outdir in i['loc']['file']
                        and outdir in i['loc']['includedFrom']['file']
                    ) or (
                        'file' in i['loc']
                        and outdir in i['loc']['file']
                    ) or (
                        len(i['loc']) == 4
                        and (not ('file' in i['loc']))
                        and (not ('includedFrom' in i['loc']))
                    )
                )
            ]
            # print(current_file)
            afile.close()

'''
Loads in the AST of the last function (e.g. main)

Basically, this script only really works with single-function files
'''
# quit()
for a in ast:
    with open(f'{a}.trace', 'r') as tfile:
        wstr = a
        current = tfile.readline()
        rl = 0
        rc = 0
        ref = 0
        ln = 0
        fpath = ''
        current_key = ''
        def_offset = 0
        while current != '':
            ### If New Expansion
            if (current[0] != ' '):
                current = current.split(f'{wstr}:', 1)[1].split(':', 2)
                rl = current[0]
                rc = current[1]
                ref = ':'.join([a, rl])
                if (not (ref in expansions)):
                    expansions[ref] = {}
                expansions[ref][rc] = []
            ### If Expansion Dependency
            elif (len(current.split(': see macro definition: ')) == 2):
                current = current.split(':', 1)
                fpath = current[0].strip()
                current = current[1].split(':')
                ln = int(current[0])
                current_key = f'{fpath}:{ln}'
                expansions[ref][rc].append(current_key)
                if not (current_key in macros):
                    macros[current_key] = {
                        'name': current[-1][1:-1].split('(')[0],
                        'ish': current_key.split(':', 1)[0][-1] == "h",
                        'definemein': "",
                        'type': {},
                        'value': '',
                        'const': 'const ',
                        'args': [],
                    }
                def_offset = 0
                current = current[-1].split('(', 1)
                if len(current) > 1:
                    current = current[-1][:-2].split(',')
                    macros[current_key]['args'] = current
            ### If Non-function-like Macro
            elif (def_offset == 2 and len(macros[current_key]['args']) == 0):
                x = []
                FIND(ast[a], x, ln, fpath, a)
                macros[current_key]['type'] = list(set(x))
                macros[current_key]['type'].sort() # TEMPORARY, REPLACE WITH TYPEMAX
                macros[current_key]['value'] = current.strip()
            ### If Function-like Macro
            elif (def_offset == 3 and len(macros[current_key]['args']) > 0):
                # x = []

                CORRESPOND(ast[a], macros[current_key]['type'], ln, rl, rc, fpath, a, f'{a}:{rl}:{rc}')

            current = tfile.readline()
            def_offset = def_offset + 1

        ### Set to const only if not redefined
        # k = list(macros.keys())
        # for i in range(len(k) - 1):
        #     for j in range(i+1, len(k)):
        #         if (macros[k[i]]['name'] == macros[k[j]]['name']):
        #             macros[k[i]]['const'] = ''
        #             macros[k[j]]['const'] = ''

for f in macros:
    if macros[f]["ish"]:
        matched = False
        for e in expansions:
            for exps in expansions[e]:
                if f in expansions[e][exps]:
                    macros[f]["definemein"] = e.split(":")[0]
                    if (e.split(":")[0] in defines):
                        defines[e.split(":")[0]][f] = []
                    else:
                        defines[e.split(":")[0]] = {f: []}
                    matched = True
                if matched:
                    break
            if matched:
                break

for (dpath, dnames, fnames) in os.walk(outdir):
    F = [i for i in fnames if ((not (".trace" in i)) and (not (".ast" in i)))]
    line_expansions = {}
    col_expansions = {}
    for f in F:
        current_file = f'{dpath}/{f}'
        if (not (current_file in line_expansions)):
            line_expansions[current_file] = {}
        output = []
        with open(f'{current_file}', 'r') as cfile:
            output = cfile.readlines()
            cfile.close()

        for i in range(len(output) - 1, -1, -1):
            ckey = ':'.join([current_file, str(i + 1)])
            if (ckey in macros):
                m = macros[ckey]
                # print(current_file, m)
                
                ### Replace Constant Defintion Macros
                if (len(m['args']) == 0 and len(m['type']) > 0):
                    # output[i] = f"#ifndef C2RUSTMACROREPLACE_{m['name']}\n"
                    # output.insert(i+1, f"#define C2RUSTMACROREPLACE_{m['name']}\n")
                    # output.insert(i+2, f"{m['const']}{m['type'][0]} {m['name']} = {m['value']};\n")
                    # output.insert(i+3, f"#endif\n")
                    if (m['ish']):
                        output[i] = f"extern {m['const']}{m['type'][0]} {m['name']};\n"
                        defines[m["definemein"]][ckey].append(f"{m['const']}{m['type'][0]} {m['name']} = {m['value']};\n")
                    else:
                        output[i] = f"{m['const']}{m['type'][0]} {m['name']} = {m['value']};\n"
                    # if ((i + 1) in line_expansions[current_file]):
                    #     line_expansions[current_file][i+1] = line_expansions[current_file][i+1] + 3
                    # else:
                    #     line_expansions[current_file][i+1] = 3

                ### Replace Basic Functions
                if (len(m['args']) > 0 and len(m['type']) > 0):
                    has_invalid = 0

                    my_types = []
                    testvar = 0
                    for _, typedefs in enumerate(m['type']):
                        signature = [f"{m['type'][typedefs]['fntype']}"]
                        for at in m['type'][typedefs]['argtype']:
                            signature.append(m['type'][typedefs]['argtype'][at])
                        if (len(signature) == len(m['args']) + 1):
                            my_types.append(signature)
                            m['type'][typedefs]['rename'] = f"{m['name']}_{testvar}"
                            testvar = testvar + 1
                            m['type'][typedefs]['works'] = 1
                        else:
                            has_invalid = 1
                            m['type'][typedefs]['works'] = 0
                    # print(ckey, m['name'])
                    # print(my_types, has_invalid)

                    # Handle case where function can't be converted
                    # if (has_invalid and len(my_types)):
                    for nsigs in range(len(my_types) - 1 + has_invalid):
                        output.insert(i+1, '\n')
                        if ((i + 1) in line_expansions[current_file]):
                            line_expansions[current_file][i+1] = line_expansions[current_file][i+1] + 1
                        else:
                            line_expansions[current_file][i+1] = 1

                    # Replace Basic Function-like Macros
                    for it, sig in enumerate(my_types):
                        # m['type'][typedefs]['rename'] = f"{m['name']}_{it}"
                        # Generate argument definitions
                        alist = ''
                        for fdsa, asdf in enumerate(m['args']):
                            alist += f"{sig[fdsa + 1]} {asdf}, "

                        # Insert Function Declaration
                        fdef = ""
                        if (m['ish']):
                            fdef = f"extern {sig[0]} {m['name']}_{it}({alist[:-2]});\n"
                            defines[m["definemein"]][ckey].append(f"{sig[0]} {m['name']}_{it}({alist[:-2]}) {{ return {output[i].split(')', 1)[-1].split('//')[0].strip()}; }}\n")
                        else:
                            fdef = f"{sig[0]} {m['name']}_{it}({alist[:-2]}) {{ return {output[i].split(')', 1)[-1].split('//')[0].strip()}; }}\n"
                        output[i+it+has_invalid] = fdef
                        if (it != 0):
                            if ((i + 1) in line_expansions[current_file]):
                                line_expansions[current_file][i+1] = line_expansions[current_file][i+1] + 1
                            else:
                                line_expansions[current_file][i+1] = 1
                        # else:
                        #     if ((i + 1) in line_expansions[current_file]):
                        #         line_expansions[current_file][i+1] = line_expansions[current_file][i+1] + 3
                        #     else:
                        #         line_expansions[current_file][i+1] = 3

        with open(current_file, 'w') as out:
            out.writelines(output)
            out.close()
            
    for f in F:
        current_file = f'{dpath}/{f}'
        if (not (current_file in col_expansions)):
            col_expansions[current_file] = {}
        output = []
        with open(f'{current_file}', 'r') as cfile:
            output = cfile.readlines()
            cfile.close()
        for i in range(len(output) - 1, -1, -1):
            ckey = ':'.join([current_file, str(i + 1)])
            if (ckey in expansions):
                # e = expansions[ckey]
                # print("wowwy")

                for e in expansions[ckey]:
                    # my_macro
                    # macros[]
                    aosdfjk = ':'.join([ckey, e])
                    # print(aosdfjk)

                    new_name = ''
                    my_def = ''
                    isvalid = 0
                    validisvalid = 1
                    for awejifo in macros:
                        for matchexp in macros[awejifo]['type']:
                            if matchexp == aosdfjk:
                                my_def = macros[awejifo]
                                if (not isvalid) and (my_def['type'][aosdfjk]['works'] == 1) and ('rename' in my_def['type'][aosdfjk]):
                                    new_name = my_def['type'][aosdfjk]['rename']
                                    isvalid = 1
                                else:
                                    isvalid = 0
                                    validisvalid = 0

                    if not (isvalid and validisvalid):
                        my_def = ''
                        
                    if my_def:
                        updates = [ex for ex in list(line_expansions[current_file].keys()) if ex <= (i + 1)]
                        my_line = int(i)
                        for doUpdate in updates:
                            my_line = my_line + line_expansions[current_file][doUpdate]
                        if not ((i+1) in col_expansions[current_file]):
                            col_expansions[current_file][i+1] = {}
                        col_updates = [ex for ex in list(col_expansions[current_file][i+1].keys()) if int(ex) <= int(e)]
                        my_col = int(e) - 1
                        for fdjsfjkd in col_updates:
                            my_col = my_col + col_expansions[current_file][i+1][fdjsfjkd]
                        h1 = output[my_line][:my_col]
                        h2 = output[my_line][my_col:]

                        h3 = h2.split(my_def['name'], 1)
                        h3[0] = new_name
                        
                        col_expansions[current_file][i+1][int(e)] = len(new_name) - len(my_def['name'])
                        insert = ''.join([' ' for i in range(len(new_name) - len(my_def['name']))])
                        output[my_line] = ''.join([h1, ''.join(h3)])

        with open(current_file, 'w') as out:
            out.writelines(output)
            if current_file in defines:
                for fjdkls in defines[current_file]:
                    out.writelines(defines[current_file][fjdkls])
            out.close()

os.system(f"rm -rf {outdir}/*.trace {outdir}/*.ast")

# PrintDict(macros)
# PrintDict(expansions)
# PrintDict(defines)
