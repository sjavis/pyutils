#!/usr/bin/env python3
import numpy as np


class UnitConverter:
    m: float
    s: float
    kg: float


    def __init__(self, verbose=True, dx=None, dt=None, kg=None, viscosity=None, viscosity_si=None):
        # This can be extended to use other units too

        # Set up the unit matrix and the vector of ratios of the lattice and physical values
        dimensions = [] # Powers of dimensions for each unit: meters, seconds, kilograms
        value_ratios = []
        if (dx is not None):
            dimensions.append([1, 0, 0])
            value_ratios.append(1/dx)
        if (dt is not None):
            dimensions.append([0, 1, 0])
            value_ratios.append(1/dt)
        if (kg is not None):
            dimensions.append([0, 0, 1])
            value_ratios.append(kg)
        if (viscosity is not None) and (viscosity_si is not None):
            dimensions.append([-1, -1, 1])
            value_ratios.append(viscosity / viscosity_si)
        if (len(dimensions)!=3) or (len(value_ratios)!=3):
            raise Exception("Three values are needed to initialise the unit converter.")

        # Invert the unit matrix to find the values for m, s, kg
        inv_dimensions = np.linalg.inv(dimensions)
        units = np.ones(3)
        for i in range(3):
           for j in range(3):
                units[i] = units[i] * value_ratios[j]**inv_dimensions[i,j] # Matrix multiplication with linear operators of multiplication and raising to a power
        self.m, self.s, self.kg = units

        if (verbose): print(self)


    def __str__(self):
        return "Unit Converter:\n" + \
              f"1 metre    = {self.m} l.u.\n" + \
              f"1 second   = {self.s} l.u.\n" + \
              f"1 kilogram = {self.kg} l.u."


    def toLattice(self, value, m=0, s=0, kg=0):
        return value * self.m**m * self.s**s * self.kg**kg


    def toSI(self, value, m=0, s=0, kg=0):
        return value / self.m**m / self.s**s / self.kg**kg



if (__name__ == "__main__"):
    units = UnitConverter(dx=0.1, dt=1, viscosity=10, viscosity_si=1e-3)
    print()
    print("10 meters in lattice units:", units.toLattice(10, m=1))
    print("10 lattice units of energy in Joules:", units.toSI(10, m=2, s=-2, kg=1))
