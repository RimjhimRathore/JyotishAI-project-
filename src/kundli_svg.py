# Short labels for planets
ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke"}

# house number -> (planet_x, planet_y, sign_number_x, sign_number_y)
# The chart is a 400x400 square; these are fixed North Indian positions.
HOUSE_POS = {
    1:  (200,  95, 200, 178),
    2:  (100,  30, 100,  75),
    3:  ( 28, 100,  75, 100),
    4:  ( 90, 200, 168, 200),
    5:  ( 28, 300,  75, 300),
    6:  (100, 372, 100, 325),
    7:  (200, 320, 200, 225),
    8:  (300, 372, 300, 325),
    9:  (372, 300, 325, 300),
    10: (310, 200, 232, 200),
    11: (372, 100, 325, 100),
    12: (300,  30, 300,  75),
}


def build_north_chart(chart):
    """Takes the dict from calculate_chart() and returns an SVG string."""
    lagna_sign = chart["lagna"]["sign_num"]

    # Group planet labels by house
    by_house = {h: [] for h in range(1, 13)}
    for name, p in chart["planets"].items():
        label = ABBR[name] + ("(R)" if p.get("retrograde") else "")
        by_house[p["house"]].append(label)

    svg = ['<svg viewBox="-4 -4 408 408" xmlns="http://www.w3.org/2000/svg" '
           'style="width:100%;height:auto;">']
    svg.append('<rect x="0" y="0" width="400" height="400" fill="#fff8e1" '
               'stroke="#b8860b" stroke-width="3"/>')
    svg.append('<polygon points="200,0 400,200 200,400 0,200" fill="none" '
               'stroke="#b8860b" stroke-width="2"/>')
    svg.append('<line x1="0" y1="0" x2="400" y2="400" stroke="#b8860b" stroke-width="2"/>')
    svg.append('<line x1="400" y1="0" x2="0" y2="400" stroke="#b8860b" stroke-width="2"/>')

    for house in range(1, 13):
        px, py, sx, sy = HOUSE_POS[house]

        # Sign number: house 1 has the Lagna sign, then it goes up by one each house
        sign_num = (lagna_sign + house - 2) % 12 + 1
        weight = "bold" if house == 1 else "normal"
        svg.append(f'<text x="{sx}" y="{sy}" text-anchor="middle" '
                   f'dominant-baseline="middle" font-size="14" font-weight="{weight}" '
                   f'fill="#b03a2e">{sign_num}</text>')

        # Planets: two per line so they fit in the small triangles
        labels = by_house[house]
        lines = [" ".join(labels[i:i + 2]) for i in range(0, len(labels), 2)]
        start_y = py - (len(lines) - 1) * 8
        for i, line in enumerate(lines):
            svg.append(f'<text x="{px}" y="{start_y + i * 16}" text-anchor="middle" '
                       f'dominant-baseline="middle" font-size="12" font-weight="bold" '
                       f'fill="#1a1a1a">{line}</text>')

    svg.append("</svg>")
    return "".join(svg)