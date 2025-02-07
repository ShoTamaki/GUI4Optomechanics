import os
import tkinter as tk

import customtkinter
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from plot_control import PlotControl

path_cur = os.path.dirname(os.path.realpath(__file__))
os.chdir(path_cur)


FONT_TYPE = "Helvetica"


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Member variables
        self.fonts = (FONT_TYPE, 15)
        self.data_filepath = None

        # Setup form
        self.setup_form()

    def setup_form(self):
        # Form design of CustomTkinter
        customtkinter.set_appearance_mode(
            "dark"
        )  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme(
            "blue"
        )  # Themes: blue (default), dark-blue, green

        # Form size
        self.geometry("1200x800")
        self.title("Date plot")

        # Resize configuration
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((1), weight=1)

        # 1st frame setting
        self.file_select = FileSelect(master=self, width=300)
        self.file_select.grid(
            row=0, column=0, columnspan=1, padx=0, pady=10, sticky="nsew"
        )

        # 2nd frame setting
        self.plot_main_frame = PlotMainFrame(master=self, header_name="Plot", width=900)
        self.plot_main_frame.grid(
            row=0, column=1, columnspan=1, padx=0, pady=10, sticky="nsew"
        )

    def update_canvas(self, data_filepath=None):
        """
        Update plot
        """
        if data_filepath is not None:
            self.data_filepath = data_filepath
        self.plot_main_frame.update(data_filepath=self.data_filepath)


class FileSelect(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)

        self.curr_path = None

        self.setup_form()

    def setup_form(self):
        # Resize configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=0)

        # Variable to store the selected file
        self.selected_file = tk.StringVar(value="")

        # Select folder button
        self.select_folder_button = customtkinter.CTkButton(
            master=self, text="Select Folder", command=self.select_folder
        )
        self.select_folder_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")

        # Update current folder
        self.update_folder_button = customtkinter.CTkButton(
            master=self, text="Update", command=self.update_folder
        )
        self.update_folder_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")

        # Scrollable frame for displaying files
        self.scrollable_frame = customtkinter.CTkScrollableFrame(master=self, width=300)
        self.scrollable_frame.grid(
            row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ns"
        )

        # Process button
        self.process_button = customtkinter.CTkButton(
            master=self, text="Plot!!", command=self.process_file
        )
        self.process_button.grid(row=2, column=0, padx=5, pady=5, sticky="ns")

    def select_folder(self):
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.display_data_files(folder_path)
            self.curr_path = folder_path

    def update_folder(self):
        if self.curr_path is not None:
            self.display_data_files(self.curr_path)

    def display_data_files(self, folder_path):
        # Clear the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get all data files
        data_files = [
            f
            for f in os.listdir(folder_path)
            if f.endswith(".pickle") or f.endswith(".h5")
        ]

        # Display files in the scrollable frame with radio buttons
        if data_files:
            for file in data_files:
                radio_button = customtkinter.CTkRadioButton(
                    self.scrollable_frame,
                    text=file,
                    variable=self.selected_file,
                    value=os.path.join(folder_path, file),
                )
                radio_button.pack(fill="x", pady=2, padx=5)
        else:
            no_files_label = customtkinter.CTkLabel(
                self.scrollable_frame, text="No .pickle or h5 file found in the folder."
            )
            no_files_label.pack(pady=10)

    def process_file(self):
        # selected = self.selected_file.get()
        # print(selected)
        if self.selected_file.get() is not None:
            data_filepath = self.selected_file.get()
            self.master.update_canvas(data_filepath)


