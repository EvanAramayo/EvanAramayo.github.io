import pandas as pd
from pandas.api import types as ptypes
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, Button, PhotoImage, Label
import mplcursors as mpc



# Set up asset paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# GUI Setup
window = Tk()
window.geometry("950x600")
window.configure(bg="#2A2F4F")

canvas = Canvas(
    window,
    bg="#2A2F4F",
    height=600,
    width=950,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)

# Background Top Bar
canvas.create_rectangle(0.0, 0.0, 950.0, 90, fill="#E5BEEC", outline="")

# Button and image loading
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: start_system(),
    relief="flat"
)
button_1.place(x=8.0, y=98.0, width=81.0, height=40.0)

button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: stop_system(),
    relief="flat"
)
button_2.place(x=97.0, y=101.0, width=81.0, height=40.0)

### Vycarb logoooool

logo_path = relative_to_assets("image_1.png")
raw_img   = Image.open(logo_path)

#the size
resized_img = raw_img.resize((170, 90), Image.LANCZOS)
logo_img    = ImageTk.PhotoImage(resized_img)

logo_label = Label(window, image=logo_img, bg="#E5BEEC")
logo_label.image = logo_img
logo_label.place(x=0, y=-4)  #position

#the GUI elements
canvas.create_rectangle(8.0, 151.0, 308.0, 434.0, fill="#917FB3", outline="")
canvas.create_rectangle(8.0, 448.0, 308.0, 591.0, fill="#5F4A87", outline="")
canvas.create_rectangle(313.0, 448.0, 613.0, 591.0, fill="#917FB3", outline="")
canvas.create_rectangle(313.0, 150.0, 613.0, 434.0, fill="#5F4A87", outline="")
canvas.create_rectangle(618.0, 150.0, 944.0, 339.0, fill="#5F4A87", outline="")
canvas.create_rectangle(809.0, 95.0, 944.0, 140.0, fill="#917FB3", outline="")

canvas.create_text(831.0, 104.0, anchor="nw", text="Cycle:", fill="#FFFFFF", font=("Inter Bold", 22 * -1))
cycle_display = canvas.create_text(
    940.0, 104.0,
    anchor="ne",
    text="1",
    fill="#FFFFFF",
    font=("Inter Bold", 22 * -1)
)

canvas.create_rectangle(618.0, 150.0, 943.0, 183.0, fill="#917FB3", outline="")
canvas.create_text(624.0, 155.0, anchor="nw", text="Time", fill="#FFFFFF", font=("Inter Bold", 15 * -1))
canvas.create_text(734.0, 155.0, anchor="nw", text="DeviceName", fill="#FFFFFF", font=("Inter Bold", 15 * -1))
canvas.create_text(855.0, 155.0, anchor="nw", text="Error", fill="#FFFFFF", font=("Inter Bold", 15 * -1))
canvas.create_rectangle(731.0, 182.0, 732.0, 339.0, fill="#FFFFFF", outline="")
canvas.create_rectangle(829.0, 182.0, 830.0, 339.0, fill="#FFFFFF", outline="")
canvas.create_rectangle(621.0, 513.0, 944.0, 593.0, fill="#5F4A87", outline="")
canvas.create_rectangle(621.0, 347.0, 944.0, 503.0, fill="#917FB3", outline="")
canvas.create_rectangle(624.0, 346.0, 943.0, 369.0, fill="#5F4A87", outline="")
canvas.create_text(714.0, 345.0, anchor="nw", text="Peripheral Status", fill="#DC1A51", font=("Inter Bold", 17 * -1))
canvas.create_rectangle(8.0, 150.0, 308.0, 186.0, fill="#5F4A87", outline="")
canvas.create_rectangle(312.0, 148.0, 612.0, 184.0, fill="#917FB3", outline="")
canvas.create_text(414.0, 147.0, anchor="nw", text="DI-SEA 2", fill="#FFFFFF", font=("Inter Bold", 22 * -1))
canvas.create_text(115.0, 148.0, anchor="nw", text="DI-SEA 1", fill="#FFFFFF", font=("Inter Bold", 22 * -1))
canvas.create_text(687.0, 511.0, anchor="nw", text="System Power Metrics", fill="#FFC300", font=("Inter Bold", 18 * -1))
canvas.create_text(378.0, 453.0, anchor="nw", text="Reactor Peripheral ", fill="#27EF00", font=("Inter Bold", 20 * -1))
canvas.create_text(77.0, 453.0, anchor="nw", text="Doser Peripheral ", fill="#EF7000", font=("Inter Bold", 20 * -1))
canvas.create_text(178.0, 321.0, anchor="nw", text="Air temp: \nWater temp:\nPressure: ", fill="#FFFFFF", font=("Inter Bold", 15 * -1))
canvas.create_text(486.0, 329.0, anchor="nw", text="Air temp: \nWater temp:\nPressure: ", fill="#FFFFFF", font=("Inter Bold", 15 * -1))

