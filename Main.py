import math
import numpy as np
import copy
import sys

 
#To use my testing function, type "python Circuit.py Test" into the command line



class circuitBlock:
    # circuitBlock - type: Class
    # Description: Each object represents a component defined in the input.
    # These objects have many functionalities and can perform the necessary
    # actions for circuit analysis.

    def __init__(self, node1, node2, component, value):

        # Instantiation method: This method is called when the object is defined.
        # This class first orders the nodal connections, saves the relecant information
        # in the parameters of the object. This method also uses the input, interprets the
        # information, processes it and saves it. This way, when the object needs to
        # perform calculations, it can just refer to its own parameters that are already
        # defined.

        # Inputs: [node1 : String], [node2 : String], [component : String], [value : float]

        # Outputs: null

        # sorting the node order
        self.n1 = node1
        self.n2 = node2
        if (node1 > node2 and node2 != 0) or node1 == 0:
            self.n1 = node2
            self.n2 = node1

        #Storing and initialising all values.
        self.matrix = np.array([[1, 0j], [0j, 1]])
        self.type = component.upper()
        self.series = True
        self.val = value
        self.oneover = False
        self.freqdependant = False
        self.a = self.matrix[0, 0]
        self.b = self.matrix[0, 1]
        self.c = self.matrix[1, 0]
        self.d = self.matrix[1, 1]

        # Processing the inputs to interpret them into meaningful data
        if self.type in ["G", "C"]:
            self.oneover = True
        if self.type in ["L", "C"]:
            self.freqdependant = True
        if self.n2 == 0:
            self.series = False
        elif abs(self.n1-self.n2) == 1:
            self.series = True


    def applyFreq(self, frequency=0):

        # Method: applyFreq
        # since a component can be a capacitor or an inductor the ABCD
        # matrix can be frequency dependant. To attain numerical values for
        # the ABCD matrix, we must apply a frequency to these frequency dependant
        # components. This method essentially obtains numerical values and for
        # resistors, it initalises the ABCD matrix with the correct values.


        # Inputs: [frequency : float] - set to zero by default.

        # Outputs: null

        # Creats the omega constant for frequency dependant components.
        omega = 2j*math.pi*frequency
        z = self.val

        # figures out what ABCD matrix format to use based on the node connections
        # and component type.
        if self.freqdependant:
            z = z*omega
        if self.oneover:
            z = 1/z
        if self.series:
            self.matrix[0, 1] = z
        else:
            self.matrix[1, 0] = 1/z
        self.a = self.matrix[0, 0]
        self.b = self.matrix[0, 1]
        self.c = self.matrix[1, 0]
        self.d = self.matrix[1, 1]

    def multM(self, multiplierObject):

        # Method: multM
        # Takes in a object as an input and multiplies both of thier
        # ABCD matricies together to create a resultant transmission
        # matrix. The order of multiplication is self*inputObject

        # Input: [multiplierObject: Object circuitBlock]

        # Output: null

        #Performs a matrix multiplication and stors it in its own ABCD matrix
        # it also redifned A,B,C,D and the nodal start and end connections.

        self.matrix = np.matmul(self.matrix, multiplierObject.matrix)
        self.n2 = multiplierObject.n2
        self.a = self.matrix[0, 0]
        self.b = self.matrix[0, 1]
        self.c = self.matrix[1, 0]
        self.d = self.matrix[1, 1]

    def VAPIn(self, Rs, Rl, Source, SourceType):
        # Method: VAPIn
        # Given the source resistance, the load resistance,
        # source type and source value, this method works out the
        # input voltage, current and power.

        # Input : [Rs : float], [Rl : float], [Source : float], [SourceType: Integer]

        # Output : [v1 : Complex],[i1 : Complex],[Pin : Complex]

        Zinp = self.Zin(Rl)             #Uses own methods to calculate the input impedance.
        if SourceType == 1:             #Represents a voltage source.
            v1 = (Zinp/(Zinp+Rs))*Source
        elif SourceType == 2:           #Represents a current source.
            v1 = Source/((1/Rs)+(1/Zinp))
        i1 = v1/Zinp
        Pin = v1*np.conjugate(i1)
        return v1, i1, Pin

    def Zin(self, Rl):
        #Method: Zin
        #This method takes in the source resistance and calculates
        #the input impedance of the component using the load resistance
        #equation

        # Input : [Rl : float]

        # Output : [Complex]
        return (self.a*Rl + self.b) / (self.c*Rl + self.d)

    def Zout(self, Rs):
        # Method  : Zout
        # This uses the equation for calculating the output impedance
        # using the source resistance.

        # Input : [Rs : float]

        # Output : [Complex]

        
        return (self.d*Rs + self.b) / (self.c*Rs + self.a)

    def AvAi(self, Rl):
        # Method  : AvAi
        # This uses the equation for calculating the voltage and current gains
        # using the load resistance.

        # Input : [Rl : float]

        # Output : [Av : Complex],[Ai : Complex]
        Av = Rl/(self.a*Rl+self.b)
        Ai = 1/(self.c*Rl+self.d)
        return Av, Ai

    def VAPout(self, Vin, Iin, Rl):
        # Method  : VAPout
        # This uses the equation for calculating the output voltage, current and pwoer
        # using the input voltages and current and load resistances to attain gain..

        # Input : [Vin : float],[Iin : float],[Rl : float]

        # Output : [vout, Complex],[iout : Complex],[pout : Complex]
        Av,Ai=self.AvAi(Rl)
        vout=Vin*Av
        iout=Iin*Ai
        pout = vout*np.conjugate(iout)
        return vout, iout, pout

    def calculateAll(self, Rs, Rl, Source, SourceType):
        # Method  : calculateAll
        # This method uses all of the other methods used for calculating all values
        # wihtin itslef to create a dictionary of all output values.

        # Input : [Rs : float], [Rl : float], [Source : float], [SourceType: Integer]

        # Output : [AllValues : Dictionary]

        #Calls all of its methods to calculate all values
        Zinp = self.Zin(Rl)
        Zoutp = self.Zout(Rs)
        Vin, Iin, Pin = self.VAPIn(Rs, Rl, Source, SourceType)
        Vout, Iout, Pout = self.VAPout(Vin, Iin, Rl)
        Av, Ai = self.AvAi(Rl)

        #Sorts out the values and creates a dictionary from it.
        AllValues = {
            "Vin": Vin,
            "Vout": Vout,
            "Iin": Iin,
            "Iout": Iout,
            "Pin": Pin,
            "Zout": Zoutp,
            "Pout": Pout,
            "Zin": Zinp,
            "Av": Av,
            "Ai": Ai
        }
        return AllValues


