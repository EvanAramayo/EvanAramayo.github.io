import json
import logging
import collections
from datetime import datetime
from pathlib import Path
from tkinter import Tk, Canvas, Button, Label
from tkinter.scrolledtext import ScrolledText
import zmq
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors as mpc

# Paths / assets

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Small helper: create an embedded Matplotlib figure
class LiveLine:
    def __init__(self, master, x, y, w, h, title="", ylabel="", maxlen=60):
        self.buffer_x = collections.deque(maxlen=maxlen)
        self.buffer_y = collections.deque(maxlen=maxlen)
        self.fig = Figure(figsize=(w/100, h/100), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title, fontsize=8)
        self.ax.set_ylabel(ylabel, fontsize=8)
        self.ax.tick_params(labelsize=7)
        self.ax.grid(True, alpha=0.3)
        (self.line,) = self.ax.plot([], [], lw=1.5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().place(x=x, y=y, width=w, height=h)
        # mplcursors hover tooltip
        cur = mpc.cursor(self.line, hover=True)

        @cur.connect("add")
        def _on_add(sel):
            try:
                idx = int(round(sel.target.index))
            except Exception:
                idx = None
            if idx is not None and 0 <= idx < len(self.buffer_y):
                y = self.buffer_y[idx]
                sel.annotation.set_text(f"{y:.2f}")
            else:
                x, y = sel.target
                sel.annotation.set_text(f"{y:.2f}")

    def push(self, y):
        # simple index on x; you can switch to timestamps if desired
        self.buffer_x.append(len(self.buffer_x))
        self.buffer_y.append(float(y))
        self.line.set_data(range(len(self.buffer_y)), list(self.buffer_y))
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()


# ZMQ subscriber setup
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")     # subscribe to all topics
socket.setsockopt(zmq.RCVTIMEO, 10)       # short timeout so UI stays snappy


# GUI setup (matches your wireframe)
window = Tk()
window.geometry("1153x802")
window.configure(bg="#2A2F4F")
window.title("Vycarb GUI")
window.resizable(False, False)

canvas = Canvas(window, bg="#2A2F4F", height=802, width=1153,
                bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Top bar & logo
canvas.create_rectangle(0, -5, 1151, 96, fill="#E5BEEC", outline="")
raw_img = Image.open(relative_to_assets("image_1.png"))
resized = raw_img.resize((295, 90), Image.LANCZOS)
logo_img = ImageTk.PhotoImage(resized)
Label(window, image=logo_img, bg="#E5BEEC").place(x=0, y=-4)

# Start/Stop buttons (hooks kept; no-op for now)
btn1 = ImageTk.PhotoImage(file=relative_to_assets("button_1.png"))
Button(image=btn1, borderwidth=0, highlightthickness=0,
       command=lambda: None, relief="flat").place(x=8, y=101, width=81, height=40)
btn2 = ImageTk.PhotoImage(file=relative_to_assets("button_2.png"))
Button(image=btn2, borderwidth=0, highlightthickness=0,
       command=lambda: None, relief="flat").place(x=97, y=101, width=81, height=40)

# Layout rectangles (exactly as your wireframe)
# DI-SEA 1
canvas.create_rectangle(8, 151, 411, 519, fill="#917FB3", outline="")
canvas.create_text(158, 147, anchor="nw", text="DI-SEA 1", fill="#FFFFFF", font=("Inter Bold", -22))
# DI-SEA 2
canvas.create_rectangle(416, 153, 819, 519, fill="#5F4A87", outline="")
canvas.create_text(574, 152, anchor="nw", text="DI-SEA 2", fill="#FFFFFF", font=("Inter Bold", -22))
# Doser
canvas.create_rectangle(8, 530, 308, 792, fill="#5F4A87", outline="")
canvas.create_text(77, 529, anchor="nw", text="Doser Peripheral", fill="#A34D18", font=("Inter Bold", -20))
# Reactor Peripheral
canvas.create_rectangle(316, 529, 616, 654, fill="#917FB3", outline="")
canvas.create_text(377, 529, anchor="nw", text="Reactor Peripheral", fill="#27EF00", font=("Inter Bold", -20))
# System Power
canvas.create_rectangle(316, 660, 616, 785, fill="#5F4A87", outline="")
canvas.create_text(330, 665, anchor="nw", text="System Power Metrics", fill="#FFC300", font=("Inter Bold", -18))
# Peripheral Status
canvas.create_rectangle(822, 152, 1148, 392, fill="#5F4A87", outline="")
canvas.create_rectangle(822, 152, 1147, 185, fill="#917FB3", outline="")
for x, label in [(828, "Time"), (938, "DeviceName"), (1052, "Error")]:
    canvas.create_text(x, 157, anchor="nw", text=label, fill="#FFFFFF", font=("Inter Bold", -15))
canvas.create_rectangle(935, 184, 936, 392, fill="#FFFFFF", outline="")
canvas.create_rectangle(1033, 184, 1034, 392, fill="#FFFFFF", outline="")
canvas.create_text(915, 397, anchor="nw", text="Peripheral Status", fill="#DC1A51", font=("Inter Bold", -17))

# Cycle label & number
canvas.create_rectangle(1010, 98, 1145, 143, fill="#917FB3", outline="")
canvas.create_text(1032, 107, anchor="nw", text="Cycle:", fill="#FFFFFF", font=("Inter Bold", -22))
cycle_text_id = canvas.create_text(1100, 107, anchor="nw", text="1", fill="#FFFFFF", font=("Inter Bold", -22))

# Bottom-right Terminal area (inside the blank rectangle)
canvas.create_rectangle(822, 525, 1145, 792, fill="#917FB3", outline="")
canvas.create_text(840, 502, anchor="nw", text="Terminal", fill="#000000", font=("Inter Bold", -16))
terminal_text = ScrolledText(window, bg="#0D1117", fg="#E6EDF3", font=("Consolas", 10), padx=6, pady=6)
terminal_text.place(x=825, y=530, width=319, height=260)
terminal_text.insert("end", "Waiting for device simulator data...\n")
terminal_text.configure(state="disabled")

def term_print(ts, topic, device, msg_type, status, short):
    line = f"{ts} | {topic:<5} | {device:<8} | {msg_type:<9} | {status:<7} | {short}"
    terminal_text.configure(state="normal")
    terminal_text.insert("end", line + "\n")
    terminal_text.see("end")
    terminal_text.configure(state="disabled")

# Mini-plots
# DI-SEA 1 (inside 8,151 to 411,519)
di1_ph   = LiveLine(window, x=50,  y=210, w=150, h=120, title="pH",        ylabel="")
di1_co2  = LiveLine(window, x=240, y=210, w=150, h=120, title="CO₂ (ppm)", ylabel="")
di1_psi  = LiveLine(window, x=60,  y=360, w=150, h=120, title="Pressure",  ylabel="psi")

# DI-SEA 2 (inside 416,153 to 819,519)
di2_ph   = LiveLine(window, x=455, y=210, w=150, h=120, title="pH",        ylabel="")
di2_co2  = LiveLine(window, x=645, y=210, w=150, h=120, title="CO₂ (ppm)", ylabel="")
di2_psi  = LiveLine(window, x=465, y=360, w=150, h=120, title="Pressure",  ylabel="psi")

# Doser chart (long and thin)
doser_rate = LiveLine(window, x=16, y=595, w=280, h=150, title="Doser", ylabel="mL/min")

# Text readouts under DI-SEA cards (Air/Water/Pressure)
# Left card labels
canvas.create_text(260, 390, anchor="nw", text="Air temp:",   fill="#FFFFFF", font=("Inter Bold", -14))
canvas.create_text(260, 415, anchor="nw", text="Water temp:", fill="#FFFFFF", font=("Inter Bold", -14))
canvas.create_text(260, 440, anchor="nw", text="Pressure:",   fill="#FFFFFF", font=("Inter Bold", -14))
di1_air_t_id   = canvas.create_text(345, 390, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))
di1_water_t_id = canvas.create_text(365, 415, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))
di1_psi_t_id   = canvas.create_text(335, 440, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))

