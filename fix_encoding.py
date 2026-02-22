with open('transformer_complete.html', 'rb') as f:
    data = f.read()

content = data.decode('utf-8', errors='replace')

# Fix the nav-icon spans — replace broken emoji with HTML entities
import re

nav_icons = {
    "goto('overview')": '&#127758;',   # globe
    "goto('embed')": '&#128288;',       # symbols  
    "goto('sdpa')": '&#127919;',        # target
    "goto('single')": '&#128065;',      # eye
    "goto('multi')": '&#129504;',       # brain
    "goto('masked')": '&#128274;',      # lock
    "goto('cross')": '&#128279;',       # link
    "goto('ffn')": '&#9881;',           # gear
    "goto('encoder')": '&#128442;',     # inbox
    "goto('decoder')": '&#128452;',     # outbox
    "goto('train')": '&#128200;',       # chart
}

# Fix each nav item by replacing the broken icon span content
for nav_fn, icon in nav_icons.items():
    # Pattern: <div class="nav-item..." onclick="goto('xxx')"><span class="nav-icon">???</span>
    pattern = r'(<div class="nav-item[^"]*" onclick="' + nav_fn.replace('(', r'\(').replace(')', r'\)').replace("'", r"'") + r'"><span class="nav-icon">)[^<]+(</span>)'
    replacement = r'\g<1>' + icon + r'\g<2>'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        content = new_content
        print(f'Fixed icon for {nav_fn}')
    else:
        print(f'No match for {nav_fn}')

# Fix nav logo
content = content.replace(
    '<h1>⚡ Transformer Guide</h1>',
    '<h1>&#9889; Transformer Guide</h1>'
)

# Also fix arch-arrow divs (the ↓ arrows)
content = re.sub(r'<div class="arch-arrow">[^<]*N layers</div>',
    '<div class="arch-arrow">&#8595; x N layers</div>', content)
content = re.sub(r'(<div class="arch-arrow">)[^<]+(</div>)',
    r'\g<1>&#8595;\g<2>', content, count=20)

with open('transformer_complete.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. File size:', len(open('transformer_complete.html','rb').read()), 'bytes')