# Peripheral Logic
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
        canvas.itemconfig(cycle_display, text=str(cycle_count))
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

# window frame
window.title("Vycarb GUI")
window.resizable(False, False)

##PLOTING UGHHH

# Load
excel_path = Path(__file__).parent / "RPI_Sensor_datalogs.xlsx"
all_sheets = pd.read_excel(excel_path, sheet_name=None)

sheets = {}
for name, df in all_sheets.items():
    # Rename 
    if "Unnamed: 1" in df.columns:
        df.rename(columns={"Unnamed: 1": "timestamp"}, inplace=True)

        # Drop embedded header row inside data
        if isinstance(df["timestamp"].iloc[0], str) and "timestamp" in df["timestamp"].iloc[0].lower():
            df = df.drop(index=0).reset_index(drop=True)

        # Convert to datetime
        df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")

    sheets[name] = df

# this cleans up sheets and renames columns for easier access because they were named the wrong things in the csv file 
reactor = sheets["reactor_raw_data"].copy()
reactor.rename(columns={"Unnamed: 3": "flow"}, inplace=True)

doser = sheets["doser_raw_data"].copy()
doser.rename(columns={"Unnamed: 3": "dosing_rate"}, inplace=True)

di1_raw = sheets["di-sea_1_raw_data"].copy()
di1_raw = di1_raw.drop(index=0).reset_index(drop=True)
di1_raw.rename(columns={"Unnamed: 4": "ph", "Unnamed: 1": "timestamp"}, inplace=True)
di1_raw["datetime"] = pd.to_datetime(di1_raw["timestamp"], errors="coerce")

di2_raw = sheets["di-sea_2_raw_data"].copy()
di2_raw = di2_raw.drop(index=0).reset_index(drop=True)
di2_raw.rename(columns={"Unnamed: 4": "ph", "Unnamed: 1": "timestamp"}, inplace=True)
di2_raw["datetime"] = pd.to_datetime(di2_raw["timestamp"], errors="coerce")

di1_proc = sheets["di-sea_1_processed_data"].copy()
di1_proc = di1_proc.drop(index=0).reset_index(drop=True)
di1_proc.rename(columns={"Unnamed: 4": "ph", "Unnamed: 1": "timestamp"}, inplace=True)
di1_proc["datetime"] = pd.to_datetime(di1_proc["timestamp"], errors="coerce")

di2_proc = sheets["di-sea_2_processed_data"].copy()
di2_proc = di2_proc.drop(index=0).reset_index(drop=True)
di2_proc.rename(columns={"Unnamed: 4": "ph", "Unnamed: 1": "timestamp"}, inplace=True)
di2_proc["datetime"] = pd.to_datetime(di2_proc["timestamp"], errors="coerce")

# Embed helper
def embed_figure(fig, x, y, w, h):
    canvas_fig = FigureCanvasTkAgg(fig, master=window)
    widget = canvas_fig.get_tk_widget()
    widget.place(x=x, y=y, width=w, height=h)
    canvas_fig.draw()

# Embed helper
def embed_figure(fig, x, y, w, h):
    canvas_fig = FigureCanvasTkAgg(fig, master=window)
    widget = canvas_fig.get_tk_widget()
    widget.place(x=x, y=y, width=w, height=h)
    canvas_fig.draw()



#Plotting UGHHHH

di1_raw.rename(columns={"Unnamed: 7": "co2", "Unnamed: 9": "ec"}, inplace=True)
di2_raw.rename(columns={"Unnamed: 7": "co2", "Unnamed: 9": "ec"}, inplace=True)

# DI-SEA 1 CO₂ (raw & processed)
fig1_co2 = Figure(dpi=80)
ax1_co2 = fig1_co2.add_subplot(111)
line1 = ax1_co2.plot(di1_raw["datetime"],  di1_raw["co2"],  label="Raw",       color="#FF6B6B")
line2 = ax1_co2.plot(di1_proc["datetime"], di1_proc["co2"], label="Processed", color="#27EF00")
ax1_co2.set_title("CO₂", color="#FFFFFF", fontsize=10)
ax1_co2.legend(fontsize=6, loc="upper right")
ax1_co2.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig1_co2, x=140, y=190, w=170, h=94)

# DI-SEA 1 EC (raw & processed)
fig1_ec = Figure(dpi=80)
ax1_ec = fig1_ec.add_subplot(111)
line1 = ax1_ec.plot(di1_raw["datetime"],  di1_raw["ec"],  label="Raw",       color="#5F4A87")
line2 = ax1_ec.plot(di1_proc["datetime"], di1_proc["ec"], label="Processed", color="#FFC300")
ax1_ec.set_title("EC", color="#FFFFFF", fontsize=10)
ax1_ec.legend(fontsize=6, loc="upper right")
ax1_ec.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig1_ec, x=8, y=245, w=170, h=94)

