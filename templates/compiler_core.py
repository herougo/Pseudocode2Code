def main():
    import sys
    #print("Please enter a command-style input")
    input_path = sys.argv[1]
    with open(input_path, 'r') as f:
        input = str(f.read())
    for line in input.split('\n'):
        print(translate(line))

if __name__ == '__main__':
    main()