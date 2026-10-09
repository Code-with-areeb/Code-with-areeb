NAME = "Areeb"
USERNAME = "Code-with-areeb"
ROLE = "Full-Stack Developer"
STACK = "React, Node.js, Python, JavaScript"
LOCATION = "Pakistan"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="400" viewBox="0 0 490 400">
  <style>
    .bg {{ fill: #0d1117; rx: 6px; }}
    .text {{ font-family: monospace; font-size: 14px; fill: #c9d1d9; }}
    .key {{ fill: #58a6ff; font-weight: bold; }}
    .title {{ fill: #7fa127; font-weight: bold; }}
    .fade {{ opacity: 0; animation: fadeIn 0.5s forwards; }}
    @keyframes fadeIn {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <g class="text">
    <text x="20" y="40" class="title fade" style="animation-delay: 0.1s">{USERNAME}@github ~ $ neofetch</text>
    <text x="20" y="80" class="fade" style="animation-delay: 0.3s"><tspan class="key">Name:</tspan> {NAME}</text>
    <text x="20" y="120" class="fade" style="animation-delay: 0.5s"><tspan class="key">Role:</tspan> {ROLE}</text>
    <text x="20" y="160" class="fade" style="animation-delay: 0.7s"><tspan class="key">Stack:</tspan> {STACK}</text>
    <text x="20" y="200" class="fade" style="animation-delay: 0.9s"><tspan class="key">Location:</tspan> {LOCATION}</text>
  </g>
</svg>'''

with open("info-card.svg", "w") as f:
    f.write(svg)
