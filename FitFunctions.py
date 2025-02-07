import numpy as np
import scipy


class Functions:
    def __init__(self) -> None:
        return

    def Lorentz(x, offset, x0, height, dx):
        return offset + height * (1 + (x - x0) ** 2 / (dx / 2) ** 2) ** -1

    def Fano(x, offset, x0, height, dx, q):
        return (
            offset
            + height
            * (1 - q**2 - q / dx * (x - x0))
            * (1 + (x - x0) ** 2 / (dx / 2) ** 2) ** -1
        )

    def Gauss(x, offset, x0, height, dx):
        return offset + height * np.exp(-((x - x0) ** 2) / (2 * dx**2))

    # def Gorodetsky(x, offset, Lx0, Lheight, Ldx, Gx0, Gheight, Gdx):
    #     Lorentz = Lheight * (1 + (x - Lx0) ** 2 / (Ldx / 2) ** 2) ** -1
    #     Gauss = Gheight * np.exp(-((x - Gx0) ** 2) / (2 * Gdx**2))
    #     return Lorentz + Gauss + offset