# DI-SEA 1 pH (raw & processed)
fig1_ph = Figure(dpi=80)
ax1_ph = fig1_ph.add_subplot(111)
line1 = ax1_ph.plot(di1_raw["datetime"],  di1_raw["ph"],  label="Raw",       color="#E5BEEC")
line2 = ax1_ph.plot(di1_proc["datetime"], di1_proc["ph"], label="Processed", color="#27EF00")
ax1_ph.set_title("pH", color="#FFFFFF", fontsize=10)
ax1_ph.legend(fontsize=6, loc="upper right")
ax1_ph.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig1_ph, x=8, y=339, w=170, h=94)

# DI-SEA 2 CO₂ (raw & processed)
fig2_co2 = Figure(dpi=80)
ax2_co2 = fig2_co2.add_subplot(111)
line1 = ax2_co2.plot(di2_raw["datetime"],  di2_raw["co2"],  label="Raw",       color="#FF6B6B")
line2 = ax2_co2.plot(di2_proc["datetime"], di2_proc["co2"], label="Processed", color="#27EF00")
ax2_co2.set_title("CO₂", color="#FFFFFF", fontsize=10)
ax2_co2.legend(fontsize=6, loc="upper right")
ax2_co2.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig2_co2, x=313, y=150, w=170, h=95)

# DI-SEA 2 EC (raw & processed)
fig2_ec = Figure(dpi=80)
ax2_ec = fig2_ec.add_subplot(111)
line1 = ax2_ec.plot(di2_raw["datetime"],  di2_raw["ec"],  label="Raw",       color="#5F4A87")
line2 = ax2_ec.plot(di2_proc["datetime"], di2_proc["ec"], label="Processed", color="#FFC300")
ax2_ec.set_title("EC", color="#FFFFFF", fontsize=10)
ax2_ec.legend(fontsize=6, loc="upper right")
ax2_ec.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig2_ec, x=313, y=245, w=170, h=94)

# DI-SEA 2 pH (raw & processed)
fig2_ph = Figure(dpi=80)
ax2_ph = fig2_ph.add_subplot(111)
line1 = ax2_ph.plot(di2_raw["datetime"],  di2_raw["ph"],  label="Raw",       color="#E5BEEC")
line2 = ax2_ph.plot(di2_proc["datetime"], di2_proc["ph"], label="Processed", color="#FFC300")
ax2_ph.set_title("pH", color="#FFFFFF", fontsize=10)
ax2_ph.legend(fontsize=6, loc="upper right")
ax2_ph.tick_params(labelsize=8, rotation=20)
mpc.cursor(line1 + line2, hover=True)
embed_figure(fig2_ph, x=313, y=339, w=170, h=95)

# Doser
fig_d = Figure(dpi=100)
ax_d = fig_d.add_subplot(111)
line = ax_d.plot(doser["datetime"], doser["dosing_rate"], color="#FFC300")
ax_d.set_title("Doser Rate", color="#FFFFFF")
ax_d.set_xlabel("Time")
mpc.cursor(line, hover=True)
embed_figure(fig_d, x=8, y=448, w=300, h=143)


# 1) Reactor Flow Value
flow_value = float(reactor["flow"].iloc[-1])  # last reading
canvas.create_text(
    378.0, 503.0,
    anchor="nw",
    text=f"Flow: {flow_value:.2f} L/Min",
    fill="#FFFFFF",
    font=("Inter Bold", 20 * -1)
)

# 2) Total Solar Yield 
ve = sheets["ve_direct_raw_data"].copy()

# If the first row is a stray header, drop it
if isinstance(ve["timestamp"].iloc[0], str) and "timestamp" in ve["timestamp"].iloc[0].lower():
    ve = ve.drop(index=0).reset_index(drop=True)

# Identify which column header contains the word "yield"
header_row = all_sheets["ve_direct_raw_data"].iloc[0]
yield_col = next((col for col, val in header_row.items()
                  if "yield" in str(val).lower()), None)

# Renames the column to something we can reference
if yield_col:
    ve.rename(columns={yield_col: "total_solar_yield"}, inplace=True)
else:
    ve["total_solar_yield"] = float("nan")

# Grab the last total‐yield value
total_yield = float(ve["total_solar_yield"].iloc[-1])

canvas.create_text(
    687.0, 557.0,
    anchor="nw",
    text=f"Yield: {total_yield:.2f}",
    fill="#FFFFFF",
    font=("Inter Bold", 18 * -1)
)
window.mainloop()