class PlotMainFrame(customtkinter.CTkFrame):
    """
    Main frame for plotting
    """

    def __init__(self, *args, header_name="PlotMainFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        # Import plot function from external file
        self.plot_control = PlotControl()

        self.data_pathname = None

        # Setup form
        self.setup_form()

    def setup_form(self):
        # Resize configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # Import canvas for the main frame
        self.canvas = FigureCanvasTkAgg(self.plot_control.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0, sticky="nwes")

        # Import metadata frame
        self.meta_frame = MetaFrame(
            master=self,
            header_name="Metadata",
            plot_config=self.plot_control.config,
            fit_config=self.plot_control.fit_config,
        )
        self.meta_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nwes")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.grid(row=1, column=0, padx=10, pady=0, sticky="nwes")

        # # Save file button
        # self.button_save = customtkinter.CTkButton(master=self, command=self.button_save_callback, text="Save as .png", font=self.fonts)
        # self.button_save.grid(row=1, column=1, padx=10, pady=10, sticky="s")

        # Import curve fitting frame
        self.range_frame = PlotRange(
            master=self,
            header_name="Range",
            data_pathname=self.data_pathname,
            plot_config=self.plot_control.config,
            fit_config=self.plot_control.fit_config,
        )
        self.range_frame.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )

    def update(self, data_filepath=None, config=None, fit_config=None):
        """Update fit curve"""
        fit_config = {}
        fit_config["FitFunc"] = self.range_frame.get_func()
        try:
            fit_config["WidthRatio"] = float(self.range_frame.entry_width.get())
        except:
            fit_config["WidthRatio"] = None

        # Get fitting parameters if fitted
        try:
            fit_dict = self.plot_control.replot(
                data_filepath, config, fit_config
            )  # Return fitted parameters
        except:
            fit_dict = None

        self.canvas.draw()
        self.toolbar.update()
        self.meta_frame.update(data_filepath=data_filepath, fit_dict=fit_dict)
        self.range_frame.g0_window(data_filepath=data_filepath, fit_dict=fit_dict)

    def button_save_callback(self):
        """
        When pressed, save png
        """
        filepath = self.plot_control.save_fig()
        if filepath is not None:
            tk.messagebox.showinfo("Success", f"Exported to {filepath}")


