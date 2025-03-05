import os

import customtkinter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class PlotControl:
    def __init__(self):
        plt.style.use("dark_background")
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        # Config setting
        self.config = {"linewidth": 1, "linetype": "line"}
        self.filepath = None
        self.df = None

    def replot(self, filename=None, config=None):
        """
        Update plot
        """
        # Clear plot before update
        self.ax.clear()

        count = 0
        for file in filename:
            # Update data when file name is set
            if file is not None:
                # Read file data
                # self.filepath = file
                # self.df = pd.read_pickle(file)

                self.filepath = file
                if self.filepath.endswith(".pickle"):
                    self.df = pd.read_pickle(self.filepath)

                elif self.filepath.endswith(".h5"):
                    # Read DataFrame and retrieve attributes
                    with pd.HDFStore(self.filepath) as store:
                        self.df = store["df"]  # Load the DataFrame
                        self.df.attrs = store.get_storer("df").attrs.metadata

            if self.df is None:
                return

            # Update when configuration is set
            if config is not None:
                self.config.update(config)

            # plot
            # Different types of plot (not usually used)
            if self.config["linetype"] == "line + marker":
                self.ax.plot(
                    self.df[list(self.df.keys())[0]],
                    self.df[list(self.df.keys())[1]],
                    "o-",
                    linewidth=self.config["linewidth"],
                    label=f"Curve {count+1}",
                )

            elif self.config["linetype"] == "dashed":
                self.ax.plot(
                    self.df[list(self.df.keys())[0]],
                    self.df[list(self.df.keys())[1]],
                    "--",
                    linewidth=self.config["linewidth"],
                    label=f"Curve {count+1}",
                )
            else:
                self.ax.plot(
                    self.df[list(self.df.keys())[0]],
                    self.df[list(self.df.keys())[1]],
                    linewidth=self.config["linewidth"],
                    label=f"Curve {count+1}",
                )

            self.ax.set_xlabel(list(self.df.keys())[0])
            self.ax.set_ylabel(list(self.df.keys())[1], labelpad=0)
            self.ax.legend()
            count += 1

        self.fig.tight_layout()

    def save_fig(self, export_path=None):
        """
        Save figure
        """
        # File name setting
        if export_path is None and self.filepath is not None:
            file, ext = os.path.splitext(self.filepath)
            export_path = f"{file}.png"

        if export_path is None:
            return

        self.fig.savefig(export_path)
        return export_path

    def show_meta(self, filename=None, config=None):
        # Update data when file name is set
        if filename is not None:
            # Read file data
            self.filepath = filename
            if self.filepath.endswith(".pickle"):
                self.df = pd.read_pickle(self.filepath)
                # Return the file data to main
                return self.df

            elif self.filepath.endswith(".h5"):
                # Read DataFrame and retrieve attributes
                with pd.HDFStore(self.filepath) as store:
                    self.df = store["df"]  # Load the DataFrame
                    self.df.attrs = store.get_storer("df").attrs.metadata
                return self.df

        if self.df is None:
            return


# if __name__ == "__main__":
#     # Export sample csv
#     filename = "./sample_data.csv"
#     time = np.linspace(0.0, 3.0)
#     y = np.sin(2*np.pi*time)
#     out_df = pd.DataFrame(data={"time": time, "y": y})
#     out_df.to_csv(filename)

#     # Plot graph
#     plot_control = PlotControl()
#     plot_control.replot(filename)
#     plot_control.save_fig("test1.png")

#     # Change line style
#     config = plot_control.config.copy()
#     config["linewidth"] = 5
#     plot_control.replot(config=config)
#     plot_control.save_fig("test2.png")