def NodeSorter(unsortedCircuit):
    # Function : NodeSorter
    # Since all nodes can be defined in any order, it is important that we sort them
    # This allows for correct matrix multiplications. This method also has validation checks
    # To ensure that the circuit definition isnt corrupt.

    #Inputs: [unsortedCircuit : circuitBlock List]

    #Output: [error : boolean],  [sortedCircuit : circuitBlock List]

    # Sorts the circuit with the n1 key as the parameter to define the order.
    sortedCircuit = sorted(unsortedCircuit, key=lambda block: (block.n1 , block.n2))
    allSeries = []
    order = 0
    #Validation checks
    for component in sortedCircuit:  # checks duplicates not parallel, checks valid node number not negative and no node skips, no same node connection
        if component.n1 <= 0:  # node 1 is zero or negative
            return True, sortedCircuit
        if component.n1 == component.n2:  # both nodes are the same
            return True, sortedCircuit
        if component.n1 - order > 1:  # node1 has an increase more than 1 from the previous node
            return True, sortedCircuit
        else:
            order = component.n1
        if component.n2 != 0:  # if its not parallel
            if [component.n1, component.n2] in allSeries:  # and if the series already exists
                return True, sortedCircuit
            allSeries.append([component.n1, component.n2])
    # no problems return true and the sorted array.
    return False, sortedCircuit

