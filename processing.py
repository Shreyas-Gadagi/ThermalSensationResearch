import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import linregress

class CalreaDataProcessor:
    def __init__(self, file_path, output_file):
        self.file_path = file_path
        self.output_file = output_file # the output file has to be changed
        self.t0_offset = -213  # Calibration offset for temperature
        self.s0 = 768  # Scaling factor for heat flux

    def calculate_temp_and_flux(self):
        """Processes the file to compute skin temperature and heat flux."""
        df = pd.read_csv(self.file_path, sep=",", skiprows=14)

        df["skin_temperature_C"] = (df["temp_a0 [mC]"] - self.t0_offset) / 1000
        df["heat_flux_W_m2"] = (df["hf_a0 [counts]"] * 1.953125) / (self.s0 / 1000)

        df.to_csv(self.output_file, index=False)
        print(f"Skin temperature and heat flux calculations saved to {self.output_file}")

    def extract_data(self, timestamp, interval):
        """Extracts averaged heat flux and skin temperature for a given timestamp and interval."""
        df = pd.read_csv(self.output_file, sep=",")
        df["time"] = pd.to_datetime(df["time [UTC-OFS=-0500]"], errors="coerce")

        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp, format="%m/%d/%Y %H:%M", errors="coerce")

        if pd.isna(timestamp):
            raise ValueError("Invalid timestamp format. Use 'MM/DD/YYYY HH:MM'.")

        start_time = timestamp - timedelta(minutes=interval)
        filtered_df = df[(df["time"] >= start_time) & (df["time"] < timestamp)]

        if filtered_df.empty:
            return {"average_skin_temperature": None, "average_heat_flux": None}

        avg_skin_temp = filtered_df["skin_temperature_C"].mean()
        avg_heat_flux = filtered_df["heat_flux_W_m2"].mean()

        return {"average_skin_temperature": avg_skin_temp, "average_heat_flux": avg_heat_flux}
    
    def calculate_gradient(self, filepath, column, interval, timestamp):
        """Computes the gradient (slope) using linear regression within a given timeframe. Takes the output file as the filepath. Computes gradient with time vs varible(column)"""
        df = pd.read_csv(self.output_file, sep=",")
        df["time"] = pd.to_datetime(df["time [UTC-OFS=-0500]"], errors="coerce")

        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp, format="%m/%d/%Y %H:%M", errors="coerce")

        if pd.isna(timestamp):
            raise ValueError("Invalid timestamp format. Use 'MM/DD/YYYY HH:MM'.")

        start_time = timestamp - timedelta(minutes=interval)
        filtered_df = df[(df["time"] >= start_time) & (df["time"] < timestamp)].copy()
        
        filtered_df["time_seconds"] = (filtered_df["time"] - filtered_df["time"].min()).dt.total_seconds()
        print(filtered_df)
        slope, _, _, _, _ = linregress(filtered_df["time_seconds"], filtered_df[column])
        return slope


class IButtonDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_data(self, timestamp, interval):
        """Extracts averaged temperature for a given timestamp and interval."""
        df = pd.read_excel(self.file_path, skiprows=24)
        timestamp = datetime.strptime(timestamp, "%m/%d/%Y %H:%M")
        start_time = timestamp - timedelta(minutes=interval)

        df = df.dropna(subset=["Date", "Time"])
        df["Date"] = df["Date"].astype(str).str.strip()
        df["Time"] = df["Time"].astype(str).str.strip()

        df = df[df["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
        df = df[df["Time"].str.match(r"\d{2}:\d{2}:\d{2}")]

        df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%Y-%m-%d %H:%M:%S")
        filtered_df = df[(df["DateTime"] >= start_time) & (df["DateTime"] <= timestamp)]

        mean_temp = filtered_df["Value"].mean()
        return {"averageTemperature": mean_temp}
    
    def calculate_gradient(self, timestamp, interval):
        df = pd.read_excel(self.file_path, skiprows=24)

        timestamp = datetime.strptime(timestamp, "%m/%d/%Y %H:%M")

        start_time = timestamp - timedelta(minutes=interval)

        df = df.dropna(subset=["Date", "Time"])
        df["Date"] = df["Date"].astype(str).str.strip()
        df["Time"] = df["Time"].astype(str).str.strip()

        df = df[df["Date"].str.match(r"\d{4}-\d{2}-\d{2}")]
        df = df[df["Time"].str.match(r"\d{2}:\d{2}:\d{2}")]

        df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%Y-%m-%d %H:%M:%S")
        filtered_df = df[(df["DateTime"] >= start_time) & (df["DateTime"] <= timestamp)].copy() 
        print(filtered_df)

        filtered_df["time_seconds"] = (filtered_df["DateTime"] - filtered_df["DateTime"].min()).dt.total_seconds()
        filtered_df["Value"] = pd.to_numeric(filtered_df["Value"], errors="coerce")

        print(filtered_df)
        slope, _, _, _, _ = linregress(filtered_df["time_seconds"], filtered_df["Value"])
        return slope
class TotalData:
    def __init__(self, timeinterval):
        self.timeinterval = timeinterval
        pass

    def populateData(timeinterval):
        #make sure to consider edge cases
        pass



# Example Usage
if __name__ == "__main__":
    calrea_processor = CalreaDataProcessor("CALERAresearch/2025-01-17T10-43-33.986Z_EE0BC45190C9.csv", "CALERAresearch/temperature_heat_flux_results.csv")
    calrea_processor.calculate_temp_and_flux()
    result1 = calrea_processor.extract_data("1/17/2025 10:00", 5)
    print(result1)

    result2 = calrea_processor.calculate_gradient(calrea_processor.output_file, "skin_temperature_C", 5, "1/17/2025 10:00")
    print(result2)


    # ibutton_processor = IButtonDataProcessor("IButton/01-17/A.xlsx")
    # result = ibutton_processor.calculate_gradient("1/17/2025 10:00", 5)
    # print(result)

    # result2 = ibutton_processor.extract_data("1/17/2025 10:00", 5)
    # print(result2)
    pass
