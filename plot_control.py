import os

import customtkinter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.constants import c, hbar
from scipy.optimize import curve_fit

from FitFunctions import Functions


class PlotControl:
    def __init__(self) -> None:
        plt.style.use("dark_background")
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        # Config setting for plot
        self.config = {"linewidth": 1, "linetype": "line", "upper": 1, "lower": 0}
        # Config setting for fit
        self.fit_config = {
            "FitFunc": "None",
            "WidthRatio": None,
            "WidthRatio_sub": None,
        }
        self.filepath = None
        self.df = None

    def get_dataframe(self, filename=None):
        # Update data when file name is set
        if filename is not None:
            # Read file data
            self.filepath = filename
            if self.filepath.endswith(".pickle"):
                df = pd.read_pickle(filename)

            elif self.filepath.endswith(".h5"):
                # Read DataFrame and retrieve attributes
                with pd.HDFStore(filename) as store:
                    df = store["df"]  # Load the DataFrame
                    df.attrs = store.get_storer("df").attrs.metadata

            return df
        else:
            df = None

        if df is None:
            return

    def update_dataframe(self, filename=None, fit_dict=None):
        """This is to add fitted parametes etc. to the metadata of the file"""
        # Update data when file name is set
        if filename is None:
            return
        else:
            # Read file data
            self.filepath = filename
            if self.filepath.endswith(".pickle"):
                df = pd.read_pickle(self.filepath)

            elif self.filepath.endswith(".h5"):
                # Read DataFrame and retrieve attributes
                with pd.HDFStore(self.filepath) as store:
                    df = store["df"]  # Load the DataFrame
                    df.attrs = store.get_storer("df").attrs.metadata

        if fit_dict is not None:
            df.attrs.update(fit_dict)

        if self.filepath.endswith(".pickle"):
            df.to_pickle(self.filepath)

        elif self.filepath.endswith(".h5"):
            # Store DataFrame to HDF5 with a key
            with pd.HDFStore(self.filepath) as store:
                store.put("df", df)
                # Add an attribute
                store.get_storer("df").attrs.metadata = df.attrs

    def replot(self, filename=None, config=None, fit_config=None):
        """
        Update plot
        """
        # Update data when file name is set
        if filename is not None:
            # Read file data
            self.filepath = filename
            if self.filepath.endswith(".pickle"):
                self.df = pd.read_pickle(filename)

            elif self.filepath.endswith(".h5"):
                # Read DataFrame and retrieve attributes
                with pd.HDFStore(filename) as store:
                    self.df = store["df"]  # Load the DataFrame
                    self.df.attrs = store.get_storer("df").attrs.metadata

        if self.df is None:
            print("df is None")
            return

        # Update when configuration is set
        if config is not None:
            self.config.update(config)

        if fit_config is not None:
            self.fit_config.update(fit_config)

        # Clear plot before update
        self.ax.clear()

        # Set upper and lower limit
        up = int(self.config["upper"] * len(self.df[list(self.df.keys())[0]]))
        low = int(self.config["lower"] * len(self.df[list(self.df.keys())[0]]))

        # plot
        # Different types of plot (not usually used)
        if self.config["linetype"] == "line + marker":
            self.ax.plot(
                self.df[list(self.df.keys())[0]][low:up],
                self.df[list(self.df.keys())[1]][low:up],
                "o-",
                linewidth=self.config["linewidth"],
            )

        elif self.config["linetype"] == "dashed":
            self.ax.plot(
                self.df[list(self.df.keys())[0]][low:up],
                self.df[list(self.df.keys())[1]][low:up],
                "--",
                linewidth=self.config["linewidth"],
            )
        else:
            self.ax.plot(
                self.df[list(self.df.keys())[0]][low:up],
                self.df[list(self.df.keys())[1]][low:up],
                linewidth=self.config["linewidth"],
            )

        self.ax.set_xlabel(list(self.df.keys())[0])
        self.ax.set_ylabel(list(self.df.keys())[1])
        self.fig.tight_layout()

        if self.fit_config["FitFunc"] is not None:
            if self.fit_config["FitFunc"] != "None":
                try:
                    para = self.create_fitting(
                        file_name=self.filepath,
                        fit_config=self.fit_config,
                        config=self.config,
                        up=up,
                        low=low,
                    )
                    fit_dict = {}
                    fit_dict[self.fit_config["FitFunc"] + "_offset"] = para[0]
                    fit_dict[self.fit_config["FitFunc"] + "_eigenfrequency"] = para[1]
                    fit_dict[self.fit_config["FitFunc"] + "_amplitude"] = para[2]
                    fit_dict[self.fit_config["FitFunc"] + "_linewidth"] = para[3]
                    self.update_dataframe(filename=self.filepath, fit_dict=fit_dict)
                    return fit_dict
                except:
                    return

            else:
                # print('FitFunc is None')
                return

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

    def create_fitting(
        self, file_name, fit_config=None, config=None, up=None, low=None
    ):
        self.df = self.get_dataframe(file_name)

        x = list(self.df[list(self.df.keys())[0]][low:up])
        y = list(self.df[list(self.df.keys())[1]][low:up])

        if fit_config["WidthRatio"] is not None:
            width_ratio = fit_config["WidthRatio"]
        else:
            width_ratio = 0.5

        # Mechanical Lorentzian
        if fit_config["FitFunc"] == "Lorentz":
            offset = 0.5 * (np.mean(y[:10]) + np.mean(y[-10:]))
            height = np.nanmax(y) - offset
            x0 = x[np.nanargmax(y)]
            dx = (np.max(x) - np.min(x)) * width_ratio
            try:
                para, cov = curve_fit(
                    Functions.Lorentz, x, y, p0=[offset, x0, height, dx]
                )
            except:
                return

            # Plot fitting curve if successful
            new_x = list(
                np.arange(np.min(x), np.max(x), (np.max(x) - np.min(x)) / 1000)
            )
            self.ax.plot(
                new_x, Functions.Lorentz(new_x, para[0], para[1], para[2], para[3])
            )
            self.fig.tight_layout()
            print("Lorentz fit is done")
            return para

        # Calibration tone (Gaussian)
        elif fit_config["FitFunc"] == "Gauss":
            offset = 0.5 * (np.mean(y[:10]) + np.mean(y[-10:]))
            height = np.nanmax(y) - offset
            x0 = x[np.nanargmax(y)]
            dx = (np.max(x) - np.min(x)) * width_ratio
            para, cov = curve_fit(Functions.Gauss, x, y, p0=[offset, x0, height, dx])
            # Plot fitting curve if successful
            if para is not None:
                new_x = list(
                    np.arange(np.min(x), np.max(x), (np.max(x) - np.min(x)) / 1000)
                )
                self.ax.plot(
                    new_x, Functions.Gauss(new_x, para[0], para[1], para[2], para[3])
                )
                self.fig.tight_layout()
                # print("Gauss fit is done")
                return para

        # Optical resonance
        elif fit_config["FitFunc"] == "Fano":
            offset = 0.5 * (np.mean(y[:5]) + np.mean(y[-5:]))
            height = np.nanmin(y) - offset
            x0 = x[np.nanargmin(y)]
            dx = (np.max(x) - np.min(x)) * width_ratio
            q = 0.1
            try:
                para, cov = curve_fit(
                    Functions.Fano, x, y, p0=[offset, x0, height, dx, q]
                )
            except:
                return

            # Plot fitting curve if successful
            if para is not None:
                new_x = list(
                    np.arange(np.min(x), np.max(x), (np.max(x) - np.min(x)) / 1000)
                )
                self.ax.plot(
                    new_x,
                    Functions.Fano(new_x, para[0], para[1], para[2], para[3], para[4]),
                )
                self.fig.tight_layout()
                # print("Fano fit is done")
                return para

        # # Gorodetsky with smaller calibration freq
        # elif fit_config["FitFunc"] == "Gorodetsky_Left":
        #     offset = 0.5 * (np.mean(y[:5]) + np.mean(y[-5:]))

        #     # Index at half of data point
        #     half = int(len(x) / 2)

        #     # Mechanical Lorentzian parameters
        #     Lheight = np.nanmin(y[half:]) - offset
        #     Lx0 = x[np.nanargmin(y[half:])]
        #     Ldx = (np.max(x[half:]) - np.min(x[half:])) * width_ratio

        #     # Gaussian tone parameters
        #     Gheight = np.nanmin(y[:half]) - offset
        #     Gx0 = x[np.nanargmin(y[:half])]
        #     Gdx = (np.max(x[:half]) - np.min(x[:half])) * width_ratio_sub

        #     para, cov = curve_fit(
        #         Functions.Gorodetsky,
        #         x,
        #         y,
        #         p0=[offset, Lx0, Lheight, Ldx, Gx0, Gheight, Gdx],
        #     )

        #     if para is not None:
        #         new_x = list(
        #             np.arange(np.min(x), np.max(x), (np.max(x) - np.min(x)) / 1000)
        #         )
        #         self.ax.plot(
        #             new_x,
        #             Functions.Fano(
        #                 new_x,
        #                 para[0],
        #                 para[1],
        #                 para[2],
        #                 para[3],
        #                 para[4],
        #                 para[5],
        #                 para[6],
        #             ),
        #         )
        #         self.fig.tight_layout()
        #         # print("Gorodetsky fit is done")
        #         return para

        #     return

        # elif fit_config["FitFunc"] == "None":
        #     return

        else:
            return

    # Esticate g0 based on fitted parameters
    def estimate_g0(
        self,
        mech_freq,
        mech_height,
        gamma,
        mod_freq,
        mod_height,
        ENBW,
        Vpi,
        mod_power_dBm,
        power_loss=1.34**-1,
    ):
        # Physical constants
        self.kb = 1.380649e-23
        self.planck = 6.62607015e-34
        self.temperature = 273.15 + 21
        # Voltages to get modulation depth
        # V_pi = 6 # Value from the iXblue spec sheet at 10GHz. 9V for 16GHz and 4V for 50kHz
        # V = (965e-5)*2 # For -40dBm and ENBW = 30kHz,
        V_pi = Vpi  # 6.5 # Thorlabs EOM
        valon_power = mod_power_dBm  # dBm
        valon_power = 10 ** (valon_power / 10) * 1e-3
        valon_V = np.sqrt(power_loss * valon_power * 50)
        V = valon_V * np.sqrt(2)
        beta = V / V_pi * np.pi

        nth = 1.0 / (np.exp(self.planck * mech_freq / (self.kb * self.temperature)) - 1)
        # '''Below calculates g0. gamma should be expressed in angular frequency so it's multiplied by 2pi while ENBW is in direct frequency.'''
        g0 = np.sqrt(
            0.5
            / nth
            * (beta**2)
            * (abs(mod_freq) ** 2)
            / 2
            * abs(mech_height)
            * abs(gamma)
            * 2
            * np.pi
            / 4
            / (abs(mod_height) * ENBW)
        )
        return g0


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
