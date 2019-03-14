from main import *

"""
A basic command-line interface with limited functionality.
- accepts input and output and outputs the compiler code
"""

def main():
	gen = CompilerCodeGenerator()
	
	print("Hello! You can give me a command-style input and a template-style output" +
	      " and I will generate a compiler for you."
	print("Please enter a command-style input")
	input = sys.stdin.readline().trim()
	print("Please enter a template-style output")
	ouput = sys.stdin.read()
	
	gen.fit([input], [output])
	print("Here is the compiler code in python"
	print(gen.code)
	
	print("Test it out! Try typing and input and seeing if the output is correct."
	while True:
	    print("Please enter a command-style input")
		input = sys.stdin.read()
		print("Here is the predicted output by the compiler.")
		gen.transform(input)
	
	
	
if __name__ == "__main__":
    main()