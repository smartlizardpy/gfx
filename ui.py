import json
import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import websockets

# Load data from JSON file
try:
    with open("names.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    names_list = list(data.keys())
except FileNotFoundError:
    messagebox.showerror("Error", "File 'names.json' not found!")
    names_list = []
except json.JSONDecodeError:
    messagebox.showerror("Error", "Error decoding JSON data!")
    names_list = []

# WebSocket URI
WEBSOCKET_URI = "ws://localhost:8081"

ticker_running = False  # Keeps track of ticker state

async def send_to_websocket(message):
    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")
    except Exception as e:
        messagebox.showerror("WebSocket Error", f"Could not send data: {e}")

# Function to update the instrument and song list when a name is selected
def update_instrument_and_songs(event):
    selected_name = combobox_name.get()
    if selected_name in data:
        instrument = data[selected_name].get("instrument", "Unknown")
        songs = [piece["piece"] for piece in data[selected_name].get("pieces", [])]
        label_instrument_var.set(instrument)
        combobox_song["values"] = songs
        combobox_song.set("")  # Reset song selection
    else:
        label_instrument_var.set("Unknown")
        combobox_song["values"] = []
        combobox_song.set("")

def send_lower_thirds():
    selected_name = combobox_name.get()
    selected_song = combobox_song.get()
    instrument = label_instrument_var.get()

    if selected_name and instrument and selected_song:
        lower_thirds = {
            "type": "lower-thirds",
            "name": selected_name,
            "instrument": instrument,
            "song": selected_song
        }
        asyncio.run(send_to_websocket(lower_thirds))
    else:
        messagebox.showwarning("Incomplete Data", "Please fill in all fields.")

def toggle_ticker():
    """Toggle the ticker on and off."""
    global ticker_running
    if ticker_running:
        # Stop the ticker
        ticker_running = False
        stop_ticker = {
            "type": "ticker",
            "message": "",  # Send an empty message to stop the ticker
            "speed": 0,
            "action":"hide"
        }
        asyncio.run(send_to_websocket(stop_ticker))
        btn_toggle_ticker.config(text="Start Ticker")  # Update button text
        print("Ticker stopped")
    else:
        # Start the ticker
        selected_ticker_type = ticker_type_var.get()
        if selected_ticker_type == "Names":
            message = ", ".join(names_list)
            start_ticker = {
                "type": "ticker",
                "message": message,
                "speed": 1  ,
                "action":"show"
                # Adjust speed for names ticker
            }
        elif selected_ticker_type == "Message":
            message = entry_ticker.get()
            if not message:
                messagebox.showwarning("Incomplete Data", "Please enter a ticker message.")
                return
            start_ticker = {
                "type": "ticker",
                "message": message,
                "speed": 10 ,
                 "action":"show" # Adjust speed for message ticker
            }
        else:
            messagebox.showwarning("Invalid Option", "Please select a ticker type.")
            return
        
        ticker_running = True
        asyncio.run(send_to_websocket(start_ticker))
        btn_toggle_ticker.config(text="Stop Ticker")  # Update button text
        print("Ticker started with message:", message)

# Tkinter Application
root = tk.Tk()
root.title("Live Stream GFX Control")
root.geometry("800x600")

# Lower Thirds Section
lower_thirds_frame = tk.LabelFrame(root, text="Lower Thirds Control", padx=10, pady=10)
lower_thirds_frame.pack(pady=10, fill="x")

# Name Combobox
label_name = tk.Label(lower_thirds_frame, text="Name:")
label_name.grid(row=0, column=0, padx=5, pady=5, sticky="e")
combobox_name = ttk.Combobox(lower_thirds_frame, values=names_list, state="readonly", width=30)
combobox_name.grid(row=0, column=1, padx=5, pady=5)
combobox_name.bind("<<ComboboxSelected>>", update_instrument_and_songs)

# Instrument Label
label_instrument = tk.Label(lower_thirds_frame, text="Instrument:")
label_instrument.grid(row=1, column=0, padx=5, pady=5, sticky="e")
label_instrument_var = tk.StringVar()
label_instrument_display = tk.Label(lower_thirds_frame, textvariable=label_instrument_var)
label_instrument_display.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Song Combobox
label_song = tk.Label(lower_thirds_frame, text="Song:")
label_song.grid(row=2, column=0, padx=5, pady=5, sticky="e")
combobox_song = ttk.Combobox(lower_thirds_frame, state="readonly", width=30)
combobox_song.grid(row=2, column=1, padx=5, pady=5)

# Send Lower Thirds Button
btn_send_lower_thirds = tk.Button(lower_thirds_frame, text="Send Lower Thirds", command=send_lower_thirds)
btn_send_lower_thirds.grid(row=3, column=0, columnspan=2, pady=10)

# Ticker Section
ticker_frame = tk.LabelFrame(root, text="Ticker Control", padx=10, pady=10)
ticker_frame.pack(pady=10, fill="x")

# Ticker Type Selection
label_ticker_type = tk.Label(ticker_frame, text="Ticker Type:")
label_ticker_type.grid(row=0, column=0, padx=5, pady=5, sticky="e")
ticker_type_var = tk.StringVar(value="Message")
ticker_type_options = ["Names", "Message"]
combobox_ticker_type = ttk.Combobox(ticker_frame, values=ticker_type_options, state="readonly", textvariable=ticker_type_var)
combobox_ticker_type.grid(row=0, column=1, padx=5, pady=5)

# Ticker Message Entry
label_ticker = tk.Label(ticker_frame, text="Message:")
label_ticker.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_ticker = tk.Entry(ticker_frame, width=50)
entry_ticker.grid(row=1, column=1, padx=5, pady=5)

# Toggle Ticker Button
btn_toggle_ticker = tk.Button(ticker_frame, text="Start Ticker", command=toggle_ticker)
btn_toggle_ticker.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()