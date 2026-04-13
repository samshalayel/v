import json
import re

# Read filter info
with open('filter_info.json', 'r', encoding='utf-8') as f:
    filters = json.load(f)

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Generate filter HTML/JS code
filter_code = []

for filter_name, filter_info in filters.items():
    # Create safe variable name (remove special characters)
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', filter_name.replace(' ', '').replace('|', ''))

    filter_code.append(f'            document.getElementById("menu").appendChild(')
    filter_code.append(f'                document.createElement("div"));')

    if filter_info['type'] == 'int':
        # Create slider for integer fields
        filter_code.append(f'            var div_{safe_name} = document.createElement("div");')
        filter_code.append(f'            div_{safe_name}.id = "div_{safe_name}";')
        filter_code.append(f'            div_{safe_name}.className = "slider";')
        filter_code.append(f'            document.getElementById("menu").appendChild(div_{safe_name});')

        filter_code.append(f'            var lab_{safe_name} = document.createElement(\'div\');')
        filter_code.append(f'            lab_{safe_name}.innerHTML  = \'{filter_name}: <span id="val_{safe_name}"></span>\';')
        filter_code.append(f'            lab_{safe_name}.className = \'filterlabel\';')
        filter_code.append(f'            document.getElementById("menu").appendChild(lab_{safe_name});')

        filter_code.append(f'            var reset_{safe_name} = document.createElement(\'div\');')
        filter_code.append(f'            reset_{safe_name}.innerHTML = \'clear filter\';')
        filter_code.append(f'            reset_{safe_name}.className = \'filterlabel\';')
        filter_code.append(f'            lab_{safe_name}.className = \'filterlabel\';')
        filter_code.append(f'            reset_{safe_name}.onclick = function() {{')
        filter_code.append(f'                sel_{safe_name}.noUiSlider.reset();')
        filter_code.append(f'            }};')
        filter_code.append(f'            document.getElementById("menu").appendChild(reset_{safe_name});')

        filter_code.append(f'            var sel_{safe_name} = document.getElementById(\'div_{safe_name}\');')
        filter_code.append(f'            noUiSlider.create(sel_{safe_name}, {{')
        filter_code.append(f'                start: [{filter_info["min"]}, {filter_info["max"]}],')
        filter_code.append(f'                connect: true,')
        filter_code.append(f'                step: 1,')
        filter_code.append(f'                range: {{')
        filter_code.append(f'                    \'min\': {filter_info["min"]},')
        filter_code.append(f'                    \'max\': {filter_info["max"]}')
        filter_code.append(f'                }}')
        filter_code.append(f'            }});')

        filter_code.append(f'            sel_{safe_name}.noUiSlider.on(\'update\', function (values) {{')
        filter_code.append(f'            filterVals =[];')
        filter_code.append(f'            for (value in values){{')
        filter_code.append(f'            filterVals.push(parseInt(value))')
        filter_code.append(f'            }}')
        filter_code.append(f'            val_{safe_name} = document.getElementById(\'val_{safe_name}\');')
        filter_code.append(f'            val_{safe_name}.innerHTML = values.join(\' - \');')
        filter_code.append(f'                filterFunc()')
        filter_code.append(f'            }});')

    elif filter_info['type'] == 'str':
        # Create dropdown for string fields
        filter_code.append(f'            var div_{safe_name} = document.createElement(\'div\');')
        filter_code.append(f'            div_{safe_name}.id = "div_{safe_name}";')
        filter_code.append(f'            div_{safe_name}.className= "filterselect";')
        filter_code.append(f'            document.getElementById("menu").appendChild(div_{safe_name});')

        filter_code.append(f'            sel_{safe_name} = document.createElement(\'select\');')
        filter_code.append(f'            sel_{safe_name}.multiple = true;')

        # Set size based on number of options
        select_size = min(len(filter_info['unique_values']), 10)
        filter_code.append(f'            sel_{safe_name}.size = {select_size};')

        filter_code.append(f'            sel_{safe_name}.id = "sel_{safe_name}";')
        filter_code.append(f'            var {safe_name}_options_str = "<option value=\'\' unselected></option>";')
        filter_code.append(f'            sel_{safe_name}.onchange = function(){{filterFunc()}};')

        # Add options
        for value in filter_info['unique_values']:
            # Escape quotes in value
            escaped_value = value.replace('"', '&quot;').replace("'", "\\'")
            filter_code.append(f'            {safe_name}_options_str  += \'<option value="{escaped_value}">{escaped_value}</option>\';')

        filter_code.append(f'            sel_{safe_name}.innerHTML = {safe_name}_options_str;')
        filter_code.append(f'            div_{safe_name}.appendChild(sel_{safe_name});')

        filter_code.append(f'            var lab_{safe_name} = document.createElement(\'div\');')
        filter_code.append(f'            lab_{safe_name}.innerHTML = \'{filter_name}\';')
        filter_code.append(f'            lab_{safe_name}.className = \'filterlabel\';')
        filter_code.append(f'            div_{safe_name}.appendChild(lab_{safe_name});')

        filter_code.append(f'            var reset_{safe_name} = document.createElement(\'div\');')
        filter_code.append(f'            reset_{safe_name}.innerHTML = \'clear filter\';')
        filter_code.append(f'            reset_{safe_name}.className = \'filterlabel\';')
        filter_code.append(f'            reset_{safe_name}.onclick = function() {{')
        filter_code.append(f'                var options = document.getElementById("sel_{safe_name}").options;')
        filter_code.append(f'                for (var i=0; i < options.length; i++) {{')
        filter_code.append(f'                    options[i].selected = false;')
        filter_code.append(f'                }}')
        filter_code.append(f'                filterFunc();')
        filter_code.append(f'            }};')
        filter_code.append(f'            div_{safe_name}.appendChild(reset_{safe_name});')

# Join all filter code
filter_code_str = '\n'.join(filter_code)

# Find where to insert the filter code (before </script> at the end)
# Look for the last occurrence of </script> before </body>
script_end_pattern = r'(</script>\s*</body>)'
match = re.search(script_end_pattern, html_content)

if match:
    insertion_point = match.start()
    # Insert the filter code before </script></body>
    html_content = (
        html_content[:insertion_point] +
        '\n' + filter_code_str + '\n        ' +
        html_content[insertion_point:]
    )

    # Write back
    with open('index_with_filters.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Filter code generated successfully!")
    print(f"Total filters added: {len(filters)}")
    print("\nFilters:")
    for name in filters.keys():
        print(f"  - {name}")
    print("\nNew file created: index_with_filters.html")
else:
    print("ERROR: Could not find insertion point in HTML")