def InputRead(FileLines):
    #Function : InputRead
    # This is the main bulk of the program converting the user input into
    # meaningful data. Using this data, the program extracts relevant information
    # and begins to define the circuit block order. It also defines the frequency
    # range and values.

    # Input: [FileLines: String List]

    # Output: [error:boolean], [unsortedCircuit: circuitBlock List], [Source: float],
    #   [Sourcetype: String], [RSval: flaot], [RLval: float], [Frequencies: float List], [OutputOrder: String 2D List (2 Columns)]

    #Variables defined for validation checks
    circuitOpen = False
    unsortedCircuit = []
    termsOpen = False
    outputOpen = False
    Loadfound = False
    Sourcetype = 0  # 0 not found, 1 voltage, 2 current.
    RSfound = False
    Freqtype = 0  # 0 not found, 1 is linear, 2 is logarithmic (START)
    Freqtype2 = 0  # 0 not found, 1 is linear, 2 is logarithmic (END)
    noff = False
    error = False
    OutputOrder = []
    FrequencyDependant = False
    circuitTag=False
    termsTag=False
    outputTag=False
    expPref= ["a","f","p","n","u","m","k","M","G","T","P","E"]
    #Checks each line in the file lines list
    
    for word in FileLines:
        #removes all comments
        word,_,_=word.partition("#")

        #Tries to match the line with a tag name to evaluate what
        # is being defined.
        if word == "<CIRCUIT>":
            circuitOpen = True
        if word == "</CIRCUIT>":
            if circuitOpen==True:
                circuitTag=True
            circuitOpen = False
        if word == "<TERMS>":
            termsOpen = True
        if word == "</TERMS>":
            if termsOpen==True:
                termsTag=True
            termsOpen = False
        if word == "<OUTPUT>":
            outputOpen = True
        if word == "</OUTPUT>":
            if outputOpen==True:
                outputTag=True
            outputOpen = False

        #If the circuit tag is open:
        if circuitOpen == True:
            lineword = word.split()
            if len(lineword)>0:
                if len(lineword[0]) > 1:

                    #Joins the prefix with the previous item - had to implement this as initially
                    # I assumed the number and prefix wouldnt have a space in between.
                    for num,delPref in enumerate(lineword):
                        if delPref in expPref and num !=0:
                            lineword[num-1]=lineword[num-1]+lineword[num]
                            lineword.pop(num)

                    #Checks if the line is relevant and stores it accordingly
                    #Program allows the order of each variable to be in any order. (using "in")

                    if lineword[0][0:2].upper() in ["N1", "N2", "C=", "R=", "G=", "L="]:
                        
                        n1found = False
                        n2found = False
                        compfound = False
                        #Goes through each item in lineword to iterate through each variable definition
                        for termword in lineword:
                            #Seperates item by equals sign
                            namevalue = termword.split("=")
                            if len(namevalue)>1:
                                #The following lines filter the line into their category
                                #And store them, updating the necessary values.
                                if namevalue[0].upper() == "N1":
                                    n1found = True
                                    try:
                                        n1 = int(namevalue[1])
                                    except:
                                        n1found=False
                                elif namevalue[0].upper() == "N2":
                                    n2found = True
                                    try:
                                        n2 = int(namevalue[1])
                                    except:
                                        n2found=False
                                elif namevalue[0].upper() in ["C", "R", "G", "L"]:
                                    compfound = True
                                    compValue = ValueConvert(namevalue[1])  #Allows for conversion if the
                                                                            #value is defined using exponent prefix
                                    if compValue == "error":
                                        compfound=False
                                    elif compValue<=0:
                                        compfound=False
                                    else:
                                        compName = namevalue[0].upper()
                                        if compName in ["C", "L"]:
                                            FrequencyDependant = True
                                else:# If the line has other uncommented random words, create an error
                                    error=True
                            else:# If the line has other uncommented random words, create an error
                                error=True
                        #Validation checks to see if all three definitions were found. and that the series nodes
                        # definition is correct

                        if n1found == True and n2found == True and compfound == True:
                            unsortedCircuit.append(circuitBlock(n1, n2, compName, compValue))
                            if abs(n1-n2)>1 and n1*n2 !=0:
                                error = True
                        else:
                            #If the component was to be defined but there was missing information
                            #an error is flagged
                            error = True

        if termsOpen == True:
            lineword = word.split()
            # used lineword because whitespace is removed
            if len(lineword)>0:
                if len(lineword[0])>2:
                    #Joins the prefix with the previous item
                    for num,delPref in enumerate(lineword):
                        if delPref in expPref and num !=0:
                            lineword[num-1]=lineword[num-1]+lineword[num]
                            lineword.pop(num)
                    #Checks if the information in the line is relevant variables or comments
                    if lineword[0][0:2].upper() in ["VT", "RS", "RL", "IN", "GS", "FS", "FE", "NF", "LF"]:
                        #iterates through each word in the line that is split by a space
                        for termword in lineword:
                            namevalue = termword.split("=")
                            #Filters again to check if a varible is being defined
                            # If it is, the relevant variables and validity checks are performed.
                            # For each variable, it is checked if it is part of the variables the program is looking for
                            # If the program matches with it, the boolean to signify that the variable is found is turned to true
                            # 
                            # Validation checks are carreid out on each variable - these check if it is a suitable value


                            if len(namevalue)>1:
                                if namevalue[0].upper() == "VT":
                                    Sourcetype = 1
                                    Source = ValueConvert(namevalue[1])
                                    if Source == "error":
                                        Sourcetype = 0
                                    elif Source <=0:
                                        Sourcetype=0
                                if namevalue[0].upper() == "IN":
                                    Sourcetype = 2
                                    Source = ValueConvert(namevalue[1])
                                    if Source == "error":
                                        Sourcetype = 0
                                    elif Source <=0:
                                        Sourcetype=0
                                if namevalue[0].upper() == "RS":
                                    RSfound = True
                                    RSval = ValueConvert(namevalue[1])
                                    if RSval == "error":
                                        RSfound = False
                                    elif RSval <0:
                                        RSfound=False
                                if namevalue[0].upper() == "GS":
                                    RSfound = True
                                    try:
                                        RSval = 1/ValueConvert(namevalue[1])
                                    except:
                                        RSval="error"
                                    if RSval == "error":
                                        RSfound = False
                                    elif RSval <0:
                                        RSfound=False
                                if namevalue[0].upper() == "RL":
                                    Loadfound = True
                                    RLval = ValueConvert(namevalue[1])
                                    if RLval == "error":
                                        Loadfound = False
                                    elif RLval <=0:
                                        Loadfound=False
                                if namevalue[0].upper() == "FSTART":
                                    Freqtype = 1
                                    FStart = ValueConvert(namevalue[1])
                                    if FStart == "error":
                                        Freqtype = 0
                                    elif FStart <0:
                                        Freqtype=0
                                if namevalue[0].upper() == "FEND":
                                    Freqtype2 = 1
                                    Fend = ValueConvert(namevalue[1])
                                    if Fend == "error":
                                        Freqtype2 = 0
                                    elif Fend <0:
                                        Freqtype2=0
                                if namevalue[0].upper() == "NFREQS":
                                    noff = True
                                    try:
                                        numFreq = int(namevalue[1])
                                        if numFreq<=0:
                                            noff=False
                                    except:
                                        noff = False

                                if namevalue[0].upper() == "LFSTART":
                                    Freqtype = 2
                                    FStart = ValueConvert(namevalue[1])
                                    if FStart == "error":
                                        Freqtype = 0
                                    elif FStart <0:
                                        Freqtype=0
                                if namevalue[0].upper() == "LFEND":
                                    Freqtype2 = 2
                                    Fend = ValueConvert(namevalue[1])
                                    if Fend == "error":
                                        Freqtype2=0
                                    elif Fend <0:
                                        Freqtype2=0

        # if the output tag is open:
        if outputOpen == True:
            lineword = word.split()  # Check its not a comment
            # used lineword because whitespace is removed
            #checks if the line is defining a output variable name
            if len(lineword)>0:
                if lineword[0] in ["Vin", "Vout", "Iin", "Iout", "Pin", "Pout", "Zin", "Zout", "Av", "Ai"]:
                    if len(lineword) > 1:
                        #If it is, store the unit and name
                        OutputOrder.append([lineword[0], lineword[1]])
                    else:
                        #If there isnt any unit use L as the unit.
                        OutputOrder.append([lineword[0], "L"])

    #Validity checks
    #Checks all the required terms are defined
    if not(RSfound and Loadfound and noff) or Freqtype * Freqtype2 * Sourcetype == 0 or Freqtype != Freqtype2 or unsortedCircuit==[]:
        error = True
    #Checks if the circuits impedance is frequency dependant but the user defined a frequency that is DC.
    elif (FStart == 0 or Fend == 0) and FrequencyDependant:
        error = True
    #Can not to fourier transform if the frequencies arent equally spaced.
    if Fourier==True and Freqtype == 2:
        error=True
    if not(circuitTag and termsTag and outputTag) or OutputOrder==[]:
        error=True
    if error == True:
        return error, [], 0, 0, 0, 0, [], []
    #Otherwise, based on the type of frequency create an array that contains the frequencies required.
    else:
        if Freqtype == 1:
            Frequencies = np.linspace(FStart, Fend, numFreq)
        if Freqtype == 2:
            Frequencies = np.logspace(np.log10(FStart), np.log10(Fend), numFreq)
        return error, unsortedCircuit, Source, Sourcetype, RSval, RLval, Frequencies, OutputOrder

