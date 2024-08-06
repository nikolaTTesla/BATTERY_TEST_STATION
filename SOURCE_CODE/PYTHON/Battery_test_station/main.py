'''
Battery Cycling Test
Created by: Nikola Japundzic
Date created: 02-20-24
Last modify date: 06-10-24, Rev 23
Reading/Writing, serial, python/arduino(or similar)
'''

'''
Type in the terminal to generate standalomne app:
pyinstaller --noconsole --onefile --windowed --icon logo.icns --name Battery_data_aquisition Battery_test_006.py

with consol:
pyinstaller --onefile --windowed --icon logo.icns --name Battery_data_aquisition Battery_test_006.py 

or run instaler.py file, but make sure that "dist" and "build" folder do not exist
or run instaler.py file, but make sure that dist" and "build" folder do not exist
'''
import sys
import time
import serial
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from serial.tools import list_ports
import os
from datetime import datetime
import json
import Converting_csv_to_xlxs

name_JSON_Settings = 'settings_file_battery_test'

#create Gui with starting json
global_cycles_string = '1'
global_sampling_time_string = '1'
global_charging_length_string = '1'
global_discharging_length_string = '1'
global_port_combobox_string = ''
global_port_combobox_baud_string = 250000
serial_data = ''
global_text_widget_path_for_csv = ''
global_5_min_checkbox_state = False

# Global variable to hold the serial connection
ser = None
filename_sample_time = None
filename_capacity = None
filename_sample_time_per_10_x_smaller = None
received_data = []
pause_bool = False
thread_killer = False


global_array_capacity_currents_1 = [0, 0, 0, 0, 0, 0, 0, 0]
global_array_capacity_currents_2 = [0, 0, 0, 0, 0, 0, 0, 0]
global_discharge_first_capacity = [0, 0, 0, 0, 0, 0, 0, 0]

def count_all_lines():
    total_lines = text_terminal_print.index('end-1c').split('.')[0]#count_all_lines_inside terminal
    return int(total_lines)
def delete_first_line():
    text_terminal_print.delete("1.0", "2.0")#delete_first_line
def keep100lines():
    while count_all_lines() > 101:
        delete_first_line()
def write_on_terminal_widget(value):
    text_terminal_print.configure(state='normal')
    text_terminal_print.insert(tk.END, value)  # Insert received data into Text widget
    keep100lines()
    text_terminal_print.configure(state='disable')