class MetaFrame(customtkinter.CTkScrollableFrame):
    """Show metadata"""

    def __init__(
        self, *args, header_name="Metadata", plot_config=None, fit_config=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        # Copy config of plog
        self.plot_config = plot_config.copy()
        self.fit_config = fit_config.copy()
        self.plot_control = PlotControl()
        # Setup form
        self.setup_form()

    def setup_form(self):
        """
        Setup of form design
        """
        # Resize configuration
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure((0, 1), weight=1)

        self.cell = customtkinter.CTkLabel(
            self, text=self.header_name, font=(FONT_TYPE, 13), width=400
        )
        self.cell.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nwes")

    def update(self, data_filepath=None, fit_dict=None):
        df = self.plot_control.get_dataframe(data_filepath)

        if df is not None:
            for widget in self.winfo_children():
                widget.destroy()

            for i in np.arange(len(list(df.attrs.keys()))):
                cell = customtkinter.CTkLabel(
                    self,
                    text=list(df.attrs.keys())[i],
                    anchor="center",
                    # width=150,
                    # height=30,
                )
                cell.grid(row=i, column=0, padx=5, pady=5, sticky="nwes")
                cell = customtkinter.CTkLabel(
                    self,
                    text=df.attrs[list(df.attrs.keys())[i]],
                    anchor="center",
                    # width=150,
                    # height=30,
                )
                cell.grid(row=i, column=1, padx=5, pady=5, sticky="nwes")


class PlotRange(customtkinter.CTkFrame):
    """Control plot range"""

    def __init__(
        self,
        *args,
        header_name="Plot range",
        data_pathname=None,
        plot_config=None,
        fit_config=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        # Import plot function from external file
        self.plot_control = PlotControl()
        self.plot_config = plot_config.copy()
        self.fit_config = fit_config.copy()
        self.data_pathname = data_pathname

        # Setup form
        self.setup_form()

    def setup_form(self):
        """
        Setup of form design
        """
        # Resize configuration
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)

        # Slider for upper limit for plot
        self.slider_label_upper = customtkinter.CTkLabel(
            self, text=f"Upper limit 1", font=(FONT_TYPE, 13)
        )
        self.slider_label_upper.grid(row=0, column=0, padx=10, sticky="we")
        self.slider_upper = customtkinter.CTkSlider(
            master=self,
            from_=0,
            to=1,
            number_of_steps=100,
            hover=True,
            width=400,
            command=self.slider_upper,
        )
        self.slider_upper.grid(row=0, column=1, padx=0, pady=10, sticky="ew")
        self.slider_upper.set(1)

        # Slider for lower limit
        self.slider_label_lower = customtkinter.CTkLabel(
            self, text=f"Lower limit 0", font=(FONT_TYPE, 13)
        )
        self.slider_label_lower.grid(row=1, column=0, padx=10, sticky="we")
        self.slider_min = customtkinter.CTkSlider(
            master=self,
            from_=0,
            to=1,
            number_of_steps=100,
            hover=True,
            width=400,
            command=self.slider_lower,
        )
        self.slider_min.grid(row=1, column=1, padx=10, sticky="ew")
        self.slider_min.set(0)

        # Select fit function
        self.func_label = customtkinter.CTkLabel(
            self, text=f"Fitting Function", font=(FONT_TYPE, 13)
        )
        self.func_label.grid(row=2, column=0, padx=10, sticky="we")
        self.combo_func = customtkinter.CTkComboBox(
            self,
            font=self.fonts,
            values=["None", "Lorentz", "Gauss", "Fano"],
            command=None,
        )
        self.combo_func.grid(row=2, rowspan=1, column=1, padx=10, pady=10, sticky="we")

        # Entry for fitting linewidth
        self.entry_width = customtkinter.CTkEntry(
            self, placeholder_text="FitWidth/PlotRange"
        )
        self.entry_width.grid(row=2, column=2)

        # Text to show Gorodetsky
        self.text_Gor = customtkinter.CTkLabel(self, text="Gorodetsky")
        self.text_Gor.grid(row=3, column=0, pady=10)
        self.Gor_result = customtkinter.CTkLabel(self, text="")
        self.Gor_result.grid(row=3, column=1, padx=0, pady=0)

    def slider_upper(self, value):
        old_label = self.slider_label_upper.cget("text")
        new_label = f"Upper limit {value:.2f}"
        if old_label != new_label:
            # Update plot only when value has changed
            self.slider_label_upper.configure(text=new_label)
            self.plot_config["upper"] = value
            self.master.update(config=self.plot_config)

    def slider_lower(self, value):
        old_label = self.slider_label_lower.cget("text")
        new_label = f"Lower limit {value:.2f}"
        if old_label != new_label:
            # Update plot only when value has changed
            self.slider_label_lower.configure(text=new_label)
            self.plot_config["lower"] = value
            self.master.update(config=self.plot_config)

    def get_func(self):
        if self.combo_func is not None:
            # self.fit_config['FitFunc'] = self.combo_func.get()
            return self.combo_func.get()

        return

    # Below is to show g0
    def g0_window(self, data_filepath=None, fit_dict=None):
        for widget in self.Gor_result.winfo_children():
            widget.destroy()

        df = self.plot_control.get_dataframe(data_filepath)
        if df is None:
            return

        if "Lorentz_offset" in df.attrs:
            if "Gauss_offset" in df.attrs:
                # Get Gorodetsky result
                mech_freq = df.attrs["Lorentz_eigenfrequency"]
                mech_height = df.attrs["Lorentz_amplitude"]
                gamma = df.attrs["Lorentz_linewidth"]
                mod_freq = df.attrs["mod_frequency"]
                mod_height = df.attrs["Gauss_amplitude"]
                ENBW = df.attrs["ENBW"]
                Vpi = df.attrs["Vpi"]
                mod_power_dBm = df.attrs["mod_power_dBm"]
                if "power_loss" in df.attrs:
                    power_loss = df.attrs["power_loss"]
                else:
                    power_loss = 1.34**-1

                g0 = self.plot_control.estimate_g0(
                    mech_freq,
                    mech_height,
                    gamma,
                    mod_freq,
                    mod_height,
                    ENBW,
                    Vpi,
                    mod_power_dBm,
                    power_loss,
                )

                self.Gor_result = customtkinter.CTkLabel(
                    self, text=f"g0/2pi [kHz] =  {g0*1e-3:.3f}"
                )
                self.Gor_result.grid(row=3, column=1, padx=0, pady=0)
            else:
                return
        else:
            return


if __name__ == "__main__":
    app = App()
    app.mainloop()