def ValueConvert(value, unit="", name=""):
    # Function : ValueConvert
    # This function converts a value with an exponent attatched to it
    # or can attatch a prefix to a value. This function also calculates the
    # dB if the output requires it.

    # Convert from complex number to required output form:
    # Input : [value: Complex],
    #   [unit : String], [name : String]
    # Output: [float]

    # Convert from String to float mode (input reading):
    # Input : [value: String]
    # Output: [Magnitude : float],[Phase : float]
    #                   or
    # Output: [Real : float],[Imaginary : float]

    #Dictionary with all exponents
    """

        >>> ValueConvert("2n")
        2e-09
        >>> ValueConvert("300u")
        0.0003
        >>> ValueConvert("1m")
        0.001
        >>> ValueConvert("1k")
        1000.0
        >>> ValueConvert("1M")
        1000000.0
        >>> ValueConvert("1G")
        1000000000.0
        >>> ValueConvert("1H")
        'error'
        
    """
    exponent = {
        "a": 1e-18,
        "f": 1e-15,
        "p": 1e-12,
        "n": 1e-9,
        "u": 1e-6,
        "m": 1e-3,
        "k": 1e3,
        "M": 1e6,
        "G": 1e9,
        "T": 1e12,
        "P": 1e15,
        "E": 1e28
    }

    #If the unit is empty then the function is in input reading mode.
    if unit == "":
        try:
            #First checks if the value is a float already
            return float(value)
        except:
            # If it isnt, that means there is an exponent attatched
            # So the float is multiplied by the exponent
            try:
                return exponent[value[-1]]*float(value[0:-1])
            except:
                #If the exponent is invalid an error is thrown
                return "error"
    else:
        if "dB" in unit:  # then check exponent prefix for things like dBuV
            unit = unit.replace("dB", "")
            try:
                # checks if the unit has an exponent attatched to it
                # also checks if the name of the output is any of the gains
                # as they require a different calculations.
                # If an exponent prefix is required, the program devides by the necessary component
                mltp=20
                if name == "Pin" or name == "Pout":
                    mltp=10
                return mltp*np.log10(np.abs(value)/exponent[unit[0]]), np.angle(value)
            except:
                try:
                    #If there is no exponent, the calculations wihtout exponents are carried out.
                    mltp=20
                    if name == "Pin" or name == "Pout":
                        mltp=10
                    return mltp*np.log10(np.abs(value)), np.angle(value)
                except:#If an invalid unit is defined the program will end up here
                    outputfile.close()
                    exit()
        try:
            return value.real/exponent[unit[0]], value.imag/exponent[unit[0]]
        except:
            return value.real, value.imag


                            ################################
                                #   START OF PROGRAM    #
                            ################################

