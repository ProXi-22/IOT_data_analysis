import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from PIL import Image, ImageTk


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IOT data analysis")
        self.center_window(self.root, 600, 300)

        self.sensors = {
            'Energy (kWh)': False,
            'Hot Water (L)': False,
            'Cold Water (L)': False,
            'Temperature (C)': False,
            'Humidity (%)': False
        }
        self.data = pd.DataFrame()
        self.create_widgets()

    def create_widgets(self):
        self.sensor_settings_button = tk.Button(self.root, text="Sensor settings", command=self.open_sensor_settings)
        self.sensor_settings_button.pack(pady=10)

        self.generate_data_button = tk.Button(self.root, text="Generate data", command=self.generate_data)
        self.generate_data_button.pack(pady=10)

        self.save_data_button = tk.Button(self.root, text="Save data", command=self.save_data)
        self.save_data_button.pack(pady=10)

        self.load_data_button = tk.Button(self.root, text="Load data", command=self.load_data)
        self.load_data_button.pack(pady=10)

        self.plot_data_button = tk.Button(self.root, text="Plot data", command=self.plot_data)
        self.plot_data_button.pack(pady=10)

        self.author_label = tk.Label(self.root, text="Author: Michał Stanisławski 55335")
        self.author_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.version_label = tk.Label(self.root, text="Version 1.0")
        self.version_label.pack(side=tk.RIGHT, padx=10, pady=10)

    def open_sensor_settings(self):
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Sensor Settings")
        self.center_window(self.settings_window, 300, 200)
        self.sensor_vars = {}
        for sensor in self.sensors:
            var = tk.BooleanVar(value=self.sensors[sensor])
            chk = tk.Checkbutton(self.settings_window, text=sensor, variable=var)
            chk.pack(anchor='w')
            self.sensor_vars[sensor] = var
        save_button = tk.Button(self.settings_window, text="Save", command=self.save_settings)
        save_button.pack(pady=10)

    def save_settings(self):
        for sensor, var in self.sensor_vars.items():
            self.sensors[sensor] = var.get()
        self.settings_window.destroy()

    def generate_data(self):
        date_rng = pd.date_range(start=datetime.datetime.now() - pd.DateOffset(years=1), end=datetime.datetime.now(),
                                 freq='h')
        data = {'timestamp': date_rng}
        if self.sensors['Energy (kWh)']:
            hours = date_rng.hour
            data['Energy (kWh)'] = np.where(
                (hours >= 6) & (hours < 22),
                np.random.uniform(1, 5, size=len(date_rng)),
                np.random.uniform(0.5, 2, size=len(date_rng))
            )
        if self.sensors['Hot Water (L)']:
            hours = date_rng.hour
            data['Hot Water (L)'] = np.where(
                (hours >= 6) & (hours < 9) | (hours >= 18) & (hours < 22),
                np.random.uniform(5, 15, size=len(date_rng)),
                np.random.uniform(0, 5, size=len(date_rng))
            )
        if self.sensors['Cold Water (L)']:
            hours = date_rng.hour
            data['Cold Water (L)'] = np.where(
                (hours >= 6) & (hours < 22),
                np.random.uniform(10, 20, size=len(date_rng)),
                np.random.uniform(0, 5, size=len(date_rng))
            )
        if self.sensors['Temperature (C)']:
            hour_of_day = date_rng.hour
            daily_variation = 2 * np.sin(2 * np.pi * hour_of_day / 24)
            base_temperature = 22
            data['Temperature (C)'] = base_temperature + daily_variation + np.random.uniform(-1, 1, size=len(date_rng))
        if self.sensors['Humidity (%)']:
            hour_of_day = date_rng.hour
            daily_variation = 10 * np.cos(2 * np.pi * hour_of_day / 24)
            base_humidity = 60
            data['Humidity (%)'] = base_humidity + daily_variation + np.random.uniform(-10, 10, size=len(date_rng))
        self.data = pd.DataFrame(data)

    def save_data(self):
        if not self.data.empty:
            filepath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
            if filepath:
                self.data.to_csv(filepath, index=False)

    def load_data(self):
        filepath = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if filepath:
            self.data = pd.read_csv(filepath)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            for sensor in self.sensors.keys():
                self.sensors[sensor] = sensor in self.data.columns

    def plot_data(self):
        if not self.data.empty:
            self.plot_window = tk.Toplevel(self.root)
            self.plot_window.title("Plot Data")
            self.center_window(self.plot_window, 800, 600)

            self.plot_frame = ttk.Frame(self.plot_window)
            self.plot_frame.pack(fill=tk.BOTH, expand=True)

            self.canvas = tk.Canvas(self.plot_frame)
            self.scrollbar = ttk.Scrollbar(self.plot_frame, orient=tk.VERTICAL, command=self.canvas.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.plot_content = ttk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.plot_content, anchor="nw")

            self.plot_content.bind("<Configure>", self.on_frame_configure)

            self.timeframe = tk.StringVar(value='Day')
            self.timeframe_options = ttk.Combobox(self.plot_content, textvariable=self.timeframe)
            self.timeframe_options['values'] = ('Day', 'Month', 'Year')
            self.timeframe_options.pack(pady=10)

            self.date_entry = tk.Entry(self.plot_content)
            self.date_entry.pack(pady=10)

            self.plot_button = tk.Button(self.plot_content, text="Update Plot", command=self.update_plot)
            self.plot_button.pack(pady=10)

            self.energy_label = tk.Label(self.plot_content, text="Total Energy (kWh): 0")
            self.energy_label.pack(pady=5)
            self.hot_water_label = tk.Label(self.plot_content, text="Total Hot Water (L): 0")
            self.hot_water_label.pack(pady=5)
            self.cold_water_label = tk.Label(self.plot_content, text="Total Cold Water (L): 0")
            self.cold_water_label.pack(pady=5)

            self.plot_area = tk.Label(self.plot_content)
            self.plot_area.pack(fill=tk.BOTH, expand=True)

            self.update_plot()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_plot(self):
        timeframe = self.timeframe.get().lower()
        date_str = self.date_entry.get()

        if timeframe == 'day':
            try:
                selected_date = pd.to_datetime(date_str)
                start_date = selected_date
                end_date = selected_date + pd.DateOffset(days=1)
                date_format = '%H'
                x_label = 'Hour'
                resample_rule = 'h'
            except ValueError:
                return
        elif timeframe == 'month':
            try:
                selected_date = pd.to_datetime(date_str)
                start_date = selected_date.replace(day=1)
                end_date = (selected_date.replace(day=1) + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
                date_format = '%d'
                x_label = 'Day'
                resample_rule = 'D'
            except ValueError:
                return
        elif timeframe == 'year':
            try:
                selected_date = pd.to_datetime(date_str)
                start_date = selected_date.replace(month=1, day=1)
                end_date = selected_date.replace(month=12, day=31)
                date_format = '%m'
                x_label = 'Month'
                resample_rule = 'M'
            except ValueError:
                return

        data = self.data[(self.data['timestamp'] >= start_date) & (self.data['timestamp'] < end_date)]
        data.set_index('timestamp', inplace=True)
        active_sensors = [sensor for sensor in self.sensors if self.sensors[sensor]]
        if not active_sensors:
            return

        fig, axes = plt.subplots(nrows=len(active_sensors), ncols=1, figsize=(8, len(active_sensors) * 4))
        axes = axes.flatten() if len(active_sensors) > 1 else [axes]
        for i, sensor in enumerate(active_sensors):
            if sensor in data.columns:
                if 'Water' in sensor or 'Energy' in sensor:
                    grouped_data = data.resample(resample_rule).sum()
                else:
                    grouped_data = data.resample(resample_rule).mean()

                ax = axes[i]
                grouped_data[sensor].plot(kind='bar' if 'Water' in sensor or 'Energy' in sensor else 'line', ax=ax)
                ax.set_title(sensor)
                ax.set_xlabel(x_label)
                ax.set_ylabel(sensor.split()[-1])
                ax.set_xticklabels(grouped_data.index.strftime(date_format), rotation=45)
                ax.yaxis.set_major_locator(plt.MaxNLocator(10))

        fig.tight_layout()
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img = Image.fromarray(img)
        self.imgtk = ImageTk.PhotoImage(image=img)
        self.plot_area.configure(image=self.imgtk)
        self.energy_label.config(
            text=f"Total Energy (kWh): {data['Energy (kWh)'].sum() if 'Energy (kWh)' in data.columns else 0:.2f}")
        self.hot_water_label.config(
            text=f"Total Hot Water (L): {data['Hot Water (L)'].sum() if 'Hot Water (L)' in data.columns else 0:.2f}")
        self.cold_water_label.config(
            text=f"Total Cold Water (L): {data['Cold Water (L)'].sum() if 'Cold Water (L)' in data.columns else 0:.2f}")

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f'{width}x{height}+{x}+{y}')

root = tk.Tk()
app = SensorApp(root)
root.mainloop()
