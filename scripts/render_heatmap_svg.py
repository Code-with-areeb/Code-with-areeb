import json
import os

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

def render_svg():
    json_path = "data/contributions.json"
    if not os.path.exists(json_path):
        print("Data file not found! Run fetch_contributions.py first.")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    days = data.get("days", [])
    
    box_size = 10
    box_gap = 3
    start_x = 20
    start_y = 20
    
    svg_width = 860
    svg_height = 140
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    .day-box {{ rx: 2; ry: 2; opacity: 0; animation: fadeIn 0.4s ease-out forwards; }}
    @keyframes fadeIn {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117" rx="6" />
  <g transform="translate({start_x}, {start_y})">
'''

    # Grid 53 weeks x 7 days
    for i, day in enumerate(days):
        week = i // 7
        day_of_week = i % 7
        
        x = week * (box_size + box_gap)
        y = day_of_week * (box_size + box_gap)
        
        level = min(day.get("level", 0), 5)
        color = PALETTE[level]
        delay = (week + day_of_week) * 0.01
        
        svg += f'    <rect class="day-box" x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{color}" style="animation-delay: {delay:.2f}s;" />\n'

    svg += '''  </g>
</svg>'''

    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Heatmap SVG saved to contrib-heatmap.svg")

if __name__ == "__main__":
    render_svg()