#UNIT TESTING
def Testing():
    #Cannot Use Doctest as these are too complex and require outside files.

    
    print("Class 'circuitBlock' Test Started:")
    fail=False
    TestFile=open("TestingData.csv","r")
    #This is from prior knowledge, i know all variables are stored in this order.
    #It will be used to extract the output order in the excel file
    allTerms=["Vin", "Vout", "Iin", "Iout", "Pin", "Pout", "Zin", "Zout", "Av", "Ai"]
    for LineNum,TestFileLine in enumerate(TestFile):
        linein=TestFileLine.replace("\n","").split(",")
        if LineNum%5==1:#Every 5n+1 line
            
            #Known Order Save all values from the file in thier corresponding variables
            n1=int(linein[0])
            n2=int(linein[1])
            Rs=float(linein[2])
            Rl=float(linein[3])
            Frqs=float(linein[4])
            CompN=linein[5]
            CompV=float(linein[6])
            SrcType=int(linein[7])
            SrcVal=float(linein[8])

            #Create a component depending on the variables above
            Node=circuitBlock(n1,n2,CompN,CompV)
        if LineNum%5==3:#Every 5n+3 line
            works=False
            try:#Uses try to check if its computable

                #applies a frequency and calculates all outputs depending on the file input
                Node.applyFreq(Frqs)
                answer=Node.calculateAll(Rs,Rl,SrcVal,SrcType)
                works=True
            except:
                #If there was an error, the file should also show error - otherwise it fails the test
                if linein[0]!="error":#TODO: Doctest
                    fail=True
            if works == True:
                listOfAnswers=[answer[allTermsx] for allTermsx in allTerms]#Iterates through each value in file
                #and stores it in an array

                #Compares every output in the file agains the output from the calculateAll dictionary values
                # If any arent matching, the boolean fail will be true.
                for count,compareVal in enumerate(listOfAnswers):
                    compareValRound=round(compareVal.real,5)+round(compareVal.imag,5)*1j
                    if compareValRound != complex(linein[count]):#TODO:DOCTEST
                        fail=True

    #Final Result
    if fail:
        print("Test Failed\n")
    else:
        print("All Tests Passed\n")
    TestFile.close()
    
    original=[]
    Test2=[]
    TestFile2=open("ValidFile.net","r")
    for Tline in TestFile2:
        Test2.append(Tline.replace("\n", ""))
        original.append(Tline.replace("\n", ""))
    TestFile2.close()



    print("Class 'circuitBlock' Test Multiple Elements:")#multiple elements
    fail=False
    Rs=50
    Rl=50
    Vs=5
    A = circuitBlock(1, 0, "R", 150)
    B = circuitBlock(1, 2, "R", 150)
    A.applyFreq()
    B.applyFreq()
    A.multM(B)
    answersTest=[3.2,0.79,0.037,0.016,0.12,0.012,86,190,0.25,0.43]
    dictOut=A.calculateAll(Rs, Rl, Vs, 1)
    for indexx,nameDict in enumerate(allTerms):
        compareVal=dictOut[nameDict]
        compareValRound=float("{:.1e}".format(compareVal.real))
        if compareValRound!=answersTest[indexx]:
            fail=True
    if fail:
        print("Test Failed\n")
    else:
        print("Test Passed\n")


    print("Valid Test 1 for InputRead()")
    error, Circ, Source, Sourcetype, RSval, RLval, Frequencies, OutOrd=InputRead(Test2)

    t1f=False

    correctOrd=[['Vin', 'V'], ['Vout', 'V'], ['Iin', 'A'], ['Iout', 'A'], ['Pin', 'W'], ['Zout', 'Ohms'], ['Pout', 'W'], ['Zin', 'Ohms'], ['Av', 'L'], ['Ai', 'L']]
    if OutOrd!=correctOrd:
        t1f=True
    
    if len(Circ)!=10:
        t1f=True
    correct=[[4,0,82],[4,5,25000],[2,0,1e-05],[2,3,150],[4,0,1.25e-05],[6,0,100],[5,6,2],[3,4,3.3],[5,0,3e-09],[1,2,47000]]
    for g in range(0,10):
        comparex=[Circ[g].n1,Circ[g].n2,Circ[g].val]
        if comparex!=correct[g]:
            t1f=True

    if error or t1f or Source !=5 or Sourcetype != 1 or RSval != 50 or RLval != 75 or (Frequencies != [10,20,30,40]).any():
        print("Failed")
    else:

        print("Passed")
    





    print("Valid Test 2 for InputRead()")
    #Modifying the file so all definitions are on the same line and
    # It uses a logarithmic sweep
    for _ in range(0,6):
        Test2.pop(20)
    Test2[20]=Test2[20].replace("#","")
    _, _, _, _, _, _, Frequencies, _=InputRead(Test2)
    if (Frequencies == [10,100,1000,10000,100000,1000000,10000000]).all():
        print("Passed")
    else:
        print("Failed")


    print("\nInvalid tests inside <circuit> tag:\n")
    print("Invalid Test 3 for InputRead()")
    Test3=original.copy()
    Test3[0]=""
    error, _, _, _, _, _, _, _=InputRead(Test3)
    if error:
        print("Passed")
    else:
        print("Failed")

    
    print("Invalid Test 4 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3.5 n2=4 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")

    print("Invalid Test 5 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4.5 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 6 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4 R=-1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 7 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4 C=kx"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")

    print("Invalid Test 8 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 9 for InputRead()")
    Test=original.copy()
    Test[1]="n2=4 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")

    print("Invalid Test 10 for InputRead()")
    Test=original.copy()
    Test[1]="n1=4 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 11 for InputRead()")
    Test=original.copy()
    Test[1]="n1.=3 n2=4 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 11 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2 =4 R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 11.1 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4 yol R=1"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    
    print("Invalid Test 11.2 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4 R=1 k k"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 11.3 for InputRead()")
    Test=original.copy()
    Test[1]="n1=3 n2=4 R=1 hello"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")



    print("\nInvalid Tests for <TERMS> tag:\n")
    print("Invalid Test 12 for InputRead()")
    Test=original.copy()
    Test[20]="VT="
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 13 for InputRead()")
    Test=original.copy()
    Test[21]="RS=abc"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")



    print("Invalid Test 14 for InputRead()")
    Test=original.copy()
    Test[22]="RL=-3"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 15 for InputRead()")
    Test=original.copy()
    Test[23]="Fstart=100sr"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 16 for InputRead()")
    Test=original.copy()
    Test[24]="Fend=-123"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")



    print("Invalid Test 17 for InputRead()")
    Test=original.copy()
    Test[25]="Nfreqs=1.2"
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")

    print("Invalid Test 18 for InputRead()")
    Test=original.copy()
    Test[27]=""#no tag
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")





    print("\nInvalid Tests for <OUTPUT> tag:\n")
    print("Invalid Test 19 for InputRead()")
    Test=original.copy()
    Test[41]=""
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Invalid Test 20 for InputRead()")
    Test=original.copy()
    for i in range(31,41):
        Test[i]=Test[i].upper()
    error, _, _, _, _, _, _, _=InputRead(Test)
    if error:
        print("Passed")
    else:
        print("Failed")


    print("Valid Tests for Node Sorter")

    originalList=[]
    originalList.append(circuitBlock(1, 2,"L",0))
    originalList.append(circuitBlock(2, 0,"R",1))
    originalList.append(circuitBlock(2, 0,"R",2))
    originalList.append(circuitBlock(2, 3, "R",3))
    originalList.append(circuitBlock(3, 4, "R",4))
    originalList.append(circuitBlock(4, 0, "G",5))
    originalList.append(circuitBlock(4, 0, "R",6))
    originalList.append(circuitBlock(4, 0, "R",7))
    originalList.append(circuitBlock(4, 0, "R",8))
    originalList.append(circuitBlock(4, 5, "R",9))
    originalList.append(circuitBlock(5, 0, "C",10))
    originalList.append(circuitBlock(5, 6, "G",11))
    originalList.append(circuitBlock(6, 7, "R",12))
    originalList.append(circuitBlock(7, 8, "R",13))
    originalList.append(circuitBlock(8, 9, "R",14))
    originalList.append(circuitBlock(9, 0, "R",15))
    originalList.append(circuitBlock(9, 0, "R",16))
    originalList.append(circuitBlock(9, 0, "R",17))
    originalList.append(circuitBlock(9, 0, "R",18))
    originalList.append(circuitBlock(10, 11, "R",19))
    

    fail=False
    shuffled=originalList.copy()
    import random
    for i in range(0,20):
        random.shuffle(shuffled)
        _,sort=NodeSorter(shuffled)
        for indx,tst in enumerate(originalList):
            if tst.n1 != sort[indx].n1: # Compares the first node
                                        # to the original list first node
                fail=True
            if tst.n2 != sort[indx].n2: # Compares the second node
                                        # to the original list second node
                fail=True

    if fail==True:
        print("Failed")
    else:
        print("Passed")

    
    shuffled.append(circuitBlock(5, 6, "G",11))
    error,_=NodeSorter(shuffled)
    if error:
        print("Passed")
    else:
        print("Failed")
    shuffled.pop()
    
    shuffled.append(circuitBlock(-3, 3, "C",23))
    error,_=NodeSorter(shuffled)
    if error:
        print("Passed")
    else:
        print("Failed")
    shuffled.pop()

    shuffled.append(circuitBlock(3, 3, "C",23))
    error,_=NodeSorter(shuffled)
    if error:
        print("Passed")
    else:
        print("Failed")
    shuffled.pop()

    shuffled.append(circuitBlock(1, 1, "C",23))
    error,_=NodeSorter(shuffled)
    if error:
        print("Passed")
    else:
        print("Failed")
    shuffled.pop()

    print("\nStarting ValueConvert() Valid Tests")

    if ValueConvert("3k") == 3000:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("3u") == 3e-6:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("1.234567M") == 1234567:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("0p") == 0:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("500") == 500:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("3e-3m") == 3e-6:
        print("Passed")
    else:
        print("Fail")

    
    if ValueConvert("3e-3 m") == 3e-6:
        print("Passed")
    else:
        print("Fail")
    
    if ValueConvert("0.0001 M") == 1000:
        print("Passed")
    else:
        print("Fail")
    
    print("ValueConvert() invalid cases")


    if ValueConvert("10uu") == "error":
        print("Passed")
    else:
        print("Fail")

    if ValueConvert("10uk") == "error":
        print("Passed")
    else:
        print("Fail")


    if ValueConvert("106K") == "error":
        print("Passed")
    else:
        print("Fail")


    if ValueConvert("ten k") == "error":
        print("Passed")
    else:
        print("Fail")


    if ValueConvert("1k.1") == "error":
        print("Passed")
    else:
        print("Fail")
        
    if ValueConvert("10 1k") == "error":
        print("Passed")
    else:
        print("Fail")
    
    
    print("\nStarting ValueConvert() Valid Tests for output side:")
    
    
    if ValueConvert(3,"V","Vin") == (3,0):
        print("Passed")
    else:
        print("Fail")


    if (ValueConvert(1,"dB","Vin")) == (0,0):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(100,"dBu","Vin")) == (160.0,0.0):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(1000,"dBm","Vin")) == (120.0, 0.0):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(100j,"dB","Pin")) == (20.0, 1.5707963267948966):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(25+25j,"dB","Pout")) == (15.484550065040281, 0.7853981633974483):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(25+25j,"kV","Iout")) == (0.025, 0.025):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(20+30j,"dBK","Zin")) == (31.13943352306837, 0.982793723247329):
        print("Passed")
    else:
        print("Fail")
    if (ValueConvert(2500+25j,"mOhms","Zout")) == (2500000.0, 25000.0):
        print("Passed")
    else:
        print("Fail")


   





