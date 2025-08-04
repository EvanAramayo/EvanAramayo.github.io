import pandas as pd
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button, PhotoImage, Label
import mplcursors as mpc

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def embed_figure(fig, master, x, y, w, h):
    canvas_fig = FigureCanvasTkAgg(fig, master=master)
    widget     = canvas_fig.get_tk_widget()
    widget.place(x=x, y=y, width=w, height=h)
    canvas_fig.draw()


# Peripheral
peripherals    = ["Reactor"]
current_index  = 0
cycle_count    = 1
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

# Load 
excel_path = OUTPUT_PATH / "RPI_Sensor_datalogs.xlsx"
all_sheets = pd.read_excel(excel_path, sheet_name=None)
sheets     = {}

for name, df in all_sheets.items():
    if "Unnamed: 1" in df.columns:
        df.rename(columns={"Unnamed: 1":"timestamp"}, inplace=True)
        if isinstance(df["timestamp"].iloc[0], str) and "timestamp" in df["timestamp"].iloc[0].lower():
            df = df.drop(index=0).reset_index(drop=True)
        df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")
    sheets[name] = df

reactor = sheets["reactor_raw_data"].copy()
reactor.rename(columns={"Unnamed: 3":"flow"}, inplace=True)

doser = sheets["doser_raw_data"].copy()
doser.rename(columns={"Unnamed: 3":"dosing_rate"}, inplace=True)

def prep_di(raw, proc):
    for d in (raw, proc):
        d.drop(index=0, inplace=True, errors="ignore")
        d.reset_index(drop=True, inplace=True)
        d.rename(columns={"Unnamed: 4":"ph", "Unnamed: 7":"co2", "Unnamed: 9":"ec"}, inplace=True)
        d["datetime"] = pd.to_datetime(d["timestamp"], errors="coerce")
    return raw, proc

di1_raw, di1_proc = prep_di(sheets["di-sea_1_raw_data"], sheets["di-sea_1_processed_data"])
di2_raw, di2_proc = prep_di(sheets["di-sea_2_raw_data"], sheets["di-sea_2_processed_data"])

ve = sheets["ve_direct_raw_data"].copy()
if isinstance(ve["timestamp"].iloc[0], str) and "timestamp" in ve["timestamp"].iloc[0].lower():
    ve.drop(index=0, inplace=True)
    ve.reset_index(drop=True, inplace=True)
hdr = all_sheets["ve_direct_raw_data"].iloc[0].to_dict()
yield_col = next((c for c,v in hdr.items() if "yield" in str(v).lower()), None)
if yield_col:
    ve.rename(columns={yield_col:"total_solar_yield"}, inplace=True)
else:
    ve["total_solar_yield"] = float("nan")

# GUI 
window = Tk()
window.geometry("1153x802")
window.configure(bg="#2A2F4F")

