# Takes file name as an input to the user
inputFileName = input("Enter a file name : ")

# Validation to check if the file exists, if it doesn't
# It defaults to file.txt
try:
    textFile = open(inputFileName, "r")
except:
    print("Invalid file name, defaulting to file.txt")
    textFile = open("file.txt","r")

# Reads all the lines in the text file and splits it into
# an array by line
fileLines=textFile.read().splitlines()
textFile.close()

# initialises all the variables.
vowelCount=0
charCount=0
spaceCount=0

# Goes through every line and every character
# to check if any of the characters are vowels or
# spaces and to count the total
for line in fileLines:
    for char in line:
        charCount+=1
        if char == " ":
            spaceCount+=1
        if char.lower() in ["a","e","i","o","u"]:
            vowelCount+=1

# Formats the output to print all the tallied values
print("Number of Spaces (' ') : ",spaceCount)
print("Number of Vowels (a, e, i, o or u') : ", vowelCount)

# Ensures there is no zero division error when calculating
# the percentage.
if charCount!=0:
    percentage=round(((vowelCount+spaceCount)/charCount)*100,1)
    print("Percentage of vowels and spaces : ",percentage)

