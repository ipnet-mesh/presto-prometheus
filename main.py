"""
MeshCore Dashboard for the Pimoroni Presto.
Queries Prometheus at https://metrics.ipnt.uk and displays meshcore metrics.
"""

import gc
import time

import requests
from picovector import ANTIALIAS_BEST, PicoVector, Polygon
from presto import Presto

presto = Presto(ambient_light=True, full_res=True)
display = presto.display
WIDTH, HEIGHT = display.get_bounds()

TITLE = "ipnt.uk"
SUBTITLE_NODES = "Nodes"
SUBTITLE_ADVERTISEMENTS = "Advertisements"
SUBTITLE_MESSAGES = "Messages"
LABEL_1H = "1h"
LABEL_24H = "24h"

PROMETHEUS_URL = "https://metrics.ipnt.uk"
QUERY = '{__name__=~"meshcore_nodes_total|meshcore_advertisements_received|meshcore_messages_received"}'
REFRESH_INTERVAL = 60

FONT_NAME_DEFAULT = "roboto-medium-symbols.af"
FONT_SIZE_DEFAULT = 20
FONT_SIZE_TITLE = 80
FONT_SIZE_SUBTITLE = 35
FONT_SIZE_METRIC = 65
FONT_SIZE_MINILABEL = 28

MARGIN_LEFT = 20
MARGIN_TOP = 70
MAX_WIDTH = WIDTH - (MARGIN_LEFT * 2)
PADDING_TITLE = 60
PADDING_SECTION = 100
PADDING_SECTION_MINILABELS = 30
PADDING_SUBTITLE = 60
PADDING_METRIC_HORIZONTAL = 150

COLOR_BG = display.create_pen(0, 0, 0)
COLOR_YELLOW = display.create_pen(255, 200, 50)
COLOR_WHITE = display.create_pen(255, 255, 255)
COLOR_DIM = display.create_pen(40, 60, 100)
COLOR_LIGHT = display.create_pen(150, 150, 150)
COLOR_NODES = display.create_pen(61, 108, 213)
COLOR_ADVERTISEMENTS = display.create_pen(215, 115, 208)
COLOR_MESSAGES = display.create_pen(0, 209, 178)

display.set_pen(COLOR_BG)
display.clear()
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

# header_circle = Polygon()
# header_circle.circle(WIDTH - 30, 25, 12)

presto.connect()

def fetch_metrics():
    m = {
        "nodes_total": "0",
        "ads_1h": "0", "ads_1d": "0", "ads_7d": "0",
        "msgs_1h": "0", "msgs_1d": "0", "msgs_7d": "0"
    }
    try:
        url = PROMETHEUS_URL + "/api/v1/query?query=" + QUERY
        print("Fetching...")
        resp = requests.get(url)
        data = resp.json()
        resp.close()
        for r in data["data"]["result"]:
            name = r["metric"]["__name__"]
            val = str(int(float(r["value"][1])))
            if name == "meshcore_nodes_total":
                m["nodes_total"] = val
            elif name == "meshcore_advertisements_received":
                w = r["metric"].get("window", "")
                if w == "1h":
                    m["ads_1h"] = val
                elif w == "24h":
                    m["ads_1d"] = val
                elif w == "7d":
                    m["ads_7d"] = val
            elif name == "meshcore_messages_received":
                w = r["metric"].get("window", "")
                if w == "1h":
                    m["msgs_1h"] = val
                elif w == "24h":
                    m["msgs_1d"] = val
                elif w == "7d":
                    m["msgs_7d"] = val
        print("OK")
    except Exception as e:
        print(str(e))
    return m


def vector_text(text, x, y, max_width=MAX_WIDTH, color=COLOR_WHITE,
                font_name=FONT_NAME_DEFAULT, font_size=FONT_SIZE_DEFAULT):
    vector.set_font(font_name, font_size)
    display.set_pen(color)
    vector.text(text, x, y, max_width=max_width)
    

def vector_title(text, x, y, color=COLOR_WHITE):
    vector_text(text, x, y, color, font_name=FONT_NAME_DEFAULT, font_size=FONT_SIZE_TITLE)