def open_admin_dialog():
    def validate_text_text_widget_number_of_cycles(event=None):
        new_value = text_widget_number_of_cycles.get("1.0", "end-1c")

        # Limit input to 7 characters
        if len(new_value) > 6:
            new_value = new_value[:6]
            text_widget_number_of_cycles.delete("1.0", "end")
            text_widget_number_of_cycles.insert("1.0", new_value)

        # Check if the input is empty
        if new_value == "":
            text_widget_number_of_cycles.config(bg="red")
            return

        # Check if the first character is zero when the input is not empty
        if new_value[0] == '0':
            text_widget_number_of_cycles.delete("1.0", "end")
            text_widget_number_of_cycles.config(bg="red")
            return

        # Check if the input is a valid number
        if new_value.isdigit():
            value = int(new_value)
            if 1 <= value <= 1000000:
                text_widget_number_of_cycles.config(bg="green")
                return

        # If the input is not valid, set the background to red
        text_widget_number_of_cycles.config(bg="red")

        # Remove any non-digit characters
        corrected_value = ''.join(filter(str.isdigit, new_value))
        if corrected_value != new_value:
            text_widget_number_of_cycles.delete("1.0", "end")
            text_widget_number_of_cycles.insert("1.0", corrected_value)

        # Check if the corrected value is valid again
        if corrected_value:
            value = int(corrected_value)
            if 1 <= value <= 1000000:
                text_widget_number_of_cycles.config(bg="green")
            else:
                text_widget_number_of_cycles.config(bg="red")
        else:
            text_widget_number_of_cycles.config(bg="red")
    def insert_and_validate_text_text_widget_number_of_cycles(value):
        # Check if the value starts with zero
        if value and value[0] == '0':
            value = value.lstrip('0')
        text_widget_number_of_cycles.insert(tk.END, value)
        validate_text_text_widget_number_of_cycles()

    def validate_text_text_widget_sampling_time(event=None):
        new_value = text_widget_sampling_time.get("1.0", "end-1c")

        # Limit input to 7 characters
        if len(new_value) > 6:
            new_value = new_value[:6]
            text_widget_sampling_time.delete("1.0", "end")
            text_widget_sampling_time.insert("1.0", new_value)

        # Check if the input is empty
        if new_value == "":
            text_widget_sampling_time.config(bg="red")
            return

        # Check if the first character is zero when the input is not empty
        if new_value[0] == '0':
            text_widget_sampling_time.delete("1.0", "end")
            text_widget_sampling_time.config(bg="red")
            return

        # Check if the input is a valid number
        if new_value.isdigit():
            value = int(new_value)
            if 1 <= value <= 1000000:
                text_widget_sampling_time.config(bg="green")
                return

        # If the input is not valid, set the background to red
        text_widget_sampling_time.config(bg="red")

        # Remove any non-digit characters
        corrected_value = ''.join(filter(str.isdigit, new_value))
        if corrected_value != new_value:
            text_widget_sampling_time.delete("1.0", "end")
            text_widget_sampling_time.insert("1.0", corrected_value)

        # Check if the corrected value is valid again
        if corrected_value:
            value = int(corrected_value)
            if 1 <= value <= 1000000:
                text_widget_sampling_time.config(bg="green")
            else:
                text_widget_sampling_time.config(bg="red")
        else:
            text_widget_sampling_time.config(bg="red")
    def insert_and_validate_text_widget_sampling_time(value):
        # Check if the value starts with zero
        if value and value[0] == '0':
            value = value.lstrip('0')
        text_widget_sampling_time.insert(tk.END, value)
        validate_text_text_widget_sampling_time()

    def validate_text_widget_charging_length(event=None):
        new_value = text_widget_charging_length.get("1.0", "end-1c")

        # Limit input to 7 characters
        if len(new_value) > 6:
            new_value = new_value[:6]
            text_widget_charging_length.delete("1.0", "end")
            text_widget_charging_length.insert("1.0", new_value)

        # Check if the input is empty
        if new_value == "":
            text_widget_charging_length.config(bg="red")
            return

        # Check if the first character is zero when the input is not empty
        if new_value[0] == '0':
            text_widget_charging_length.delete("1.0", "end")
            text_widget_charging_length.config(bg="red")
            return

        # Check if the input is a valid number
        if new_value.isdigit():
            value = int(new_value)
            if 1 <= value <= 1000000:
                text_widget_charging_length.config(bg="green")
                return

        # If the input is not valid, set the background to red
        text_widget_charging_length.config(bg="red")

        # Remove any non-digit characters
        corrected_value = ''.join(filter(str.isdigit, new_value))
        if corrected_value != new_value:
            text_widget_charging_length.delete("1.0", "end")
            text_widget_charging_length.insert("1.0", corrected_value)

        # Check if the corrected value is valid again
        if corrected_value:
            value = int(corrected_value)
            if 1 <= value <= 1000000:
                text_widget_charging_length.config(bg="green")
            else:
                text_widget_charging_length.config(bg="red")
        else:
            text_widget_charging_length.config(bg="red")
    def insert_and_validate_text_widget_charging_length(value):
        # Check if the value starts with zero
        if value and value[0] == '0':
            value = value.lstrip('0')
        text_widget_charging_length.insert(tk.END, value)
        validate_text_widget_charging_length()

    def validate_text_widget_discharging_length(event=None):
        new_value = text_widget_discharging_length.get("1.0", "end-1c")

        # Limit input to 7 characters
        if len(new_value) > 6:
            new_value = new_value[:6]
            text_widget_discharging_length.delete("1.0", "end")
            text_widget_discharging_length.insert("1.0", new_value)

        # Check if the input is empty
        if new_value == "":
            text_widget_discharging_length.config(bg="red")
            return

        # Check if the first character is zero when the input is not empty
        if new_value[0] == '0':
            text_widget_discharging_length.delete("1.0", "end")
            text_widget_discharging_length.config(bg="red")
            return

        # Check if the input is a valid number
        if new_value.isdigit():
            value = int(new_value)
            if 1 <= value <= 1000000:
                text_widget_discharging_length.config(bg="green")
                return

        # If the input is not valid, set the background to red
        text_widget_discharging_length.config(bg="red")

        # Remove any non-digit characters
        corrected_value = ''.join(filter(str.isdigit, new_value))
        if corrected_value != new_value:
            text_widget_discharging_length.delete("1.0", "end")
            text_widget_discharging_length.insert("1.0", corrected_value)

        # Check if the corrected value is valid again
        if corrected_value:
            value = int(corrected_value)
            if 1 <= value <= 1000000:
                text_widget_discharging_length.config(bg="green")
            else:
                text_widget_discharging_length.config(bg="red")
        else:
            text_widget_discharging_length.config(bg="red")
    def insert_and_validate_text_widget_discharging_length(value):
        # Check if the value starts with zero
        if value and value[0] == '0':
            value = value.lstrip('0')
        text_widget_discharging_length.insert(tk.END, value)
        validate_text_widget_discharging_length()

    custom_font = ('Helvetica', 18)  # Adjust the size (12 here) as needed
    dialog = tk.Toplevel(root)
    dialog.title("Admin")
    dialog.resizable(width=False, height=False)  # disabeling user to resize the window

    #Save parameters method
    def save_state():

        global global_port_combobox_string, global_port_combobox_baud_string, global_discharging_length_string, global_charging_length_string, global_sampling_time_string, global_cycles_string,global_text_widget_path_for_csv

        global global_5_min_checkbox_state
        state['check_button_5_min_delay'] = checkbox_var_m_min.get()
        global_5_min_checkbox_state = checkbox_var_m_min.get()



        state['text'] = {
            'cursor': text_widget_path_for_csv.index(tk.INSERT),
            'selection': text_widget_path_for_csv.tag_ranges(tk.SEL),
            'content': text_widget_path_for_csv.get("1.0", tk.END)[:-1]
        }
        global_text_widget_path_for_csv = text_widget_path_for_csv.get("1.0", tk.END)
        global_text_widget_path_for_csv = global_text_widget_path_for_csv.replace('\n', '')
        print("global_text_widget_path_for_csv SAVE place",global_text_widget_path_for_csv)

        state['text_cycles'] = {
            'cursor': text_widget_number_of_cycles.index(tk.INSERT),
            'selection': text_widget_number_of_cycles.tag_ranges(tk.SEL),
            'content': text_widget_number_of_cycles.get("1.0", tk.END)[:-1]
        }
        print("global_text_widget_path_for_csv",global_text_widget_path_for_csv)
        global_cycles_string = state['text_cycles']  # getting from the top layer
        global_cycles_string = int(global_cycles_string['content'])

        state['text_sampling_time'] = {
            'cursor': text_widget_sampling_time.index(tk.INSERT),
            'selection': text_widget_sampling_time.tag_ranges(tk.SEL),
            'content': text_widget_sampling_time.get("1.0", tk.END)[:-1]
        }
        global_sampling_time_string = state['text_sampling_time']  # getting from the top layer
        global_sampling_time_string = int(global_sampling_time_string['content'])

        state['text_charging_length'] = {
            'cursor': text_widget_charging_length.index(tk.INSERT),
            'selection': text_widget_charging_length.tag_ranges(tk.SEL),
            'content': text_widget_charging_length.get("1.0", tk.END)[:-1]
        }
        global_charging_length_string = state['text_charging_length']  # getting from the top layer
        global_charging_length_string = int(global_charging_length_string['content'])

        state['text_discharging_length'] = {
            'cursor': text_widget_discharging_length.index(tk.INSERT),
            'selection': text_widget_discharging_length.tag_ranges(tk.SEL),
            'content': text_widget_discharging_length.get("1.0", tk.END)[:-1]
        }
        global_discharging_length_string = state['text_discharging_length']  # getting from the top layer
        global_discharging_length_string = int(global_discharging_length_string['content'])

        state['port_combobox_baud'] = port_combobox_baud_var.get()
        global_port_combobox_baud_string = port_combobox_baud_var.get()
        state['port_combobox'] = port_combobox_var.get()
        global_port_combobox_string = port_combobox_var.get()

        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        file_path = os.path.join(desktop, name_JSON_Settings+'.json')

        # with open('widget_state.json', 'w') as file:
        with open(file_path, 'w') as file:
            json.dump(state, file)

    #restore parameters
    def restore_state():
        global global_text_widget_path_for_csv
        try:
            desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
            file_path = os.path.join(desktop, name_JSON_Settings+'.json')
            print("file_path", file_path)
            with open(file_path, 'r') as file:
                print("RESTORE FOLDER CONTAINS JSON")
                saved_state = json.load(file)
                if 'text' in saved_state:
                    text_info = saved_state['text']
                    text_widget_path_for_csv.delete("1.0", tk.END)
                    text_widget_path_for_csv.insert("1.0", text_info['content'])
                    text_widget_path_for_csv.mark_set(tk.INSERT, text_info['cursor'])
                    if text_info['selection']:
                        text_widget_path_for_csv.tag_add(tk.SEL, *text_info['selection'])

                if 'text_cycles' in saved_state:
                    text_info = saved_state['text_cycles']
                    text_widget_number_of_cycles.delete("1.0", tk.END)
                    text_widget_number_of_cycles.insert("1.0", text_info['content'])
                    text_widget_number_of_cycles.mark_set(tk.INSERT, text_info['cursor'])
                    if text_info['selection']:
                        text_widget_number_of_cycles.tag_add(tk.SEL, *text_info['selection'])

                if 'text_sampling_time' in saved_state:
                    text_info = saved_state['text_sampling_time']
                    text_widget_sampling_time.delete("1.0", tk.END)
                    text_widget_sampling_time.insert("1.0", text_info['content'])
                    text_widget_sampling_time.mark_set(tk.INSERT, text_info['cursor'])
                    if text_info['selection']:
                        text_widget_number_of_cycles.tag_add(tk.SEL, *text_info['selection'])

                if 'text_charging_length' in saved_state:
                    text_info = saved_state['text_charging_length']
                    text_widget_charging_length.delete("1.0", tk.END)
                    text_widget_charging_length.insert("1.0", text_info['content'])
                    text_widget_charging_length.mark_set(tk.INSERT, text_info['cursor'])
                    if text_info['selection']:
                        text_widget_number_of_cycles.tag_add(tk.SEL, *text_info['selection'])

                if 'text_discharging_length' in saved_state:
                    text_info = saved_state['text_discharging_length']
                    text_widget_discharging_length.delete("1.0", tk.END)
                    text_widget_discharging_length.insert("1.0", text_info['content'])
                    text_widget_discharging_length.mark_set(tk.INSERT, text_info['cursor'])
                    if text_info['selection']:
                        text_widget_number_of_cycles.tag_add(tk.SEL, *text_info['selection'])

                if 'port_combobox' in saved_state:
                    port_combobox_var.set(saved_state['port_combobox'])
                if 'port_combobox_baud' in saved_state:
                    port_combobox_baud_var.set(saved_state['port_combobox_baud'])

                global global_5_min_checkbox_state
                if 'check_button_5_min_delay' in saved_state:
                    global_5_min_checkbox_state = saved_state['check_button_5_min_delay']

        except FileNotFoundError:
            print("nothing in RESTORE METHOD")
            pass

    ##################
    # port combobox
    ##################
    update_flag = True
    def start_update_serial_ports():
        if update_flag:
            ports = [port.device for port in list_ports.comports()]
            port_combobox['values'] = ports
            root.after(1000, start_update_serial_ports)  # Update every 1 second
    def stop_update_serial_ports():
        global update_flag
        update_flag = False
    # Create a label for selecting a serial port
    label_serial_port = tk.Label(dialog, text="Select a serial port:", font=custom_font)
    label_serial_port.grid(row=1, column=0)

    # Create a dropdown menu for selecting serial ports
    port_combobox_var = tk.StringVar()
    port_combobox = ttk.Combobox(dialog, textvariable=port_combobox_var, state="readonly", font=custom_font)
    port_combobox.grid(row=2, column=0, sticky="news")

    #update drop box with available serial ports
    start_update_serial_ports()

    ##################
    #directory path
    ##################
    def change_csv_destination():
        global folder_path

        tk.Tk().withdraw()  # prevents an empty tkinter window from appearing
        folder_path_NEW = filedialog.askdirectory()
        if folder_path_NEW != "":
            text_widget_path_for_csv.configure(state='normal')
            text_widget_path_for_csv.delete('1.0', tk.END)
            text_widget_path_for_csv.insert(tk.END, folder_path_NEW)  # Insert received data path into Text widget
            text_widget_path_for_csv.configure(state='disable')
            folder_path = folder_path_NEW
        print(folder_path)
    # Create a Text widget to display received path for .csv data
    text_widget_path_for_csv = tk.Text(dialog, height=3, width=2)
    text_widget_path_for_csv.grid(row=0, column=0, sticky="news")
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    text_widget_path_for_csv.insert(tk.END, desktop)
    print(os.path.dirname(sys.argv[0]))
    text_widget_path_for_csv.configure(state='disable')

    button_path_for_csv = tk.Button(dialog, text="Change .csv destination", command=change_csv_destination)
    button_path_for_csv.grid(row=0, column=1,sticky="news")

    # Create a label f
    #
    #
    # or selecting a baud rate
    label_port_baud = tk.Label(dialog, text="Select a baud rate:", font=custom_font)
    label_port_baud.grid(row=1, column=1)
    # Create a dropdown menu for selecting baud rates
    port_combobox_baud_var = tk.StringVar()
    port_combobox_baud = ttk.Combobox(dialog, textvariable=port_combobox_baud_var, state="readonly", font=custom_font)
    port_combobox_baud.grid(row=2, column=1, sticky="news")
    port_combobox_baud['values'] = [300, 600, 750, 1200, 2400, 4800, 9600, 19200, 31250, 38400, 57600, 74880, 115200,
                                    230400, 250000, 460800, 500000, 921600, 1000000, 2000000]
    port_combobox_baud.current(14) #default 250000
    #######################################################
    # Create a Text widgets to store numerical parameters
    label_number_of_cycles = tk.Label(dialog, text="Number of Cycles [qty]:", font=custom_font)
    label_number_of_cycles.grid(row=3, column=0)
    text_widget_number_of_cycles = tk.Text(dialog, height=1, width=2, font=custom_font, bg="red")
    text_widget_number_of_cycles.grid(row=4, column=0, sticky="news")
    # Bind the validation function to the <KeyRelease> event
    text_widget_number_of_cycles.bind("<KeyRelease>", validate_text_text_widget_number_of_cycles)
    # Initial validation when the application starts
    validate_text_text_widget_number_of_cycles()
    # Example of programmatically inserting and validating
    insert_and_validate_text_text_widget_number_of_cycles("1")  # Call this function to insert a value and validate
    #
    label_sampling_time = tk.Label(dialog, text="Sampling Time [second]:", font=custom_font)
    label_sampling_time.grid(row=5, column=0)
    text_widget_sampling_time = tk.Text(dialog, height=1, width=2, font=custom_font, bg="red")
    text_widget_sampling_time.grid(row=6, column=0, sticky="news")
    # Bind the validation function to the <KeyRelease> event
    text_widget_sampling_time.bind("<KeyRelease>", validate_text_text_widget_sampling_time)
    # Initial validation when the application starts
    validate_text_text_widget_sampling_time()
    # Example of programmatically inserting and validating
    insert_and_validate_text_widget_sampling_time("1")  # Call this function to insert a value and validate

    #
    label_length_charging_cycles = tk.Label(dialog, text="Length Charging Cycles [second]:", font=custom_font)
    label_length_charging_cycles.grid(row=3, column=1)
    text_widget_charging_length = tk.Text(dialog, height=1, width=2, font=custom_font, bg="red")
    text_widget_charging_length.grid(row=4, column=1, sticky="news")
    # Bind the validation function to the <KeyRelease> event
    text_widget_charging_length.bind("<KeyRelease>", validate_text_widget_charging_length)

    # Initial validation when the application starts
    validate_text_widget_charging_length()

    # Example of programmatically inserting and validating
    insert_and_validate_text_widget_charging_length("1")  # Call this function to insert a value and validate

    #
    label_length_discharging_cycles = tk.Label(dialog, text="Length Discharging Cycles [second]:", font=custom_font)
    label_length_discharging_cycles.grid(row=5, column=1)
    text_widget_discharging_length = tk.Text(dialog, height=1, width=2, font=custom_font, bg="red")
    text_widget_discharging_length.grid(row=6, column=1, sticky="news")
    # Bind the validation function to the <KeyRelease> event
    text_widget_discharging_length.bind("<KeyRelease>", validate_text_widget_discharging_length)
    # Initial validation when the application starts
    validate_text_widget_discharging_length()
    # Example of programmatically inserting and validating
    insert_and_validate_text_widget_discharging_length("1")  # Call this function to insert a value and validate

    ################
    # Check box for 5 minutes cool down betwean charge discharge
    ################
    #TO_DO
    #create global variable that will hold truue or false for this state
    #add that global variable at the each inner functio where it has to go
    #create savings of the state in the JSON and UPDATE/Restore

    #Checking does check box operate properly
    def on_checkbox_toggle_5_min():
        if checkbox_var_m_min.get():
            print("Checkbox on_checkbox_toggle_5_min is checked")
        else:
            print("Checkbox on_checkbox_toggle_5_min is unchecked")

    # Create a variable to hold the checkbox state
    #global_5_min_checkbox_state
    #checkbox_var_m_min = tk.BooleanVar(value=True)
    global global_5_min_checkbox_state
    checkbox_var_m_min = tk.BooleanVar(value=global_5_min_checkbox_state)
    checkbox = tk.Checkbutton(dialog, text="5 [min] delay between charge/discharge to alowe battery chemistry to balance",
                              variable=checkbox_var_m_min, command=on_checkbox_toggle_5_min)
    checkbox.grid(row=9, column=0, columnspan=1, sticky="w")
    ################


    button_Apply = tk.Button(dialog, text="Apply", command=save_state, font=custom_font)
    button_Apply.grid(row=10, column=0, padx=10, pady=10)

    restore_state()

    # Configure columns and rows to expand when the dialog window is resized
    dialog.columnconfigure(1, weight=1)
    dialog.rowconfigure(1, weight=1)

    def on_close_dialog():
        stop_update_serial_ports()
        dialog.destroy()
    button_close = tk.Button(dialog, text="Close", command=on_close_dialog, font=custom_font)
    button_close.grid(row=10, column=1, padx=10, pady=10)

