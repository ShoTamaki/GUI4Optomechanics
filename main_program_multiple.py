import numpy as np
import tkinter as tk
import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from plot_control_multiple import PlotControl
import pandas as pd
import os
path_cur = os.path.dirname(os.path.realpath(__file__))
os.chdir(path_cur)



FONT_TYPE = "Helvetica"

class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Member variables
        self.fonts = (FONT_TYPE, 15)
        self.pickle_filepath = None

        # Setup form
        self.setup_form()

    def setup_form(self):
        # Form design of CustomTkinter
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # Form size
        self.geometry("1400x800")
        self.title("Date plot")
        # self.minsize(300, 400)

        # Resize configuration
        self.grid_rowconfigure((0,1), weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1st frame setting
        # self.file_select = FileSelect(master=self)
        self.file_select = FileBox(master=self)
        self.file_select.grid(row=0, column=0, columnspan=1, padx=0, pady=20, sticky="ns")

        # 2nd frame setting
        self.plot_main_frame = PlotMainFrame(master=self, header_name="Plot", width=900)
        self.plot_main_frame.grid(row=0, column=1, columnspan=1, padx=0, pady=20, sticky="nsew")

    def update_canvas(self, pickle_filepath=None):
        """
        Update plot
        """
        if pickle_filepath is not None:
            self.pickle_filepath = pickle_filepath
        self.plot_main_frame.update(pickle_filepath=self.pickle_filepath)


# Initialize the main application window
class FileBox(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Folder Selection Button
        self.select_folder_button = customtkinter.CTkButton(
            self, text="Select Folder", command=self.select_folder
        )
        self.select_folder_button.grid(row=0,column=0,pady=10)

        # Frame for checkboxes
        self.file_frame = customtkinter.CTkScrollableFrame(self, width=300, height=600)
        self.file_frame.grid(row=1, column=0,pady=10, padx=20, sticky='ns')

        # Save selected files button
        self.save_button = customtkinter.CTkButton(
            self, text="Print Selected Files", command=self.print_selected_files
        )
        self.save_button.grid(row=2,column=0,pady=10)

        self.file_checkboxes = {}
        self.folder_path = ""

    def select_folder(self):
        # Select folder dialog
        self.folder_path = tk.filedialog.askdirectory()
        if not self.folder_path:
            return
        self.update_file_list()

    def update_file_list(self):
        # Clear existing checkboxes
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        # List .pickle files in the selected folder
        if self.folder_path:
            pickle_files = [
                f for f in os.listdir(self.folder_path) if f.endswith(".pickle") or f.endswith(".h5")
            ]
            if not pickle_files:
                tk.messagebox.showinfo("No Files", "No .pickle or .h5 file found in the folder.")
            else:
                for file in pickle_files:
                    var = customtkinter.StringVar(value="off")
                    checkbox = customtkinter.CTkCheckBox(
                        self.file_frame, text=file, variable=var, onvalue="on", offvalue="off"
                    )
                    checkbox.pack(anchor="w", padx=10, pady=5)
                    self.file_checkboxes[file] = var

    def print_selected_files(self):
        selected_files = [
            file for file, var in self.file_checkboxes.items() if var.get() == "on"
        ]
        if selected_files:
            print("Selected Files:", selected_files)
            full_path = [ self.folder_path+'/'+x for x in selected_files ]
            for file in full_path:
                # pickle_filepath = self.selected_file.get()
                # full_path = [ self.folder_path+'/'+x for x in file ]
                self.master.update_canvas(full_path)
        else:
            print("No files selected.")


class FileSelect(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.fonts = (FONT_TYPE, 15)

        self.setup_form()

    def setup_form(self):
        # Resize configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)

        # Variable to store the selected file
        self.selected_file = tk.StringVar(value="")

        # Select folder button
        self.select_folder_button = customtkinter.CTkButton(master=self, text="Select Folder", command=self.select_folder)
        self.select_folder_button.grid(row=0, column=0, padx=10, pady=10)

        # Scrollable frame for displaying files
        self.scrollable_frame = customtkinter.CTkScrollableFrame(master=self, height=600)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=20, sticky="ns")

        # Process button
        self.process_button = customtkinter.CTkButton(master=self, text="Plot Selected File", command=self.process_file)
        self.process_button.grid(row=2, column=0, padx=10, pady=10)


    def select_folder(self):
        folder_path = tk.filedialog.askdirectory()
        if folder_path:
            self.display_pickle_files(folder_path)

    def display_pickle_files(self, folder_path):
        # Clear the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get all .pickle files
        pickle_files = [f for f in os.listdir(folder_path) if f.endswith('.pickle') or f.endswith(".h5")]

        # Display files in the scrollable frame with radio buttons
        if pickle_files:
            for file in pickle_files:
                radio_button = customtkinter.CTkRadioButton(
                    self.scrollable_frame,
                    text=file,
                    variable=self.selected_file,
                    value=os.path.join(folder_path, file)
                )
                radio_button.pack(fill="x", pady=2, padx=5)
        else:
            no_files_label = customtkinter.CTkLabel(self.scrollable_frame, text="No .pickle or .h5 file found in the folder.")
            no_files_label.pack(pady=10)

    def display_checkbox(self, folder_path):
        # Clear the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get all .pickle files
        pickle_files = [f for f in os.listdir(folder_path) if f.endswith('.pickle') or f.endswith(".h5")]

        # Display files in the scrollable frame with radio buttons
        if pickle_files:
            for file in pickle_files:
                box = customtkinter.CTkCheckbox(
                    self.scrollable_frame,
                    text=file,
                    variable=self.selected_file,
                    value=os.path.join(folder_path, file)
                )
                box.pack(fill="x", pady=2, padx=5)
        else:
            no_files_label = customtkinter.CTkLabel(self.scrollable_frame, text="No .pickle or .h5 file found in the folder.")
            no_files_label.pack(pady=10)

    def process_file(self):
        # selected = self.selected_file.get()
        # print(selected)
        if self.selected_file.get() is not None:
            pickle_filepath = self.selected_file.get()
            self.master.update_canvas(pickle_filepath)
        # self.textbox.detele('1,0', tk.END)
        # self.textbox.insert('1.0', 'Hello!')


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

        # Setup form
        self.setup_form()
        

    def setup_form(self):

        # Resize configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0), weight=1)

        # # Import GUI setting frame (not used)
        # self.plot_edit_frame = PlotConfigFrame(master=self, header_name="Plot setting", plot_config=self.plot_control.config)
        # self.plot_edit_frame.grid(row=0, column=0, padx=18, pady=20, sticky="ns")

        # Import metadata frame
        self.meta_frame = MetaFrame(master=self, header_name="Metadata", plot_config=self.plot_control.config)
        self.meta_frame.grid(row=0, column=1, padx=0, pady=20, sticky="nsew")

        # Import canvas for the main frame
        self.canvas = FigureCanvasTkAgg(self.plot_control.fig,  master=self)
        self.canvas.get_tk_widget().grid(row=0,column=0, padx=20, pady=20, sticky="nsew")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.grid(row=1,column=0, padx=0, pady=20, sticky="nsew")

        # Save file button
        self.button_save = customtkinter.CTkButton(master=self, command=self.button_save_callback, text="Save as .png", font=self.fonts)
        self.button_save.grid(row=1, column=1, padx=0, pady=20, sticky="s")   

    def update(self, pickle_filepath=None, config=None):
        """
        Update plot and metadata
        """
        print(pickle_filepath)
        self.plot_control.replot(pickle_filepath, config)
        self.canvas.draw()
        self.toolbar.update()
        self.meta_frame.update(pickle_filepath=pickle_filepath)

    
    def button_save_callback(self):
        """
        When pressed, save png
        """
        filepath = self.plot_control.save_fig()
        if filepath is not None:
            tk.messagebox.showinfo("Success", f"Exported to {filepath}")


# Change plot line setting (not used)
class PlotConfigFrame(customtkinter.CTkFrame):
    """
    A subframe change plot line setting
    """
    def __init__(self, *args, header_name="PlotConfigFrame", plot_config=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        # Copy config of plog
        self.plot_config = plot_config.copy()
        # Setup form
        self.setup_form()

    def setup_form(self):
        # Resize configuration
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="nswe")

        # Select linewidth
        self.slider_label = customtkinter.CTkLabel(self, text="Linewidth 2.5", font=(FONT_TYPE, 13))
        self.slider_label.grid(row=1, column=0, padx=20, pady=(20,0), sticky="ew")

        self.slider = customtkinter.CTkSlider(master=self, from_=0.5, to=5, number_of_steps=9, hover=False, width=150, command=self.slider_event)
        self.slider.grid(row=2, column=0, padx=20, pady=(0,20), sticky="ew")

        # Select line type
        self.combobox_label = customtkinter.CTkLabel(self, text="Line type", font=(FONT_TYPE, 13))
        self.combobox_label.grid(row=3, column=0, padx=20, pady=(20,0), sticky="ew")

        self.combobox = customtkinter.CTkComboBox(master=self, font=self.fonts,
                                     values=["line", "dashed", "line + marker"],
                                     command=self.combobox_callback)
        self.combobox.grid(row=4, column=0, padx=20, pady=(0,20), sticky="ew")

    def slider_event(self, value):
        """
        Slider setting for linewidth
        """
        # Chech if value has changed
        old_label = self.slider_label.cget("text")
        new_label = f"Linewidth {value}"
        if old_label != new_label:
            # Update plot only when value has changed
            self.slider_label.configure(text=new_label)
            self.plot_config["linewidth"] = value
            self.master.update(config=self.plot_config)
    
    def combobox_callback(self,value):
        self.plot_config["linetype"] = value
        self.master.update(config=self.plot_config)


class MetaFrame(customtkinter.CTkFrame):
    ''' Show metadata '''
    def __init__(self, *args, header_name="Metadata", plot_config=None, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        # Copy config of plog
        self.plot_config = plot_config.copy()
        self.plot_control = PlotControl()
        # Setup form
        self.setup_form()

    def setup_form(self):
        """
        Setup of form design
        """
        # Resize configuration
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # self.cell = customtkinter.CTkScrollableFrame(self, width=300)
        # self.cell.grid(row=1, column=0, padx=20, sticky="ns")
    
    def update(self, pickle_filepath=None, config=None):
        # Clear metadata
        for widget in self.winfo_children():
            widget.destroy()

        self.cell = customtkinter.CTkScrollableFrame(self, width=350, height=600)
        self.cell.grid(row=0, column=0, padx=0, sticky="nsew")

        count = 0
        gap = 2
        for file_name in pickle_filepath:
            df = self.plot_control.show_meta(file_name, config)
            
            for i in np.arange(len(list(df.attrs.keys()))):
                if count ==0:
                    data = customtkinter.CTkLabel(self.cell, text=f'Curve {count+1}', anchor='center')
                    data.grid(row=count*len(list(df.attrs.keys())), column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
                
                    data = customtkinter.CTkLabel(self.cell, text=list(df.attrs.keys())[i], anchor="w")
                    data.grid(row=i+1+count*len(list(df.attrs.keys())) , column=0, padx=5, pady=5, sticky="nsew")

                    data = customtkinter.CTkLabel(self.cell, text=df.attrs[list(df.attrs.keys())[i]], anchor="w")
                    data.grid(row=i+1+count*len(list(df.attrs.keys())), column=1, padx=5, pady=5, sticky="nsew")
                    self.grid_columnconfigure(0, weight=1)

                else:
                    data = customtkinter.CTkLabel(self.cell, text='---------------------------------------', anchor='center')
                    data.grid(row=count*(len(list(df.attrs.keys()))+2+gap-1), column=0, columnspan=2,  padx=5, pady=5, sticky="nsew")

                    data = customtkinter.CTkLabel(self.cell, text=f'Curve {count+1}', anchor='center')
                    data.grid(row=count*(len(list(df.attrs.keys()))+2+gap), column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
                
                    data = customtkinter.CTkLabel(self.cell, text=list(df.attrs.keys())[i], anchor="w")
                    data.grid(row=i+count*(len(list(df.attrs.keys()))+3+gap), column=0, padx=5, pady=5, sticky="nsew")

                    data = customtkinter.CTkLabel(self.cell, text=df.attrs[list(df.attrs.keys())[i]], anchor="w")
                    data.grid(row=i+count*(len(list(df.attrs.keys()))+3+gap), column=1, padx=5, pady=5, sticky="nsew")
                    self.grid_columnconfigure(0, weight=1)

            count += 1




if __name__ == "__main__":
    app = App()
    app.mainloop()