# Right card labels
canvas.create_text(627, 390, anchor="nw", text="Air temp:",   fill="#FFFFFF", font=("Inter Bold", -14))
canvas.create_text(627, 415, anchor="nw", text="Water temp:", fill="#FFFFFF", font=("Inter Bold", -14))
canvas.create_text(627, 440, anchor="nw", text="Pressure:",   fill="#FFFFFF", font=("Inter Bold", -14))
di2_air_t_id   = canvas.create_text(712, 390, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))
di2_water_t_id = canvas.create_text(732, 415, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))
di2_psi_t_id   = canvas.create_text(702, 440, anchor="nw", text="--", fill="#FFFFFF", font=("Inter Bold", -14))

# Reactor Peripheral big number
reactor_val_id = canvas.create_text(375, 586, anchor="nw", text="1000 L/min",
                                    fill="#FFFFFF", font=("Inter Bold", -36))

# System Power Metrics
battery_txt_id = canvas.create_text(360, 720, anchor="nw", text="Battery: --%",
                                    fill="#FFFFFF", font=("Inter Bold", -18))
solar_txt_id   = canvas.create_text(360, 750, anchor="nw", text="Solar total yield: --",
                                    fill="#FFFFFF", font=("Inter Bold", -18))

# Peripheral online statuses
status_reactor_id = canvas.create_text(812+20, 440, anchor="nw", text="Reactor: offline",
                                       fill="#FFFFFF", font=("Inter Bold", -18))
