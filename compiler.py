def main():
    import sys
	print("Please enter a command-style input")
	input = sys.stdin.read()
	print(translate(input))


if __name__ == "__main__":
    main()