#Main interface Start, Pause, Stop
root = tk.Tk()
#root.geometry("1200x500") #modify this if you are using program on different size screans
#root.geometry("1500x500") #modify this if you are using program on different size screans Mac
root.geometry("1700x700") #modify this if you are using program on different size screans Windows

root.title("Battery testing interface")
root.resizable(width=False, height=False)#disabeling user to resize the window
#root.configure(background='green')
custom_font = ('Helvetica', 18)  # Adjust the size (12 here) as needed

def stop_update_serial_ports():
    global update_flag
    update_flag = False
def center_window(window, width=300, height=200):
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position x, y
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f'{width}x{height}+{x}+{y}')
def killGUI():
    custom_font = ('Helvetica', 18)  # Adjust the size (12 here) as needed
    dialogEXIT = tk.Toplevel(root)

    dialogEXIT.title("Exit")


    # Set the size and center the dialog
    center_window(dialogEXIT, 371, 180)

    dialogEXIT.resizable(width=False, height=False)  # disabeling user to resize the window
    dialogEXIT.transient(root)  # Set to be on top of the main window


    def instructionsEXIT():
        root.destroy()
        on_stop()
        stop_update_serial_ports()
        exit()

    # Create a label for selecting a baud rate
    dialogEXIT_label = tk.Label(dialogEXIT, text="Do you really want to exit?", font=("Arial", 16))
    dialogEXIT_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    # dialogEXIT_label = tk.Label(dialogEXIT, text="Do you really want to exit?", font=custom_font)

    dialogEXIT_button = tk.Button(dialogEXIT, text="Exit", command=instructionsEXIT)
    dialogEXIT_button.grid(row=1, column=0, padx=10, pady=10, ipadx=20, ipady=10)

    dialogRESUME_button = tk.Button(dialogEXIT, text="Resume", command=dialogEXIT.destroy)
    dialogRESUME_button.grid(row=1, column=1, padx=10, pady=10, ipadx=20, ipady=10)

    dialogEXIT_button.config(width=10, height=2)
    dialogRESUME_button.config(width=10, height=2)