def vector_subtitle(text, x, y, color=COLOR_LIGHT):
    vector_text(text, x, y, color, font_size=FONT_SIZE_SUBTITLE)

def vector_metric(text, x, y, color=COLOR_WHITE, size=FONT_SIZE_METRIC):
    vector_text(text, x, y, color=color, font_size=size)
    
def vector_minilabel(text, x, y, color=COLOR_DIM, size=FONT_SIZE_MINILABEL):
    vector_text(text, x, y, color=color, font_size=size)
    

def draw(m):

    display.set_pen(COLOR_BG)
    display.clear()

    x_left = MARGIN_LEFT
    y_top = MARGIN_TOP
    # display.set_pen(COLOR_YELLOW)
    # vector.draw(header_circle)

    # === TITLE ===

    y_title = y_top
    vector_title(TITLE, x_left, y_title)
    
    # === NODES ===
    
    y_nodes = y_title + PADDING_TITLE
    
    vector_subtitle(
        SUBTITLE_NODES,
        x_left, y_nodes
    )
    vector_metric(
        m["nodes_total"],
        x_left, y_nodes + 60,
        color=COLOR_NODES
    )
    
    # === ADVERTISEMENTS ===
    
    y_advertisements = y_nodes + PADDING_SECTION
    
    vector_subtitle(
        SUBTITLE_ADVERTISEMENTS,
        x_left, y_advertisements
    )
    vector_metric(
        m["ads_1h"],
        x_left, y_advertisements + PADDING_SUBTITLE,
        color=COLOR_ADVERTISEMENTS
    )
    vector_minilabel(
        "1h",
        x_left, y_advertisements + PADDING_SUBTITLE + 30
    )
    vector_metric(
        m["ads_1d"],
        x_left + PADDING_METRIC_HORIZONTAL, y_advertisements + PADDING_SUBTITLE,
        color=COLOR_ADVERTISEMENTS
    )
    vector_minilabel(
        "1d",
        x_left + PADDING_METRIC_HORIZONTAL, y_advertisements + PADDING_SUBTITLE + 30
    )
    vector_metric(
        m["ads_7d"],
        x_left + (PADDING_METRIC_HORIZONTAL * 2), y_advertisements + PADDING_SUBTITLE,
        color=COLOR_ADVERTISEMENTS
    )
    vector_minilabel(
        "7d",
        x_left + (PADDING_METRIC_HORIZONTAL * 2), y_advertisements + PADDING_SUBTITLE + 30
    )

    # === MESSAGES ===

    y_messages = y_advertisements + PADDING_SECTION + PADDING_SECTION_MINILABELS
    
    vector_subtitle(
        SUBTITLE_MESSAGES,
        x_left, y_messages
    )
    vector_metric(
        m["msgs_1h"],
        x_left, y_messages + PADDING_SUBTITLE,
        color=COLOR_MESSAGES
    )
    vector_minilabel(
        "1h",
        x_left, y_messages + PADDING_SUBTITLE + 30
    )
    vector_metric(
        m["msgs_1d"],
        x_left + PADDING_METRIC_HORIZONTAL, y_messages + PADDING_SUBTITLE,
        color=COLOR_MESSAGES
    )
    vector_minilabel(
        "1d",
        x_left + PADDING_METRIC_HORIZONTAL, y_messages + PADDING_SUBTITLE + 30
    )
    vector_metric(
        m["msgs_7d"],
        x_left + (PADDING_METRIC_HORIZONTAL * 2), y_messages + PADDING_SUBTITLE,
        color=COLOR_MESSAGES
    )
    vector_minilabel(
        "7d",
        x_left + (PADDING_METRIC_HORIZONTAL * 2), y_messages + PADDING_SUBTITLE + 30
    )
    
    #display.set_pen(DIM)
    #display.text(LABEL_1H, 15, 218, WIDTH, 2)
    #display.text(LABEL_24H, 145, 218, WIDTH, 2)

    presto.update()


metrics = fetch_metrics()
last_updated = time.time()

while True:
    if time.time() - last_updated > REFRESH_INTERVAL:
        metrics = fetch_metrics()
        last_updated = time.time()

    draw(metrics)
    gc.collect()
    time.sleep(1)
