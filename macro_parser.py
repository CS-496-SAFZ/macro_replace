import re
import json

def parse_trace(trace_file):
    with open(trace_file, 'r') as file:
        lines = file.read()
    
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

    # does not handle nested situation yet
    def parse_function_macros(text):
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
                "calling_line_number": calling_line_num,
                "definition_line_number": definition_line_num,
                "macro_name": macro_name,
                "parameters": params,
                "invoked_with": invoked_with,
                "expansion": expansion,
            })
        return macros_list

    macros = parse_function_macros(lines)

    return macros

trace_file = "./trace_output2.txt"
macros = parse_trace(trace_file)

with open("macros.json", "w") as json_file:
    json.dump(macros, json_file, indent=4)

print("saved to macros.json")
