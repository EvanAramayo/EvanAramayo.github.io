import pandas as pd
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button, Label
from tkinter.scrolledtext import ScrolledText
import zmq
import json
import logging
import mplcursors as mpc

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def embed_figure(fig, master, x, y, w, h):
    canvas_fig = FigureCanvasTkAgg(fig, master=master)
    widget = canvas_fig.get_tk_widget()
    widget.place(x=x, y=y, width=w, height=h)
    canvas_fig.draw()

# ——————————————————————————————
# Peripheral & System Logic
# ——————————————————————————————
peripherals = ["Reactor"]
current_index = 0
cycle_count = 1
system_running = False

def process_peripherals():
    global current_index, cycle_count
    if not system_running:
        return
    peripheral = peripherals[current_index]
    print(f"Processing {peripheral}...")
    current_index += 1
    if current_index >= len(peripherals):
        cycle_count += 1
        current_index = 0
        canvas.itemconfig(cycle_text_id, text=str(cycle_count))
        print(f"Cycle {cycle_count} complete.")
    window.after(2000, process_peripherals)

def start_system():
    global system_running
    if not system_running:
        system_running = True
        print("System started.")
        process_peripherals()

def stop_system():
    global system_running
    system_running = False
    print("System stopped.")

# ——————————————————————————————
# GUI Setup
# ——————————————————————————————
window = Tk()
window.geometry("1153x802")
window.configure(bg="#2A2F4F")
canvas = Canvas(window, bg="#2A2F4F", height=802, width=1153,
                bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Top bar & logo
canvas.create_rectangle(0, -5, 1151, 96, fill="#E5BEEC", outline="")
raw_img = Image.open(relative_to_assets("image_1.png"))
resized = raw_img.resize((295, 90), Image.LANCZOS)
logo_img = ImageTk.PhotoImage(resized)
Label(window, image=logo_img, bg="#E5BEEC").place(x=0, y=-4)

# Start/Stop buttons
btn1 = ImageTk.PhotoImage(file=relative_to_assets("button_1.png"))
Button(image=btn1, borderwidth=0, highlightthickness=0,
       command=start_system, relief="flat").place(x=8, y=101, width=81, height=40)
btn2 = ImageTk.PhotoImage(file=relative_to_assets("button_2.png"))
Button(image=btn2, borderwidth=0, highlightthickness=0,
       command=stop_system, relief="flat").place(x=97, y=101, width=81, height=40)

# Layout rectangles
canvas.create_rectangle(8, 151, 411, 519, fill="#917FB3", outline="")   # DI-SEA 1
canvas.create_rectangle(416, 153, 819, 519, fill="#5F4A87", outline="")   # DI-SEA 2
canvas.create_rectangle(8, 530, 308, 792, fill="#5F4A87", outline="")   # Doser Peripheral
canvas.create_rectangle(316, 529, 616, 654, fill="#917FB3", outline="")   # Reactor Peripheral
canvas.create_rectangle(316, 660, 616, 785, fill="#5F4A87", outline="")   # System Power Metrics
canvas.create_rectangle(822, 152, 1148, 392, fill="#5F4A87", outline="")   # Peripheral Status
canvas.create_rectangle(822, 152, 1147, 185, fill="#917FB3", outline="")   # Status Header
canvas.create_rectangle(822, 525, 1145, 792, fill="#917FB3", outline="")   # Bottom-right blank area (terminal)

# Cycle label & number
canvas.create_rectangle(1010, 98, 1145, 143, fill="#917FB3", outline="")
canvas.create_text(1032, 107, anchor="nw", text="Cycle:", fill="#FFFFFF", font=("Inter Bold", -22))
cycle_text_id = canvas.create_text(1100, 107, anchor="nw", text=str(cycle_count),
                                   fill="#FFFFFF", font=("Inter Bold", -22))

# Section titles
canvas.create_text(158, 147, anchor="nw", text="DI-SEA 1", fill="#FFFFFF", font=("Inter Bold", -22))
canvas.create_text(574, 152, anchor="nw", text="DI-SEA 2", fill="#FFFFFF", font=("Inter Bold", -22))
canvas.create_text(77, 529, anchor="nw", text="Doser Peripheral", fill="#A34D18", font=("Inter Bold", -20))
canvas.create_text(377, 529, anchor="nw", text="Reactor Peripheral", fill="#27EF00", font=("Inter Bold", -20))
canvas.create_text(330, 665, anchor="nw", text="System Power Metrics", fill="#FFC300", font=("Inter Bold", -18))
canvas.create_text(915, 397, anchor="nw", text="Peripheral Status", fill="#DC1A51", font=("Inter Bold", -17))

# Status headers
for x, label in [(828, "Time"), (938, "DeviceName"), (1052, "Error")]:
    canvas.create_text(x, 157, anchor="nw", text=label, fill="#FFFFFF", font=("Inter Bold", -15))
canvas.create_rectangle(935, 184, 936, 392, fill="#FFFFFF", outline="")
canvas.create_rectangle(1033, 184, 1034, 392, fill="#FFFFFF", outline="")

# ——————————————————————————————
# Terminal for Device Simulator Data (bottom-right blank rectangle)
# ——————————————————————————————
terminal_text = ScrolledText(window, bg="#0D1117", fg="white", font=("Consolas", 10))
terminal_text.place(x=825, y=530, width=319, height=260)  # fully inside the blank rectangle below Peripheral Status
terminal_text.insert("end", "Waiting for device simulator data...\n")
terminal_text.configure(state="disabled")

# ——————————————————————————————
# ZMQ Subscriber Setup
# ——————————————————————————————
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.setsockopt(zmq.RCVTIMEO, 10)

def update_data():
    """Read data from ZMQ and update terminal"""
    try:
        received = socket.recv_string(zmq.NOBLOCK)
        topic = received.split("|")[0]
        data = json.loads(received.split("|")[1])
        terminal_text.configure(state="normal")
        terminal_text.insert("end", f"{topic}: {json.dumps(data)}\n")
        terminal_text.see("end")  # auto-scroll
        terminal_text.configure(state="disabled")
    except zmq.Again:
        pass  # no message
    except Exception as e:
        terminal_text.configure(state="normal")
        terminal_text.insert("end", f"Error reading data: {e}\n")
        terminal_text.see("end")
        terminal_text.configure(state="disabled")
    window.after(50, update_data)

# ——————————————————————————————
# Start updating data
# ——————————————————————————————
window.after(50, update_data)

# ——————————————————————————————
# Run GUI
# ——————————————————————————————
window.title("Vycarb GUI")
window.resizable(False, False)
window.mainloop()
