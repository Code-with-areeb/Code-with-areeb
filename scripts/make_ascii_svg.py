import cv2
import numpy as np

# Light (spaces) to Dark (dense chars)
RAMP = " .`:-=+*cs#%@"

def image_to_ascii(image_path, width=100):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not open {image_path}")
    
    h, w = img.shape
    aspect_ratio = h / w
    # Standard character aspect ratio fix (~0.55)
    height = int(width * aspect_ratio * 0.53)
    
    resized = cv2.resize(img, (width, height))
    
    lines = []
    for row in resized:
        line = ""
        for pixel in row:
            # Map 0-255 to ramp index
            char_idx = int((pixel / 255) * (len(RAMP) - 1))
            line += RAMP[char_idx]
        lines.append(line)
    return lines

def generate_svg(ascii_lines, output_path="avi-ascii.svg"):
    char_width = 7.2
    char_height = 13.0
    cols = max(len(line) for line in ascii_lines)
    rows = len(ascii_lines)
    
    svg_width = int(cols * char_width) + 20
    svg_height = int(rows * char_height) + 20

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <style>
    .ascii-text {{
      font-family: 'Courier New', Courier, monospace;
      font-size: 11px;
      font-weight: bold;
      fill: #8b949e;
      white-space: pre;
    }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117" rx="6" />
  <g transform="translate(10, 15)">
'''
    
    # Add each line with SMIL wipe animation delay
    total_lines = len(ascii_lines)
    for idx, line in enumerate(ascii_lines):
        # Escape special XML chars if any
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        y_pos = idx * char_height
        delay = idx * 0.04  # row stagger time
        
        svg_content += f'''    <text x="0" y="{y_pos:.1f}" class="ascii-text">
      <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.01s" fill="freeze" />
      {safe_line}
    </text>\n'''

    svg_content += '''  </g>
</svg>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"ASCII SVG saved to {output_path}")

if __name__ == "__main__":
    lines = image_to_ascii("source-prepped.png")
    generate_svg(lines)