#Checking File Arguments: This section of the code differentiates each part
# of the command line and uses selective statements to determine whether the user
# wants to perform a fourier analysis or a normal analysis. With that information
# the program saves the relevant information for file naming and saving.

Fourier = False

if len(sys.argv) > 2:
    if str(sys.argv[1]) == "-i" and len(sys.argv) > 4:
        if str(sys.argv[3]) == "-t":
            Fourier = True
            inputName = sys.argv[2]+".net"
            outputName = sys.argv[2]+".csv"
            FourierCoeff = int(sys.argv[4])
    else:
        inputName = sys.argv[1]
        outputName = sys.argv[2]


#Test Mode
if len(sys.argv)>1:
    if str(sys.argv[1]) == "Test":
        import doctest
        doctest.testmod()
        Testing()



#Checks if the input and the output file names have been declared.
#And closes the file if there is no input file


if "inputName" not in locals():
    print("No Input File")
    exit()
if "outputName" not in locals():
    outputName == "test.csv"

#opens the output file
outputfile = open(outputName, "w")
#Reads all the file lines, removes the new lines
# and stores it in the FileLines variable
FileLines = []
filee = open(inputName, "r")
for linex in filee:
    FileLines.append(linex.replace("\n", ""))
filee.close()

# Calls input read to retrive the interpreted input file
# Checks if any error has occurred and returns a blank page if so.
error, unsortedCircuit, Source, Sourcetype, RSval, RLval, Frequencies, OutputOrder = InputRead(FileLines)