root.protocol('WM_DELETE_WINDOW', killGUI)  # root is your root window
open_dialog_button = tk.Button(root, text="Admin", command=open_admin_dialog, font=custom_font, fg="black")
open_dialog_button.grid(row=0, column=0, padx=10, pady=10, sticky='ewsn')

def handle_data(data, filename):
    global global_text_widget_path_for_csv
    try:
        # Construct the absolute file path/DESKTOP, where will .csv be saved
        # payload_csv_terminal = payload_csv_terminal.replace('\n', '')
        path = global_text_widget_path_for_csv  # Getting stored absolute addres from text widget
        path = path.replace('\n', '')
        file_path = os.path.join(path, filename)
        with open(file_path, 'a') as file:
            file.write(data + '\n')
    except IOError:
        print("Error: could not append to file " + filename)
        print("Error: could not append to file  FULL file_path" + file_path)
# Create a start button
def on_start():
    print("start")
    stop_button.configure(state='normal')
    start_button.configure(state='disable')
    pause_button.configure(state='normal')
    open_dialog_button.configure(state='disable')

    def on_connect():
        global ser
        selected_port = global_port_combobox_string
        selected_port_baud = global_port_combobox_baud_string
        print(selected_port)
        print(selected_port_baud)
        if selected_port:
            try:
                global filename_sample_time
                global filename_capacity
                global filename_sample_time_per_10_x_smaller
                ser = serial.Serial(selected_port, baudrate=selected_port_baud)  # Example baudrate
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename_sample_time = f'Data_{timestamp}_received_data.csv'
                filename_sample_time_per_10_x_smaller = f'Data_{timestamp}_received_data_per_10_x_smaller.csv'
                filename_capacity = f'Data_{timestamp}_capacity.csv'
                threading.Thread(target=read_serial, args=(ser, filename_sample_time), daemon=True).start()  # Start a new thread for reading serial data
                print(f"Connected to {selected_port}")
            except serial.SerialException:
                print(f"Failed to connect to {selected_port}")
        else:
            print("No port selected")

    def read_serial(ser, filename):
        global serial_data
        while True:
            if ser.in_waiting:
                serial_data = ser.readline().decode().strip()
                if checkbox_var.get():
                    text_terminal_print.see("end")

    on_connect()

    def relay_a_on():
        data_to_send_raon = 'raon' + '\n'
        ser.write(data_to_send_raon.encode())

    def relay_a_off():
        data_to_send_raoff = 'raoff' + '\n'
        ser.write(data_to_send_raoff.encode())

    def relay_b_on():
        data_to_send_rbon = 'rbon' + '\n'
        ser.write(data_to_send_rbon.encode())

    def relay_b_off():
        data_to_send_rboff = 'rboff' + '\n'
        ser.write(data_to_send_rboff.encode())

    def reqequest_sensors_data():
        data_to_send_m = 'm' + '\n'
        ser.write(data_to_send_m.encode())

    time.sleep(1)  # hard 1 second from the moment of connecting for data to settle
    global ser
    print("send data")

    def pause_function():
        global pause_bool
        if pause_bool:
            relay_a_off()
            while pause_bool:
                time.sleep(1)
                #print("Pause activated")
                pass
            relay_a_on()


    def average(sample_time, current_minut):
        ##RELATED TO THE CUSTOM SETTINGS
        pause_function()
        reqequest_sensors_data()  # fill the buffer
        time.sleep(sample_time) #sleap while buffer is being filled
        #data = str(serial_data)

        #TODO
        #copy stuff from bottom
        ##RELATED TO THE CUSTOM SETTINGS

        # extract amp,
        # miltipliy it with sample time,
        # ++ it to the previous,
        # calculate mAh

        ######################### extract amp #########################
        # Parsinf of the data from arduino, extracting only "A" values for capacity purpose
        # v,a,w,v,a,w,v,a,w,v,a,w,v,a,w,v,a,w,v,a,w,v,a,w,
        input_string = serial_data
        # Remove the trailing comma
        input_string = input_string.strip(',')
        # Split the string by commas
        items = input_string.split(',')  # items = array with all parsed data
        only_currents = [items[1], items[4], items[7], items[10], items[13], items[16], items[19],
                         items[22]]  # only_currents = array with only currents data
        print(only_currents)
        ######################### miltipliy it with sample time #########################
        counter = 0
        global global_array_capacity_currents_1
        while counter < len(only_currents):
            global_array_capacity_currents_1[counter] = global_array_capacity_currents_1[counter] + (
                        ((float(only_currents[counter]) * float(global_sampling_time_string)) * 1000) / 3600)
            counter = counter + 1
        print("TEST ", global_array_capacity_currents_1)
        #make an array or list from serial_data

        serial_data_array = serial_data.split(',')
        #Inserting?\/grouping capacity mesured till now with V,A,W
        serial_data_array.insert(24, round(global_array_capacity_currents_1[7], 3)) #round(global_array_capacity_currents_1[7], 5)
        serial_data_array.insert(21, round(global_array_capacity_currents_1[6], 3))#round(global_array_capacity_currents_1[6], 3)
        serial_data_array.insert(18, round(global_array_capacity_currents_1[5], 3))
        serial_data_array.insert(15, round(global_array_capacity_currents_1[4], 3))
        serial_data_array.insert(12, round(global_array_capacity_currents_1[3], 3))
        serial_data_array.insert(9, round(global_array_capacity_currents_1[2], 3))
        serial_data_array.insert(6, round(global_array_capacity_currents_1[1], 3))
        serial_data_array.insert(3, round(global_array_capacity_currents_1[0], 3))

        print("TEST ", serial_data_array)
        serial_data_array = ','.join(map(str, serial_data_array))
        print("TEST ", serial_data_array)


        #Insert progres capacity right next to each column of newly cretad list


        #modify terminal entry (8 columns)
        write_on_terminal_widget(serial_data + "\n")

        payload_data = datetime.now().strftime("%Y-%m-%d,%H:%M:%S,")+ str(round(current_minut,3)) + ',' + serial_data_array
        handle_data(payload_data, filename_sample_time)  # [1:-1] trims last and first character from array to string, which mens no brackets anymore






    def delayed_function():
        global pause_bool, global_cycles_string, global_sampling_time_string, global_charging_length_string,global_discharging_length_string
        global global_port_combobox_string,global_port_combobox_baud_string, serial_data
        global global_5_min_checkbox_state

        time.sleep(0.5)
        relay_a_off()
        time.sleep(0.5)
        relay_b_off()
        time.sleep(0.5)

        #HEADER OF THE FILES
        payload_title ="Cycle count [qty]: " + str(global_cycles_string) + "\n" + "Sampling time [second]: " + str(global_sampling_time_string) + "\n" + "Charging length [second]: " + str(global_charging_length_string) + "\n" + "Discharging length [second]: " + str(global_discharging_length_string) + "\n"

        print("Delayed function started")
        #write_on_terminal_widget(payload_title + "\n")
        write_on_terminal_widget(payload_title)
        handle_data(payload_title, filename_sample_time)
        #add TEST payload and handle it
        handle_data("TEST", filename_capacity)
        counter_str_concan_capacyty_title = 0
        payload_concan_capacyty_title = ""
        while counter_str_concan_capacyty_title < 8:
            payload_concan_capacyty_title = payload_concan_capacyty_title + "Capacity retention rate"
            payload_concan_capacyty_title = payload_concan_capacyty_title + ","
            payload_concan_capacyty_title = payload_concan_capacyty_title + "Cycle"
            payload_concan_capacyty_title = payload_concan_capacyty_title + ","
            payload_concan_capacyty_title = payload_concan_capacyty_title + "Charging Capacity"
            payload_concan_capacyty_title = payload_concan_capacyty_title + ","
            payload_concan_capacyty_title = payload_concan_capacyty_title + "Discharging Capacity"
            payload_concan_capacyty_title = payload_concan_capacyty_title + ","
            payload_concan_capacyty_title = payload_concan_capacyty_title + "Value"
            payload_concan_capacyty_title = payload_concan_capacyty_title + ",,"
            counter_str_concan_capacyty_title = counter_str_concan_capacyty_title + 1
        handle_data(payload_concan_capacyty_title, filename_capacity)

        #payload that marks batteries numbners under this payload
        payload_battery_number = "Battery #1,,,,,,Battery #2,,,,,,Battery #3,,,,,,Battery #4,,,,,,Battery #5,,,,,,Battery #6,,,,,,Battery #7,,,,,,Battery #8"
        handle_data(payload_battery_number, filename_capacity)

        #PASTE HERE
        count_cycle = 0
        while count_cycle < int(global_cycles_string):

            print("charging is first")
            time.sleep(0.5)
            relay_a_on()
            time.sleep(0.5)
            count_1 = 0
            payload_csv_terminal = "\n\nCurrent cycle: "+ str(count_cycle +1) + "\nCharging initiated"

            write_on_terminal_widget(payload_csv_terminal + "\n[V]1,[A]1,[W]1,[mAh]1,[V]2,[A]2,[W]2,[mAh]2,[V]3,[A]3,[W]3,[mAh]3,[V]4,[A]4,[W]4,[mAh]4,[V]5,[A]5,[W]5,[mAh]5,[V]6,[A]6,[W]6,[mAh]6,[V]7,[A]7,[W]7,[mAh]7,[V]8,[A]8,[W]8,[mAh]8\n")

            handle_data(payload_csv_terminal, filename_sample_time)
            handle_data("date,time,active minutes,[V]1,[A]1,[W]1,[mAh]1,[V]2,[A]2,[W]2,[mAh]2,[V]3,[A]3,[W]3,[mAh]3,[V]4,[A]4,[W]4,[mAh]4,[V]5,[A]5,[W]5,[mAh]5,[V]6,[A]6,[W]6,[mAh]6,[V]7,[A]7,[W]7,[mAh]7,[V]8,[A]8,[W]8,[mAh]8", filename_sample_time)

            counter_inner = 0
            while count_1 < int(global_charging_length_string):
                count_1 += 1
                counter_inner += 1
                if counter_inner >= int(global_sampling_time_string):
                    #average(int(global_sampling_time_string), ((count_1+int(global_sampling_time_string))-1)/60) #mostlikly delete "-1"
                    average(int(global_sampling_time_string), (count_1 / 60))  # mostlikly delete "-1"
                    counter_inner = 0

            print("Charging finished")

            # DELAY HERE if this wasnt last cycle, delay is allowed. All in favour of stabilizing chemistry
            if (count_cycle < int(global_cycles_string)) and (global_5_min_checkbox_state == True):
                relay_a_off()
                relay_b_off()
                write_on_terminal_widget("\n5 [min], Battery chemistry balance delay")
                text_terminal_print.see("end")
                handle_data("\n\n5 [min] Battery chemistry balance delay", filename_sample_time)
                ######
                #ADD DIALOG HERE THAT TELLS US THAT chemistry is balancing and optionaly add timer reduction
                #and after timer is done kill the dialog


                notification_dialog_countown_info()


            #ADD here add to new file or append mesured capacity
            global global_array_capacity_currents_1
            global global_array_capacity_currents_2
            #save in to the new array 0,2,4,6,8,10,12,14
            global_array_capacity_currents_2 = global_array_capacity_currents_1
            global_array_capacity_currents_1 = [0, 0, 0, 0, 0, 0, 0, 0]

            count_2 = 0
            payload_csv_terminal = "\n\nCurrent cycle: " + str(count_cycle + 1) + "\n Discharging initiated"

            write_on_terminal_widget(payload_csv_terminal + "\n[V]1,[A]1,[W]1,[mAh]1,[V]2,[A]2,[W]2,[mAh]2,[V]3,[A]3,[W]3,[mAh]3,[V]4,[A]4,[W]4,[mAh]4,[V]5,[A]5,[W]5,[mAh]5,[V]6,[A]6,[W]6,[mAh]6,[V]7,[A]7,[W]7,[mAh]7,[V]8,[A]8,[W]8,[mAh]8\n")


            relay_a_on()
            relay_b_on()
            handle_data(payload_csv_terminal, filename_sample_time)
            handle_data("date,time,active minutes,[V]1,[A]1,[W]1,[mAh]1,[V]2,[A]2,[W]2,[mAh]2,[V]3,[A]3,[W]3,[mAh]3,[V]4,[A]4,[W]4,[mAh]4,[V]5,[A]5,[W]5,[mAh]5,[V]6,[A]6,[W]6,[mAh]6,[V]7,[A]7,[W]7,[mAh]7,[V]8,[A]8,[W]8,[mAh]8", filename_sample_time)

            '''
            changes:
            payload that goes on the top and says TEST
            payload for batteryes numbers
            Cast current minute to print int minutes
            '''

            counter_inner = 0
            while count_2 < int(global_discharging_length_string):
                count_2 += 1
                counter_inner += 1
                if counter_inner >= int(global_sampling_time_string):
                    average(int(global_sampling_time_string), (count_2 / 60)) #try to replace this line with first bottom line and test
                    #average(int(global_sampling_time_string), ((count_2+int(global_sampling_time_string))-1)/60)
                    counter_inner = 0
            print("Discharging finished")

            #make array that contains
            #capacity retention rate, Cycle, global_array_capacity_currents_2[i],global_array_capacity_currents_1[i],value
            rounded_array_2 = ["{:.5f}".format(num) for num in global_array_capacity_currents_2]
            rounded_array_1 = ["{:.5f}".format(num) for num in global_array_capacity_currents_1]

            counter_rounded = 0
            string_payload = ""

            global global_discharge_first_capacity
            if count_cycle == 0:
                global_discharge_first_capacity = rounded_array_1
                #print("THIS",global_discharge_first_capacity)

            while counter_rounded < 8:
                if float(global_discharge_first_capacity[counter_rounded]) != 0:
                    string_payload = string_payload + str("{:.5f}".format(((float(rounded_array_1[counter_rounded]))/(float(global_discharge_first_capacity[counter_rounded])))*100))
                else:
                    string_payload = string_payload + "nan"

                print("THIS_discharge_new",float(rounded_array_1[counter_rounded]))
                print("THIS_discharge_first", float(rounded_array_1[counter_rounded]))
                string_payload = string_payload + ","
                string_payload = string_payload + str(count_cycle+1)
                string_payload = string_payload + ","
                string_payload = string_payload + rounded_array_2[counter_rounded]
                string_payload = string_payload + ","
                string_payload = string_payload + rounded_array_1[counter_rounded]
                string_payload = string_payload + ","
                ###
                if float(rounded_array_1[counter_rounded]) != 0:
                    string_payload = string_payload + str("{:.5f}".format(float(rounded_array_2[counter_rounded])/float(rounded_array_1[counter_rounded])))
                else:
                    string_payload = string_payload + "nan"
                ###
                string_payload = string_payload + ",,"
                counter_rounded = counter_rounded + 1

            handle_data(string_payload, filename_capacity)
            print(string_payload)


            global_array_capacity_currents_1 = [0, 0, 0, 0, 0, 0, 0, 0]
            global_array_capacity_currents_2 = [0, 0, 0, 0, 0, 0, 0, 0]
            #!!!!!!!!!!!!!!!!!!!!

            relay_a_off()
            relay_b_off()

            count_cycle += 1

            #Duplicate .csv data in to new .xlxs file and then update capacity graph on the new file after every cycle
            thread = threading.Thread(target=Converting_csv_to_xlxs.convert_csv_to_xlxs(filename_capacity, global_text_widget_path_for_csv))
            thread.start()
            #Converting_csv_to_xlxs.convert_csv_to_xlxs(filename_capacity, global_text_widget_path_for_csv)

            #DELAY HERE if this wasnt last cycle, delay is alowed. All in favour of stabilizing chemistry
            if (count_cycle < int(global_cycles_string)) and (global_5_min_checkbox_state == True):
                write_on_terminal_widget("\n5 [min], Battery chemistry balance delay")
                text_terminal_print.see("end")
                handle_data("\n\n5 [min] Battery chemistry balance delay", filename_sample_time)
                notification_dialog_countown_info()
                #time.sleep(300)  # stabilizing chemistry

        relay_a_off()
        relay_b_off()
        on_stop()


    # Create a thread for the delayed function
    delayed_thread = threading.Thread(target=delayed_function)
    # Start the thread
    delayed_thread.start()