status_doser_id   = canvas.create_text(812+20, 470, anchor="nw", text="Doser: offline",
                                       fill="#FFFFFF", font=("Inter Bold", -18))
status_disea_id   = canvas.create_text(812+20, 500, anchor="nw", text="di-sea: offline",
                                       fill="#FFFFFF", font=("Inter Bold", -18))

# State for statuses
online = {"reactor": False, "doser": False, "di-sea": False}

def set_online(device):
    if device in online:
        online[device] = True
    # Reflect in UI
    canvas.itemconfig(status_reactor_id, text=f"Reactor: {'online' if online['reactor'] else 'offline'}")
    canvas.itemconfig(status_doser_id,   text=f"Doser: {'online' if online['doser'] else 'offline'}")
    canvas.itemconfig(status_disea_id,   text=f"di-sea: {'online' if online['di-sea'] else 'offline'}")

# ZMQ polling + routing
def update_data():
    try:
        received = socket.recv_string(zmq.NOBLOCK)
        topic, payload = received.split("|", 1)
        obj = json.loads(payload)
        ts = obj.get("timestamp") or datetime.now().strftime("%H:%M:%S")
        device = obj.get("device_name", "")
        msg_type = obj.get("msg_type", "")
        status = obj.get("status", "")
        data = obj.get("data", {})

        # Pretty, compact summary for terminal
        short = ""
        if device == "di-sea":
            d1 = data.get("di-sea_1", {})
            d2 = data.get("di-sea_2", {})
            short = f"d1 T={d1.get('temp',0):.2f}°C psi={d1.get('psi',0):.2f} | d2 T={d2.get('temp',0):.2f}°C psi={d2.get('psi',0):.2f}"
        elif device == "doser":
            short = f"rate={data.get('dosing_rate',0):.2f}"
        elif device == "reactor":
            short = f"flow={data.get('flow',0):.0f} L/min"
        elif device == "battery":
            short = f"soc={data.get('soc',0):.0f}"
        elif device == "ve_direct":
            short = f"yield_total={data.get('yield_total',0):.2f}"

        term_print(ts, topic, device, msg_type, status, short)

        # Route to widgets
        if topic == "logs":
            # nothing to plot, already printed
            pass

        if topic == "data":
            if device == "di-sea":
                set_online("di-sea")
                d1 = data["di-sea_1"]
                d2 = data["di-sea_2"]

                # Update cycle badge from di-sea cycle
                canvas.itemconfig(cycle_text_id, text=str(d1.get("cycle", 1)))

                # Left plots + text
                di1_ph.push(d1.get("ph", 0))
                di1_co2.push(d1.get("co2", 0))
                di1_psi.push(d1.get("psi", 0))
                canvas.itemconfig(di1_air_t_id,   text=f"{d1.get('air_temp', 0):.1f}°C")
                canvas.itemconfig(di1_water_t_id, text=f"{d1.get('temp', 0):.1f}°C")
                canvas.itemconfig(di1_psi_t_id,   text=f"{d1.get('psi', 0):.1f}")

                # Right plots + text
                di2_ph.push(d2.get("ph", 0))
                di2_co2.push(d2.get("co2", 0))
                di2_psi.push(d2.get("psi", 0))
                canvas.itemconfig(di2_air_t_id,   text=f"{d2.get('air_temp', 0):.1f}°C")
                canvas.itemconfig(di2_water_t_id, text=f"{d2.get('temp', 0):.1f}°C")
                canvas.itemconfig(di2_psi_t_id,   text=f"{d2.get('psi', 0):.1f}")

            elif device == "doser":
                set_online("doser")
                doser_rate.push(data.get("dosing_rate", 0))

            elif device == "reactor":
                set_online("reactor")
                canvas.itemconfig(reactor_val_id, text=f"{data.get('flow', 0):.0f} L/min")

            elif device == "battery":
                soc = max(0, min(100, float(data.get("soc", 0))))
                canvas.itemconfig(battery_txt_id, text=f"Battery: {soc:.0f}%")

            elif device == "ve_direct":
                canvas.itemconfig(solar_txt_id, text=f"Solar total yield: {data.get('yield_total', 0):.0f}")

    except zmq.Again:
        pass
    except Exception as e:
        term_print(datetime.now().strftime("%H:%M:%S"), "err", "gui", "exception", "error", str(e))

    window.after(50, update_data)

window.after(50, update_data)

#runs it
window.mainloop()
