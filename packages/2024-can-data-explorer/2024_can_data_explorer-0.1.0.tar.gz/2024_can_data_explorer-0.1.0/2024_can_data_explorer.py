#!/usr/bin/env python3
"""Library and GUI for viewing CAN bus data from HSM research machines.

Copyright iFOS GmbH

Authors: Jakub Wołosz, Lukas Schreiber

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
UT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.1.0"

# Imports

# standard libraries
from pathlib import Path
import glob
import json
import os
import sys
import subprocess
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser


# third party libraries
import pandas as pd
import cantools
import cantools.subparsers.decode
import cantools.logreader

### Constants

TZ = "Europe/Berlin"


###  Defined Functions


def Boundaries(datetime_start: str, time_to_add: str, tz: str = TZ) -> pd.Interval:
    """
    Creates a time period as a pandas Interval from the given datetime and the incremented time.

    Args:
        datetime_start (str): The start datetime string in 'YYYY-MM-DDTHHMMSS' format.
        time_to_add (str): The time to add in 'X XX XX XX' format, representing days, hours, minutes, and seconds.

    Returns:
        pd.Interval: A pandas Interval object representing the time period.

    Raises:
        ValueError: If the input strings do not match the expected format.
    """

    # Check and convert the input datetime string to a pandas Timestamp object
    try:
        start_datetime = pd.to_datetime(
            datetime_start, format="%Y-%m-%dT%H%M%S"
        ).tz_localize(tz)
    except ValueError:
        raise ValueError("datetime_start must be in 'YYYY-MM-DDTHHMMSS' format.")

    # Parse the time_to_add string
    try:
        days, hours, minutes, seconds = map(int, time_to_add.split())
    except ValueError:
        raise ValueError(
            "time_to_add must be in 'X XX XX XX' format, representing days, hours, minutes, and seconds."
        )

    # Check if the parsed values are non-negative
    if any(x < 0 for x in [days, hours, minutes, seconds]):
        raise ValueError(
            "Days, hours, minutes, and seconds must be non-negative integers."
        )

    # Create a Timedelta object with the specified amount of time
    time_delta = pd.Timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    # Calculate the end datetime
    end_datetime = start_datetime + time_delta
    # Create a pandas Interval object representing the time period
    time_period = pd.Interval(left=start_datetime, right=end_datetime, closed="both")

    return time_period


def Localize(cwd: str, tz: str = TZ) -> pd.DataFrame:
    """
    The function localizes all .log files within a current working directory according to the machine type,
    splits the contained information e.g. date, time and signal duration (converted to decimal values), and stores it as pd.DataFrame.

    Args:
        cwd: str

    Returns:
        pd.Dataframe, which contains data extracted from log files.
    """

    # Find all .log files within cwd and store them in a list
    directory = Path(cwd)
    # filepath = glob.glob(str(directory / '*.log'))
    filepath = sorted(glob.glob("can_????-??-??T??????_#????.log", root_dir=directory))
    # Extract components from filenames
    formatted_files = [os.path.basename(f)[4:21] for f in filepath]
    # Create a dictionary from lists
    datadict = {"name": filepath, "datetime": formatted_files}
    # Create pandas DataFrame from dictionary
    df = pd.DataFrame.from_dict(data=datadict)

    # Format DataFrame columns
    df["name"] = pd.Series(df["name"], dtype="string")
    df["datetime"] = pd.to_datetime(
        df["datetime"], format="%Y-%m-%dT%H%M%S"
    ).dt.tz_localize(
        tz
    )  # Assuming 'date' is in 'YYYY-MM-DD' format

    # # Calculate duration in hours (as decimal numbers)
    df["duration"] = (
        (df["datetime"].shift(-1) - df["datetime"])
        .dt.total_seconds()
        .div(3600)
        .fillna(0)
        .astype(float)
    )

    # # Set duration value to 0 for each last row of a currnt date.

    # Extract the date from 'datetime'
    df["date"] = df["datetime"].dt.date
    # Identify the last occurrence of each date
    last_indices = df.groupby("date").tail(1).index
    # Set the 'duration' value to 0 for these identified rows
    df.loc[last_indices, "duration"] = 0
    # Drop the 'date' column as it is no longer needed
    df = df.drop(columns=["date"])

    # #Calculate total working time (sum of the duration of the signals)
    total_working_time = df["duration"].sum()
    print("Total working time is :", round(total_working_time, 2), "h")

    return df


def File_validation(date_range: pd.Interval, data: pd.DataFrame) -> pd.DataFrame:
    """
    The function filters .log files which meet the date criteria (desired date range)
    It returns a DataFrame containing rows meeting the criteria.
    The output has the same columns as the Localize() function.

    Parameters:
    date_range: pd.Interval - The interval to filter the 'datetime' column.
    data: pd.DataFrame - The DataFrame containing log data with 'datetime' and 'duration' columns.

    Returns:
    pd.DataFrame - A DataFrame which contains desired log files (filtered by the constraints from input_info() function).
    """

    # Filter the rows where the 'datetime' is within the specified 'date_range'
    approved_files_df = data[
        (data["datetime"] >= date_range.left)
        & (data["datetime"] <= date_range.right).shift(1, fill_value=True)
    ]

    if approved_files_df.empty:
        raise ValueError("The DataFrame is empty. Check the Input Parameters!")

    total_working_time = approved_files_df["duration"].sum()
    print(
        "Total working time for desired period is :", round(total_working_time, 2), "h"
    )

    return approved_files_df


def Fuel_consumption(
    database_path: str,
    files: pd.DataFrame,
    cwd: str,
    date_range: pd.Interval,
) -> str:
    """
    The function calculates the fuel consumption over log files which satisfy the desired date range.

    Parameters:
    - database_path: str, path to the DBC file.
    - files: pd.DataFrame, DataFrame containing file names and durations.
    - cwd: str, current working directory where log files are located.
    - date_range: pd.Interval to apply to the first and last file in files.

    Returns: information about total fuel burned over desired time.
    """
    # Load the DBC file
    database = cantools.database.load_file(database_path)

    # Initialize a list to hold results
    results = []

    # Iterate over each row in the files DataFrame
    length = len(files.index)
    for index, row in files.reset_index().iterrows():
        file_name = row["name"]
        duration = row["duration"]
        check_timestamp = index in {files.index[0], files.index[-1]}

        path = os.path.join(cwd, file_name)

        # Open and parse the log file
        with open(path) as log:
            fuel_rates = []
            EN_duration = []
            parser = cantools.logreader.Parser(log)

            for line, frame in parser.iterlines(keep_unknowns=True):
                if check_timestamp and frame.timestamp not in date_range:
                    continue
                if frame is not None and frame.frame_id == 385:
                    message = database.get_message_by_frame_id(frame.frame_id)
                    decoded_message = message.decode(frame.data)
                    fuel_rates.append(decoded_message["Fuelrate"])
                    EN_duration.append(decoded_message["RPM_Diesel"])

            # Calculate the average fuel rate for the current file
            if fuel_rates:
                avg_fuel_rate = sum(fuel_rates) / len(fuel_rates)
                total_fuel_rate = avg_fuel_rate * duration
                if EN_duration:
                    # print(EN_duration)
                    count_greater_than_zero = sum(1 for x in EN_duration if x > 0)
                    time_coefficient = count_greater_than_zero / len(EN_duration)
                    working_time = duration * time_coefficient
                    results.append(
                        {
                            "File": file_name,
                            "Total Fuelrate": total_fuel_rate,
                            "Working_time": working_time,
                        }
                    )
        Progress["value"] = (100 * index) // length
        root.update_idletasks()

    # Convert results to a DataFrame
    result_df = pd.DataFrame.from_dict(results)
    # result_df_fuel = result_df['Total Fuelrate'].sum()
    result_df = result_df.sum()
    # # Round the total fuel consumption to 3 decimal places
    total_fuel_consumption = round(result_df["Total Fuelrate"], 3)
    working_time = round(result_df["Working_time"], 3)
    consumption_and_time = {
        "consumption": total_fuel_consumption,
        "working_time": working_time,
    }
    return consumption_and_time


def Draw_a_chart(elements: list, dbc_path: str, patterns: list):

    patterns = [elem for pattern in patterns for elem in (pattern, "-")][:-1]

    style_path = os.path.join(script_folder, "ifos.mplstyle")
    args = (
        [sys.executable, "-m", "cantools", "plot", dbc_path]
        + patterns
        + ["--style", style_path]
    )
    cat = ["cmd", "/c", "type"] if sys.platform == "win32" else ["cat"]
    combined = subprocess.Popen(cat + elements, stdout=subprocess.PIPE)
    subprocess.Popen(args, stdin=combined.stdout)


# ======================GUI
# Functions
def _button_trigger_directory():
    cwd_dirname = filedialog.askdirectory(initialdir=cwd_entry_var.get())
    if cwd_dirname:  # Ensure a directory was selected
        cwd_entry_var.set(cwd_dirname)


def _button_trigger_file():
    dbc_path = DBC_entry_var.get()
    file_path = filedialog.askopenfilename(
        initialdir=os.path.dirname(dbc_path), initialfile=dbc_path
    )
    if file_path:  # Ensure a file was selected
        DBC_entry_var.set(file_path)


def _get_and_cache_paths():
    logs_path = cwd_entry_var.get()
    dbc_path = DBC_entry_var.get()
    with open(cache_file, "w") as file:
        json.dump(dict(logs_path=logs_path, dbc_path=dbc_path), file)
    return logs_path, dbc_path


def _get_interval(tz=TZ):
    start = pd.to_datetime(
        st_date_entry_var.get() + " " + st_time_entry_var.get(),
        format="%Y-%m-%d %H:%M:%S",
    ).tz_localize(tz)
    end = pd.to_datetime(
        end_date_entry_var.get() + " " + end_time_entry_var.get(),
        format="%Y-%m-%d %H:%M:%S",
    ).tz_localize(tz)
    return pd.Interval(start, end)


def _run_progress_bar():
    # Reset the progress bar to zero
    Progress["value"] = 0
    Progress.grid(column=0, row=1, columnspan=4, pady=5)

    # Simulating task execution
    info = _get_interval()

    global logs_path
    global dbc_path
    logs_path, dbc_path = _get_and_cache_paths()

    logs = Localize(logs_path)

    validate = File_validation(info, logs)

    FC = Fuel_consumption(dbc_path, validate, logs_path, date_range=info)

    Progress["value"] = 100
    root.update_idletasks()

    Output_label[
        "text"
    ] += f"{info.left:%Y-%m-%d %H:%M:%S} – {info.right:%Y-%m-%d %H:%M:%S} {FC['consumption']:>10,.3f} l {FC['working_time']:>10,.3f} h\n"


def open_help_pdf():
    webbrowser.open_new(
        os.path.join("file://", script_folder, "assets/can_description_hsm.pdf")
    )


def _chart_run():
    info = _get_interval()
    logs_path, dbc_path = _get_and_cache_paths()
    logs = Localize(logs_path)
    validate = File_validation(info, logs)
    elements = validate["name"].to_list()
    os.chdir(logs_path)
    selected_items = _get_selected_list()
    Draw_a_chart(elements=elements, dbc_path=dbc_path, patterns=selected_items)


def _on_entry_click(event):
    if event.widget.get() == placeholder_text:
        event.widget.delete(0, "end")
        event.widget.config(foreground="black", font=default_font)


def _on_focusout(event):
    if event.widget.get() == "":
        event.widget.insert(0, placeholder_text)
        event.widget.config(foreground="grey", font=placeholder_font)


def _enable_entry(var, entry):
    if var.get():
        entry.config(state="normal")
    else:
        entry.config(state="disabled")


def _get_selected_list():
    # Clear the current list
    selected_items = list()

    # Add selected pattern items to the list
    selected_items.extend(
        pattern for var, pattern in zip(checkbox_vars, patterns) if var.get()
    )

    # Add custom entries to the list if the checkbox is selected and entry is not empty
    selected_items.extend(
        entry.get() for var, entry in additional_vars if var.get() and entry.get()
    )

    if asterisk_var.get():
        selected_items.append("*")

    return selected_items


def _get_date_list():
    directory = cwd_entry_var.get()
    print(directory)
    log_files = os.listdir(directory)
    dates = sorted({p[4:14] for p in log_files})
    print(dates)
    return dates


if __name__ == "__main__":

    # GUI code execution
    # Set up the main application window
    root = tk.Tk()
    root.title("CAN Data Explorer")

    # Placeholder text and font settings
    placeholder_text = "Input the time to add in D HH MM SS format"
    placeholder_font = ("TkDefaultFont", 9, "italic")
    default_font = ("TkDefaultFont", 9)

    # Defining the elements of the window
    # Mainframe
    mainframe = ttk.Frame(root, padding=15)
    mainframe.grid(column=0, row=0)

    # Header
    header = ttk.Frame(mainframe)
    header.grid(column=0, row=0)

    # Load logos
    logo1_path = r"assets/iFOS_Logo_klein_transparent.png"
    logo2_path = r"assets/co2forit.png"

    logo1 = tk.PhotoImage(file=logo1_path)
    logo2 = tk.PhotoImage(file=logo2_path)

    # Add logos and title to the header
    logo1_label = ttk.Label(header, image=logo1)
    logo1_label.grid(column=0, row=0, padx=5)

    title_label = ttk.Label(
        header, text="CAN Data Explorer", font=("TkDefaultFont", 12, "bold")
    )
    title_label.grid(column=1, row=0, padx=20)

    logo2_label = ttk.Label(header, image=logo2)
    logo2_label.grid(column=2, row=0, padx=5)

    # Contents of Calculator tab
    lf = ttk.Labelframe(mainframe, text="Input Parameters", padding=10)
    lf.grid(column=0, row=0)

    # Working directory part
    script_folder = os.path.dirname(os.path.abspath(__file__))
    cache_file = script_folder + "/.cache.json"
    try:
        with open(cache_file, "r") as file:
            db = json.load(file)
            logs_path = db.get("logs_path")
            dbc_path = db.get("dbc_path")
    except FileNotFoundError:
        logs_path = dbc_path = None

    cwd = ttk.Label(lf, text="Select folder containing the .log files")
    cwd.grid(column=0, row=0, columnspan=4)

    cwd_entry_var = tk.StringVar(value=logs_path)
    cwd_entry = ttk.Entry(lf, textvariable=cwd_entry_var, width=117)
    cwd_entry.grid(column=0, row=1, columnspan=3)

    cwd_button = ttk.Button(lf, text="Browse...", command=_button_trigger_directory)
    cwd_button.grid(column=3, row=1)

    # Select DBC file
    DBC = ttk.Label(lf, text="Select the DBC file")
    DBC.grid(column=0, row=2, columnspan=3)

    DBC_entry_var = tk.StringVar(value=dbc_path)
    DBC_entry = ttk.Entry(lf, textvariable=DBC_entry_var, width=117)
    DBC_entry.grid(column=0, row=3, columnspan=3)

    DBC_button = ttk.Button(lf, text="Browse...", command=_button_trigger_file)
    DBC_button.grid(column=3, row=3)

    # Start date part
    st_date = ttk.Label(lf, text="Start date and time:")
    st_date.grid(column=0, row=4, columnspan=1)

    st_date_entry_var = tk.StringVar(value="2024-05-24")
    st_date_entry = ttk.Combobox(
        lf,
        textvariable=st_date_entry_var,
        values=_get_date_list(),
        postcommand=lambda: st_date_entry.configure(values=_get_date_list()),
    )
    st_date_entry.grid(column=0, row=5, columnspan=1)
    # TODO show days with data in calendar.

    st_time_entry_var = tk.StringVar(value="09:00:00")
    st_time_entry = ttk.Entry(
        lf, textvariable=st_time_entry_var, width=14, justify="center"
    )
    st_time_entry.grid(column=0, row=6, columnspan=1)

    # End date part
    end_date = ttk.Label(lf, text="End date and time:")
    end_date.grid(column=2, row=4, columnspan=1)

    end_date_entry_var = tk.StringVar(value="2024-05-24")
    end_date_entry = ttk.Combobox(
        lf,
        textvariable=end_date_entry_var,
        values=_get_date_list(),
        postcommand=lambda: end_date_entry.configure(values=_get_date_list()),
    )
    end_date_entry.grid(column=2, row=5, columnspan=1)

    end_time_entry_var = tk.StringVar(value="09:15:00")
    end_time_entry = ttk.Entry(
        lf, textvariable=end_time_entry_var, width=14, justify="center"
    )
    end_time_entry.grid(column=2, row=6, columnspan=1)

    # Create Notebook
    notebook = ttk.Notebook(mainframe)
    notebook.grid(column=0, row=1)

    # Create tabs
    calculator_tab = ttk.Frame(notebook, padding=10)
    chart_tab = ttk.Frame(notebook, padding=10)

    notebook.add(calculator_tab, text="Fuel Calculator")
    notebook.add(chart_tab, text="Diagrams")

    lf2 = calculator_tab

    run_code = ttk.Button(
        lf2,
        text="Calculate the fuel consumed in the time span selected above.",
        command=_run_progress_bar,
    )
    run_code.grid(
        column=0, row=0, sticky="ew", columnspan=4, pady=5
    )  # Center the button

    Progress = ttk.Progressbar(lf2, orient="horizontal", length=400, mode="determinate")

    header_text = (
        "start                                   end                                 fuel used     engine run time  \n"
        "──────────────────────────────────\n"
    )
    Output_label = ttk.Label(lf2, text=header_text)
    Output_label.grid(column=0, row=2, columnspan=4)

    patterns = [
        "Engine_Ext.*Pres*",
        "DT_Ext.*_Press",
        "*Pump_Press",
        "*Temp*",
        "*RPM*",
        "Engine_Ext.*",
        "*.FuelRate*",
        "*Pump_Q",
        "*Pump_V",
        "*.Drive_Dir",
        "*.Speed",
        "*.RearFrameLR_Angle",
        "*_Angle*",
        "*.TiltAngle",
        "*BoomTipPos_*",
        "*.ReqP1",
        "*.ReqP2",
        "*.ReqP3",
        "*.SpeReq",
        "Harvester_Mess.*",
        "HydrCooling.Fan_*",
    ]
    lf4 = chart_tab

    # Create two separate frames inside lf4
    lf4_left = ttk.Labelframe(lf4, text="Select which diagrams to show.", padding=5)
    lf4_left.grid(column=0, row=0)

    # Add checkboxes to the left frame in three columns
    checkbox_vars = []
    num_columns = 3
    num_rows = -(len(patterns) // -num_columns)
    for idx, pattern in enumerate(patterns):
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(lf4_left, text=pattern, variable=var)
        col = idx // num_rows
        row = idx % num_rows
        checkbox.grid(column=col, row=row, sticky="w", padx=5, pady=2)
        checkbox_vars.append(var)

    # Add a horizontal line to indicate that the rest is not in columns.
    line = ttk.Separator(lf4_left, orient="horizontal")
    line.grid(column=0, row=num_rows + 1, columnspan=num_columns * 2, sticky="ew")

    # Add additional checkboxes with text entry below the created ones
    additional_vars = []
    for i in range(3):
        var = tk.BooleanVar()
        entry = ttk.Entry(lf4_left, state="disabled", width=20)
        checkbox = ttk.Checkbutton(
            lf4_left,
            text=f"Custom {i+1}",
            variable=var,
            command=lambda v=var, e=entry: (_enable_entry(v, e)),
        )
        row = num_rows + 2 + i
        checkbox.grid(column=0, row=row, columnspan=1, sticky="w", padx=5, pady=2)
        entry.grid(column=1, row=row, columnspan=1, sticky="w", padx=5, pady=2)
        additional_vars.append((var, entry))

    # Add an extra checkbox for all remaining signals
    row += 1
    asterisk_var = tk.BooleanVar()
    checkbox = ttk.Checkbutton(
        lf4_left, text="all other signals", variable=asterisk_var
    )
    checkbox.grid(column=0, row=row, sticky="w", padx=5, pady=2)

    # Add link to the signal description in the bottom right
    help_button = ttk.Button(lf4_left, text="?", command=open_help_pdf)
    help_button.grid(column=num_columns * 2 - 1, row=row, sticky="e")

    # Add RUN button to the right frame
    _chart_run_code = ttk.Button(lf4, text="Draw the figure. ⏳", command=_chart_run)
    _chart_run_code.grid(column=0, row=1, sticky="ew", pady=10)

    # Ensure the frames resize properly
    lf4.grid_rowconfigure(0, weight=1)
    lf4.grid_columnconfigure(0, weight=3)  # Larger weight for left frame
    lf4.grid_columnconfigure(1, weight=1)  # Smaller weight for right frame

    root.mainloop()