start_button = tk.Button(root, text="Start", command=on_start, font=custom_font, fg="green")
start_button.grid(row=1, column=1, ipadx = 60, ipady = 40, sticky = "news")

# Create a pause button
def on_pause():
    global pause_bool
    print("pause")
    if pause_bool:
        pause_bool = False
        write_on_terminal_widget("CONTINUE\n")
        handle_data("CONTINUE", filename_sample_time)

        ##########
        payload_title = "\n" + "Cycle count [qty]: " + str(
        global_cycles_string) + "\n" + "Sampling time [second]: " + str(
        global_sampling_time_string) + "\n" + "Charging length [second]: " + str(
        global_charging_length_string) + "\n" + "Discharging length [second]: " + str(
        global_discharging_length_string) + "\n\n"

        print("Delayed function started")
        text_terminal_print.configure(state='normal')
        text_terminal_print.insert(tk.END, payload_title)
        text_terminal_print.configure(state='disable')
        handle_data(payload_title, filename_sample_time)
        open_dialog_button.configure(state='normal')

        open_dialog_button.configure(state='disable')

        ##########

    else:
        pause_bool = True
        write_on_terminal_widget("PAUSE\n")
        handle_data("PAUSE", filename_sample_time)
        open_dialog_button.configure(state='normal')
    print("pause_bool",pause_bool)