canvas = Canvas(window, bg="#2A2F4F", height=802, width=1153,
                bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Top bar & logo
canvas.create_rectangle(0, 5, 1151, 96, fill="#E5BEEC", outline="")
raw_img  = Image.open(relative_to_assets("image_1.png"))
resized  = raw_img.resize((170, 90), Image.LANCZOS)
logo_img = ImageTk.PhotoImage(resized)
Label(window, image=logo_img, bg="#E5BEEC").place(x=0, y=-4)

# Start/Stop buttons
btn1 = PhotoImage(file=relative_to_assets("button_1.png"))
Button(image=btn1, borderwidth=0, highlightthickness=0,
       command=start_system, relief="flat").place(x=8,   y=101, width=81, height=40)
btn2 = PhotoImage(file=relative_to_assets("button_2.png"))
Button(image=btn2, borderwidth=0, highlightthickness=0,
       command=stop_system, relief="flat").place(x=97,  y=101, width=81, height=40)

# Layout rectangles
canvas.create_rectangle(8,   151, 411,  519, fill="#917FB3", outline="")  # DI-SEA 1
canvas.create_rectangle(416, 153, 819,  519, fill="#5F4A87", outline="")  # DI-SEA 2
canvas.create_rectangle(8,   530, 308,  792, fill="#5F4A87", outline="")  # Doser Peripheral
canvas.create_rectangle(316, 529, 616,  654, fill="#917FB3", outline="")  # Reactor Peripheral

# System Power Metrics under Reactor Peripheral
canvas.create_rectangle(316, 660, 616, 785, fill="#5F4A87", outline="")   # System Power Metrics

canvas.create_rectangle(822, 152,1148,  392, fill="#5F4A87", outline="")  # Peripheral Status
canvas.create_rectangle(822, 152,1147,  185, fill="#917FB3", outline="")  # Status Header
canvas.create_rectangle(822, 399,1145,  524, fill="#917FB3", outline="")  # Terminal Area
canvas.create_rectangle(825, 398,1144,  421, fill="#5F4A87", outline="")  # Terminal Header

# Cycle label & number
canvas.create_rectangle(1010, 98, 1145, 143, fill="#917FB3", outline="")
canvas.create_text(1032, 107, anchor="nw", text="Cycle:", fill="#FFFFFF", font=("Inter Bold", -22))
cycle_text_id = canvas.create_text(1100,107, anchor="nw", text=str(cycle_count),
                                   fill="#FFFFFF", font=("Inter Bold", -22))

# Section titles
canvas.create_text(158, 147, anchor="nw", text="DI-SEA 1",           fill="#FFFFFF", font=("Inter Bold", -22))
canvas.create_text(574, 152, anchor="nw", text="DI-SEA 2",           fill="#FFFFFF", font=("Inter Bold", -22))
canvas.create_text(77,  529, anchor="nw", text="Doser Peripheral",   fill="#A34D18", font=("Inter Bold", -20))
canvas.create_text(377, 529, anchor="nw", text="Reactor Peripheral", fill="#27EF00", font=("Inter Bold", -20))
canvas.create_text(330, 665, anchor="nw", text="System Power Metrics", fill="#FFC300", font=("Inter Bold", -18))
canvas.create_text(915, 397, anchor="nw", text="Peripheral Status",  fill="#DC1A51", font=("Inter Bold", -17))

# Status headers
for x, label in [(828, "Time"), (938, "DeviceName"), (1052, "Error")]:
    canvas.create_text(x, 157, anchor="nw", text=label, fill="#FFFFFF", font=("Inter Bold", -15))
canvas.create_rectangle(935, 184, 936, 392, fill="#FFFFFF", outline="")
canvas.create_rectangle(1033,184,1034,392, fill="#FFFFFF", outline="")

# ——————————————————————————————
# Embed Plots
# ——————————————————————————————
# DI-SEA 1 plots
for (x,y,name,color,raw,proc) in [
    (140,190,"co2","#FF6B6B",di1_raw,di1_proc),
    (8,245,"ec","#5F4A87",di1_raw,di1_proc),
    (8,339,"ph","#E5BEEC",di1_raw,di1_proc),
]:
    fig = Figure(dpi=80); ax = fig.add_subplot(111)
    l1 = ax.plot(raw["datetime"],  raw[name],  label="Raw",       color=color)
    l2 = ax.plot(proc["datetime"], proc[name], label="Processed", color="#27EF00")
    ax.set_title(name.upper(), color="#FFFFFF", fontsize=10)
    ax.legend(fontsize=6, loc="upper right")
    ax.tick_params(labelsize=8, rotation=20)
    mpc.cursor(l1 + l2, hover=True)
    embed_figure(fig, window, x, y, 170, 94)

# DI-SEA 2 plots
for (x,y,name,color,raw,proc) in [
    (421,158,"co2","#FF6B6B",di2_raw,di2_proc),
    (421,253,"ec","#5F4A87",di2_raw,di2_proc),
    (421,348,"ph","#E5BEEC",di2_raw,di2_proc),
]:
    fig = Figure(dpi=80); ax = fig.add_subplot(111)
    l1 = ax.plot(raw["datetime"],  raw[name],  label="Raw",       color=color)
    l2 = ax.plot(proc["datetime"], proc[name], label="Processed", color="#27EF00")
    ax.set_title(name.upper(), color="#FFFFFF", fontsize=10)
    ax.legend(fontsize=6, loc="upper right")
    ax.tick_params(labelsize=8, rotation=20)
    mpc.cursor(l1 + l2, hover=True)
    embed_figure(fig, window, x, y, 170, 94)

# Doser Rate plot
fig_d = Figure(dpi=100); ax_d = fig_d.add_subplot(111)
l     = ax_d.plot(doser["datetime"], doser["dosing_rate"], color="#FFC300")
ax_d.set_title("Doser Rate", color="#FFFFFF")
ax_d.set_xlabel("Time")
mpc.cursor(l, hover=True)
embed_figure(fig_d, window, 8, 560, 300, 143)

# Flow value 
flow_value = float(reactor["flow"].iloc[-1])
canvas.create_text(400, 590, anchor="nw",
                   text=f"Flow: {flow_value:.2f} L/Min",
                   fill="#FFFFFF", font=("Inter Bold", -20))

# Solar Yield 
total_yield = float(ve["total_solar_yield"].iloc[-1])
canvas.create_text(330, 700, anchor="nw",
                   text="Yield:", fill="#FFFFFF", font=("Inter Bold", -18))
canvas.create_text(330, 730, anchor="nw",
                   text=f"{total_yield:.2f}", fill="#FFFFFF", font=("Inter Bold", -18))

window.title("Vycarb GUI")
window.resizable(False, False)
window.mainloop()