if error:
    outputfile.close()
    exit()

#Sorts the unsorted list of circuit blocks and checks for any error occurance again.
error, sortedCircuit = NodeSorter(unsortedCircuit)
if error:
    outputfile.close()
    exit()



# Starts applying the frequencies to the components
# Calculates all values and collates all of the dictionaries in a list
FrequencyMasterMatrix = []
outputValueLine = []
for FrequencyX in Frequencies:

    if Fourier == False: # starts creating the frequency row values
        outputValueLine.append(" "+"{:.3e}".format(FrequencyX)+",")

    # Applies the frequencies to the circuit by individually
    # updating each component with thier frequency and then
    # calculating all output values.
    FirstNode = copy.deepcopy(sortedCircuit[0])
    FirstNode.applyFreq(FrequencyX)
    for indexx in range(1, len(sortedCircuit)):
        try:
            sortedCircuit[indexx].applyFreq(FrequencyX)
            FirstNode.multM(sortedCircuit[indexx])
        except:
            outputfile.close()
            exit()
    FrequencyMasterMatrix.append(FirstNode.calculateAll(RSval, RLval, Source, Sourcetype))




#If in fourier mode: do the fourier transform (and if the amount of frequencies are 2 or more)
if Fourier == True and len(Frequencies)>1:

    #format the titles
    title1a = "{message: >{width}}".format(message="TIME,", width=11)
    line1 = title1a
    title1b = "{message: >{width}}".format(message="Sec,", width=11)
    line2 = title1b

    FourierValues = []
    #Calculate the time difference
    Td = 1/((Frequencies[1]-Frequencies[0]))
    #Create the time axis and format the time column for the output
    time = np.linspace(0, Td, 2**FourierCoeff)
    for timeValue in time:
        outputValueLine.append(" "+"{:.3e}".format(timeValue)+", ")

    #Perfrom the inverse fourier transform on each value
    # going in order of the output order of variables
    for numm in range(0, len(OutputOrder)):
        listOfVals = []
        for numm2 in FrequencyMasterMatrix:
            listOfVals.append(numm2[OutputOrder[numm][0]])
        OutputOrder[numm].append(np.fft.ifft(a=listOfVals, n=2**FourierCoeff))

    #Formatting the output
    #3 stages of formatting:
    #Formatting the titles
    #Formatting the units
    #Formatting the output values
    comma = ","
    for h in OutputOrder:
        if h == OutputOrder[-1]:
            comma = ""
        if "dB" in h[1]:
            title1a = "{message: >{width}}".format(
                message="|"+h[0]+"|"+",", width=12)
            title1b = "{message: >{width}}".format(message="/_"+h[0], width=11)
            line1 = line1+title1a+title1b+comma
            title1a = "{message: >{width}}".format(message=h[1]+",", width=12)
            title1b = "{message: >{width}}".format(message="rads", width=11)
            line2 = line2+title1a+title1b+comma
        else:
            title1a = "{message: >{width}}".format(
                message="Re("+h[0]+"),", width=12)
            title1b = "{message: >{width}}".format(
                message="Im("+h[0]+")", width=11)
            line1 = line1+title1a+title1b+comma
            title1a = "{message: >{width}}".format(message=h[1], width=11)
            line2 = line2+title1a+","+title1a+comma 
        for jh in range(0, 2**FourierCoeff):
            argu1, argu2 = ValueConvert(h[2][jh], h[1], h[0])#Using ValueConvert the program
                                                            # converts the output into the required form
                                                            # whether it requires it to be in dB or have an
                                                            #exponent this function handles it all.
            spacead = " "
            spacead2 = " "
            if argu1 < 0:
                spacead = ""
            if argu2 < 0:
                spacead2 = ""
            outputValueLine[jh] = outputValueLine[jh]+spacead+"{:.3e}".format(
                argu1)+", "+spacead2+"{:.3e}".format(argu2)+comma+" "  # add second one imaginary or phase