pause_button = tk.Button(root, text="Pause/Continue", command=on_pause, font=custom_font, fg="black")
pause_button.grid(row=2, column=1, ipadx = 60, ipady = 40, sticky = "news")
pause_button.configure(state='disable')

on_stop_is_clicked = False
def notification_dialog_countown_info():

    ########
    global on_stop_is_clicked
    on_stop_is_clicked = False
    pause_button.configure(state='disable')
    flag_was_stop_pressed = False
    ########

    text_terminal_print.configure(state='normal')
    write_on_terminal_widget("\n\n")
    text_terminal_print.configure(state='disable')
    text_terminal_print.see("end")
    count_down = 300
    while count_down > 0:
        try:
            text_terminal_print.configure(state='normal')
            text_terminal_print.delete("end-1l", "end")
            write_on_terminal_widget("\n"+str(count_down) + "[second] left till cool down finishes.")
            text_terminal_print.configure(state='disable')
            text_terminal_print.see("end")
        except:
            print("An exception occurred, dialog was closed by user and can't update counter")
        count_down = count_down - 1
        time.sleep(1)

        if on_stop_is_clicked:
            flag_was_stop_pressed = True
            on_stop_is_clicked = False
            count_down = 0

    if count_down == 0 and flag_was_stop_pressed == False:
        text_terminal_print.configure(state='normal')
        text_terminal_print.delete("end-1l", "end")
        write_on_terminal_widget("\n" + "Cool down is over process continues.")
        text_terminal_print.configure(state='disable')
        text_terminal_print.see("end")


    if flag_was_stop_pressed == False:
        pause_button.configure(state='normal')
