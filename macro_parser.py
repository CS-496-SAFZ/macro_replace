import re
import json


def split_macros(trace_path, wave_path):
    """
    splits macros encountered in dump by most outer block for ease of
    dealing with nested structures
    """

    with open(trace_path, "r") as file:
        lines = file.read()
    
    # ^ to look at only start of lines (most outer blocks)
    pattern = r"(?=^" + wave_path + r"/.+?:\d+:\d+:)"
    chunks = re.split(pattern, lines, flags=re.MULTILINE)
    
    return [chunk.strip() for chunk in chunks if chunk.strip()]

# does not handle nested situation yet
def parse_function_macros(text):

    # group 1: calling line number
    # group 2: definition line number
    # group 3: name
    # group 4: parameters
    # group 5: invoked with ...
    # group 6: expansion (this capture is based on rescanning and needs to be more robust)

    function_macro_pattern = re.compile(
        r":(\d+):\d+:\s+.*?\n\s+/.*?:(\d+):\d+:\s+see macro definition: (\w+)\((.*?)\)\s+invoked with\s+\[(.*?)\]\s+\[\s+(.*?)\s+rescanning",
        re.DOTALL
    )

    macros_list = []

    for match in function_macro_pattern.finditer(text):
        calling_line_num = match.group(1)
        definition_line_num = match.group(2)
        macro_name = match.group(3)
        params = [param.strip() for param in match.group(4).split(",")]
        invoked_with = {
            p.split("=")[0].strip(): p.split("=")[1].strip() 
            for p in match.group(5).split("\n") if "=" in p
        }
        expansion = match.group(6).strip()
      
        macros_list.append({
            "type": "function",
            "calling_line_number": calling_line_num,
            "definition_line_number": definition_line_num,
            "macro_name": macro_name,
            "parameters": params,
            "invoked_with": invoked_with,
            "expansion": expansion,
        })
    
    return macros_list

def parse_constant_macros(text):
            
    constant_macro_pattern = re.compile(
        r":(\d+):\d+:\s+(\w+)\n\s+/.*?:(\d+):\d+:\s+see macro definition: (\w+)\s+\[\s+(.*?)\s+rescanning",
    re.DOTALL
    )

    macros_list = []
    
    for match in constant_macro_pattern.finditer(text):
        macros_list.append({
            "type": "constant",
            "calling_line_number": match.group(1),
            "macro_name": match.group(2),
            "definition_line_number": match.group(3),
            "expansion": match.group(5).strip(),
        })
    
    return macros_list


#TODO: support nesting
def parse_trace(chunks):
    
    macros = []
    for chunk in chunks:
        function_macros = parse_function_macros(chunk)

        if (function_macros):
            macros.extend(function_macros)
        else:
            constant_macros = parse_constant_macros(chunk)
            macros.extend(constant_macros)

    return macros


trace_path = "./trace_output2.txt"
wave_path = "/Users/frankxin/boost_1_82_0"

macros = parse_trace(split_macros(trace_path, wave_path))


with open("macros_chunking.json", "w") as json_file:
    json.dump(macros, json_file, indent=4)

print("saved to macros_chunking.json")
