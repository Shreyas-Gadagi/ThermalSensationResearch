import pandas as pd
from datetime import datetime, timedelta

file_path = "CALERAresearch/2025-01-17T10-43-33.986Z_EE0BC45190C9.csv"

# Have to do this for every file
def calculateTempAndFlux(filepath):
    df = pd.read_csv(file_path, sep=",", skiprows=14)

    t0_offset = -213  
    s0 = 768  

    df["skin_temperature_C"] = (df["temp_a0 [mC]"] - t0_offset) / 1000

    df["heat_flux_W_m2"] = (df["hf_a0 [counts]"] * 1.953125) / (s0 / 1000)

    output_file = "CALERAresearch/temperature_heat_flux_results.csv"
    df.to_csv(output_file, index=False)

    print(f"Skin temperature and heat flux calculations saved to {output_file}")

# Give a certain time-stamp, and it will return average heat flux and temperature
# from the newly created temperature_heat_flux_results.csv.
def extract_calrea_data(filepath, timestamp, interval):
    """
    Reads a CALREA CSV file, extracts sensor data within a 5-minute window before a given timestamp, 
    and computes the averaged skin temperature and heat flux.
    """
    df = pd.read_csv(filepath, sep=",", skiprows=14)

    df["time"] = pd.to_datetime(df["time [UTC-OFS=-0500]"], errors="coerce")

    t0_offset = -213  
    s0 = 768  

    df["skin_temperature_C"] = (df["temp_a0 [mC]"] - t0_offset) / 1000
    df["heat_flux_W_m2"] = (df["hf_a0 [counts]"] * 1.953125) / (s0 / 1000)

    if isinstance(timestamp, str):
        timestamp = pd.to_datetime(timestamp, format="%m/%d/%Y %H:%M", errors="coerce")
    
    if pd.isna(timestamp):
        raise ValueError("Invalid timestamp format. Use 'MM/DD/YYYY HH:MM'.")

    start_time = timestamp - timedelta(minutes=interval)
    
    filtered_df = df[(df["time"] >= start_time) & (df["time"] < timestamp)]
    print(filtered_df)
    
    if filtered_df.empty:
        return {"average_skin_temperature": None, "average_heat_flux": None}
    
    #calculate value from filtered_df
    avg_skin_temp = filtered_df["skin_temperature_C"].mean()
    avg_heat_flux = filtered_df["heat_flux_W_m2"].mean()

    #apply gradient as well
    
    return {"average_skin_temperature": avg_skin_temp, "average_heat_flux": avg_heat_flux}

# # Example Usage
# file_path = "CALERAresearch/2025-01-17T10-43-33.986Z_EE0BC45190C9.csv"
# result = extract_calrea_data(file_path, "1/17/2025 10:00", 5)
# print(result)

def extractIButtonData(filepath, timestamp, interval):
    df = pd.read_excel(filepath, skiprows=24)

    timestamp = datetime.strptime(timestamp, "%m/%d/%Y %H:%M")
    print(type(timestamp), timestamp)  # Debugging output to confirm conversion

    start_time = timestamp - timedelta(minutes=interval)

    df = df.dropna(subset=["Date", "Time"])

    df["Date"] = df["Date"].astype(str).str.strip()
    df["Time"] = df["Time"].astype(str).str.strip()

    df = df[df["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]  # Ensure Date is YYYY-MM-DD
    df = df[df["Time"].str.match(r"\d{2}:\d{2}:\d{2}")]  # Ensure Time is HH:MM:SS

    df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%Y-%m-%d %H:%M:%S")

    filtered_df = df[(df["DateTime"] >= start_time) & (df["DateTime"] <= timestamp)]

    meanTemp = filtered_df["Value"].mean()






extractIButtonData("IButton/01-17/A.xlsx", "1/17/2025 10:00", 5)
    