def on_stop_call_from_real_button():
    dialogSTOP = tk.Toplevel(root)

    dialogSTOP.title("Stop")


    # Set the size and center the dialog
    center_window(dialogSTOP, 371, 180)

    dialogSTOP.resizable(width=False, height=False)  # disabeling user to resize the window
    dialogSTOP.transient(root)  # Set to be on top of the main window


    def instructionsEXIT():
        on_stop()
        dialogSTOP.destroy()

    # Create a label for selecting a baud rate
    dialogSTOP_label = tk.Label(dialogSTOP, text="Do you really want to STOP?", font=("Arial", 16))
    dialogSTOP_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    # dialogEXIT_label = tk.Label(dialogEXIT, text="Do you really want to exit?", font=custom_font)

    dialogSTOP_button = tk.Button(dialogSTOP, text="STOP", command=instructionsEXIT)
    dialogSTOP_button.grid(row=1, column=0, padx=10, pady=10, ipadx=20, ipady=10)

    dialogRESUME_button = tk.Button(dialogSTOP, text="Resume", command=dialogSTOP.destroy)
    dialogRESUME_button.grid(row=1, column=1, padx=10, pady=10, ipadx=20, ipady=10)

    dialogSTOP_button.config(width=10, height=2)
    dialogRESUME_button.config(width=10, height=2)
