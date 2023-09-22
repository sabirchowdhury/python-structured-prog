import numpy as np


class Battery:

    def __init__(self, internalResistance, mass, SHC, currentBatTemp):
        self.internalResistance = internalResistance
        self.mass = mass
        self.SHC = SHC
        self.currentBatTemp = currentBatTemp



    def calcVoltage(self,percentageCharge):
        """ Returns the voltage given a charge percentage
            using interpolation
        :param percentageCharge: Value to be interpolated
        :type percentageCharge: real, int, float and other
        :return: A value of the voltage that was interpolated
        :rtype: float
        """

        # X points for interpolation
        xPoints=[0,0.05,0.1,0.2,0.4,0.6,0.8,1] 

        # Y points for interpolation
        yPoints=[0,1,10,15,19,20,20,20]

        # Interpolate our input paramter using
        # the defined X and Y points.
        # Uses try except to catch any errors
        try:
            return np.interp(percentageCharge,xPoints,yPoints)
        except:
            print("Error invalid parameter")
            return 0


    def calcTempChange(self, supplyCurrent, airTemperature = 20):

        """ Returns the temperature change given the ambient
            temperature and supply current
        :param supplyCurrent: current of the supply used to
                                calculate temperature change
        :type supplyCurrent: real, int, float and other

        :param airTemperature: the environment temperature,
                (defualts to 20)
        :type airTemperature: real, int, float and other

        :return: the dT/dt rate of change of temperature
                against time
        :rtype: float
        """
        # Uses try except clause to check any errors.
        try:
            # The three lines below incorperate the function to calculate
            # the temperature change rate. They are written on multiple lines
            # to reduce clogging. I've achieved this using the += and /= operators
            dTdt = (supplyCurrent**2) * self.internalResistance
            dTdt += 40*(airTemperature - self.currentBatTemp)
            dTdt /= self.mass*self.SHC
            # Returns the temperature change rate.
            return dTdt
        except:
            print("Error in input")
            return 0

    def updateTemp(self, supplyCurrent, airTemperature = 20, timeStepSize = 0.01):
        """ Returns the temperature change given the ambient
                temperature and supply current
        :param supplyCurrent: current of the supply used to calculate
                                temperature change
        :type supplyCurrent: real, int, float and other

        :param airTemperature: the environment temperature, defualts to 20
        :type airTemperature: real, int, float and other

        :return: the dT/dt rate of change of temperature against time
        :rtype: float
        """
        # Uses try except clause to check any errors.
        try:
            #Extracts the dT/dt calling the calcTempChange method, and stores in dTdt
            dTdt = self.calcTempChange(supplyCurrent, airTemperature)
            # Uses the formula to calculate the next battery temperature
            # using itself and the times step multiplied by the rate of change
            # 𝑇𝑛+1 = 𝑇𝑛 + Δ𝑇 ⋅ 𝑑𝑇/𝑑t
            self.currentBatTemp += timeStepSize*dTdt
        except:
            print("Error in input")


batteryX = Battery(0.01,50,1,70)
print(batteryX.calcVoltage(2))
print(batteryX.calcTempChange(10,20))
batteryX.updateTemp(10)
print(batteryX.currentBatTemp)