else:
    #Formatting the output for a normal output
    #Uses a predefined output value width and puts everything in scientific notation.
    title1a = "{message: >{width}}".format(message="Freq,", width=11)
    line1 = title1a
    title1b = "{message: >{width}}".format(message="Hz,", width=11)
    line2 = title1b

    comma = ","
    for h in OutputOrder:
        if h == OutputOrder[-1]:
            comma = ""
        if "dB" in h[1]:
            title1a = "{message: >{width}}".format(
                message="|"+h[0]+"|"+",", width=12)
            title1b = "{message: >{width}}".format(message="/_"+h[0], width=11)
            line1 = line1+title1a+title1b+comma  # add iaginary + DB
            title1a = "{message: >{width}}".format(message=h[1]+",", width=12)
            title1b = "{message: >{width}}".format(message="rads", width=11)
            line2 = line2+title1a+title1b+comma  # add second
        else:
            title1a = "{message: >{width}}".format(message="Re("+h[0]+"),", width=12)
            title1b = "{message: >{width}}".format(message="Im("+h[0]+")", width=11)
            line1 = line1+title1a+title1b+comma  # add iaginary + DB
            title1a = "{message: >{width}}".format(message=h[1], width=11)
            line2 = line2+title1a+","+title1a+comma  # add second
        for jh in range(0, len(FrequencyMasterMatrix)):
            argu1, argu2 = ValueConvert(FrequencyMasterMatrix[jh][h[0]], h[1], h[0])
            title1a="{:.3e}".format(argu1)+","
            title1a = "{message: >{width}}".format(message=title1a, width=12)
            title1b="{:.3e}".format(argu2)
            title1b = "{message: >{width}}".format(message=title1b, width=11)
            outputValueLine[jh] = outputValueLine[jh]+title1a+title1b+comma # add second one imaginary or phase

#Writing everythin to the output file and appending new lines.

outputfile.writelines(line1+"\n")
outputfile.writelines(line2+"\n")
for wordsad in outputValueLine:
    outputfile.writelines(wordsad+"\n")
outputfile.close()





if __name__ == '__main__':
    import doctest
    doctest.testmod()