# Create a stop button
def on_stop():
    global on_stop_is_clicked
    on_stop_is_clicked = True
    try:
        print("stop")
        global pause_bool
        pause_bool = False
        global ser
        data_to_send_raoff = 'raoff' + '\n'
        ser.write(data_to_send_raoff.encode())
        data_to_send_rboff = 'rboff' + '\n'
        ser.write(data_to_send_rboff.encode())

        stop_button.configure(state='disable')
        pause_button.configure(state='disable')
        start_button.configure(state='normal')
        open_dialog_button.configure(state='normal')

        #add 3 lines under to zero acumulated capacites capacity
        global global_array_capacity_currents_1, global_array_capacity_currents_2
        global_array_capacity_currents_1 = [0, 0, 0, 0, 0, 0, 0, 0]
        global_array_capacity_currents_2 = [0, 0, 0, 0, 0, 0, 0, 0]

        if ser:
            ser.close()
            print("Disconnected from serial port")

            write_on_terminal_widget("\n\nEnd\n")
            handle_data("\n\nEnd", filename_sample_time)
            text_terminal_print.see("end")
        else:
            print("Serial port is not connected")
    except:
        pass

stop_button = tk.Button(root, text="Stop", command=on_stop_call_from_real_button, font=custom_font, fg="red")
stop_button.grid(row=3, column=1, ipadx = 60, ipady = 40, sticky = "news")
stop_button.configure(state='disable')

# Create check_box for autoscroll
#autoscroll checkbox
def on_checkbox_toggle_autoscroll():
    if checkbox_var.get():
        print("Checkbox on_checkbox_toggle is checked")
        text_terminal_print.see("end")
    else:
        print("Checkbox on_checkbox_toggle is unchecked")
# Create a variable to hold the checkbox state
checkbox_var = tk.BooleanVar(value=True)
checkbox = tk.Checkbutton(root, text="Autoscroll", variable=checkbox_var, command=on_checkbox_toggle_autoscroll)
checkbox.grid(row=9, column=0 ,columnspan=1,sticky = "w")

# Create a Text widget to display received data
custom_font_For_terminal = ('Helvetica', 10)  # Adjust the size (12 here) as needed
#text_terminal_print = tk.Text(root, height=30, width=103)
text_terminal_print = tk.Text(root, height=35, width=170, font=custom_font_For_terminal)
text_terminal_print.grid(row=1, column=3, rowspan=3, sticky ="news")
text_terminal_print.configure(state='disable')

# Create a Button that erase from Text widget all data
def clearToTextInput():
    text_terminal_print.configure(state='normal')
    text_terminal_print.delete("1.0", "end")
    text_terminal_print.configure(state='disable')
erase_button = tk.Button(root, text="Clear", command=clearToTextInput)
erase_button.grid(row=9, column=4,columnspan=1,sticky = "e")

state = {}      # Initialize state for json saving restoring data
############################################
# restore parameters
def restore_state_to_global_vars():
    global global_cycles_string, global_sampling_time_string, global_charging_length_string, global_discharging_length_string, global_port_combobox_string, global_port_combobox_baud_string, global_text_widget_path_for_csv
    try:#settings_battery_test
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        file_path = os.path.join(desktop, name_JSON_Settings+'.json')
        with open(file_path, 'r') as file:
            saved_state = json.load(file)
            if 'text' in saved_state:
                global_text_widget_path_for_csv = saved_state['text']  # getting from the top layer
                global_text_widget_path_for_csv = global_text_widget_path_for_csv['content']  # getting from the sublayer in json ou=r numerical value and turn it in to int
                print("global_text_widget_path_for_csv",global_text_widget_path_for_csv)
            if 'text_cycles' in saved_state:
                global_cycles_string = saved_state['text_cycles']    #getting from the top layer
                global_cycles_string = int(global_cycles_string['content']) #getting from the sublayer in json ou=r numerical value and turn it in to int
            if 'text_sampling_time' in saved_state:
                global_sampling_time_string = saved_state['text_sampling_time']  # getting from the top layer
                global_sampling_time_string = int(global_sampling_time_string['content'])  # getting from the sublayer in json ou=r numerical value and turn it in to int
            if 'text_charging_length' in saved_state:
                global_charging_length_string = saved_state['text_charging_length']  # getting from the top layer
                global_charging_length_string = int(global_charging_length_string['content'])  # getting from the sublayer in json ou=r numerical value and turn it in to int
            if 'text_discharging_length' in saved_state:
                global_discharging_length_string = saved_state['text_discharging_length']  # getting from the top layer
                global_discharging_length_string = int(global_discharging_length_string['content'])  # getting from the sublayer in json ou=r numerical value and turn it in to int
            if 'port_combobox' in saved_state:
                global_port_combobox_string = (saved_state['port_combobox'])
            if 'port_combobox_baud' in saved_state:
                global_port_combobox_baud_string = (saved_state['port_combobox_baud'])

            global global_5_min_checkbox_state
            if 'check_button_5_min_delay' in saved_state:
                global_5_min_checkbox_state = saved_state['check_button_5_min_delay']

    except FileNotFoundError:
        print("json not found")
        pass

restore_state_to_global_vars()  # Restore state on application start
root.mainloop()