# pseudocode2code



An algorithm which can help with translating pseudocode to code



# How the Generated Compiler Works


- takes in a 1 line input of command-style text

  - eg. "read int as N"

- splits the line of text by spaces into tokens

  - eg. ["read", "int", "as", "N"]
- treats the first element of that split as the command name

  - eg. "read"

- from the test case it saw before, it can distinguish between multiple cases of the same command; also, for each case, it knows which indices have variables and how they map to the output



# How the Compiler Code Generator Works


- reads and splits 1 line of input as mentioned above

- labels each element as a "variable" or "constant"

  - eg. ["constant", "constant", "constant", "variable"]

  - a "variable" is a token whose value is copy-and-pasted to the output

  - a "constant" is a word that is the same any time that specific command is called; it has no relation to the output and merely serves as a word to make the pseudocode more natural English and help the compiler distinguish between different use cases of the same command

- a token is recognized as a variable if one of the following is true:

  - it is composed of only capital letters

  - it is a string, float, or integer
- assumptions:

  - each variable name is not contained in another (ie "read AB A" can lead to ambiguity errors in terms of how it maps to the output)

  - no strings contain spaces (it won't ignore those spaces during the split)
  - the output does not contain substrings matching the input variables which do not correspond to the input variables
- other complicated logic



# To Do


- [x] README

- [x] basic code

- [ ] test.py

  - list of test cases, gen compiler and check that the input is mapped correctly to the output

- [ ] try running and debug

- [ ] .transform method



# Future Features



- handle missing variables by using the previous variable

- include indenting to be used for if blocks

- features based on properties of the token (ie is_pdf_path)

- do not split by spaces within a string

- test cases from the sheet of paper