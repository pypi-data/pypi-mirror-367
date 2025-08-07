import argparse
import secrets
import string
import sys
import pyperclip


def generate_password(length: int, complexity: int, base_word: str = "") -> str:
    """ 
    Generates a password based on the provided length, complexity, and base word.

    Parameters:
    - length (int): The desired length of the password.
    - complexity (int): The desired complexity level (1, 2, 3, or 4).
    - base_word (str): A word that will be integrated into the generated password.

    Returns:
    - A string containing the generated password.
    """
    if not 1 <= complexity <= 4:
        raise ValueError("Complexity must be 1, 2, 3, or 4.")
    
    if length < len(base_word):
        raise ValueError("Password length cannot be smaller than base word.")

    # Define characters according to the complexity
    if complexity == 1:
        characters = string.ascii_lowercase
    elif complexity == 2:
        characters = string.ascii_letters + string.digits
    elif complexity == 3:
        characters = string.ascii_letters + string.digits + string.punctuation
    elif complexity == 4:
        # Maximum complexity guarantees at least one of each type
        password = [
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.digits),
            secrets.choice(string.punctuation)
        ]
        characters = string.ascii_letters + string.digits + string.punctuation
    else:
        password = []

    # Generate the remaining characters, considering the length of the base word
    remaining_length = max(length - len(base_word), 0)
    extra_password = [secrets.choice(characters) for _ in range(remaining_length)]
    password += extra_password + list(base_word)
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password[:length])


def display_menu():
    """ 
    Displays the interactive menu for the user to choose the password length, complexity, and base word.
    """
    print("Welcome to the Interactive Password Generator!")
    while True:
        try:
            length = int(input("Enter password length: "))
            if length <= 0:
                print("Length must be greater than 0.")
                continue

            print("\nComplexity levels:")
            print("1 - Lowercase letters")
            print("2 - Letters and digits")
            print("3 - Letters, digits, symbols")
            print("4 - Max complexity (guarantees all types)")

            complexity = int(input("Choose complexity (1-4): "))
            base_word = input("Optional base word: ").strip()

            password = generate_password(length, complexity, base_word)
            print(f"\nYour password: {password}\n")
            
            copy_choice = input("Copy to clipboard? (y/n): ").lower()
            if copy_choice == 'y':
                pyperclip.copy(password)
                print("Password copied to clipboard!")

            again = input("Generate another? (y/n): ").lower()
            if again != 'y':
                print("Goodbye!")
                break

        except ValueError as e:
            print(f"Error: {e}")


def cli():
    parser = argparse.ArgumentParser(
        description="Generate secure passwords with optional base word and complexity."
    )
    parser.add_argument("-l", "--length", type=int, help="Length of the password")
    parser.add_argument("-c", "--complexity", type=int, choices=[1, 2, 3, 4],
                        help="Complexity level: 1-4")
    parser.add_argument("-b", "--base", type=str, default="", help="Base word to include")
    parser.add_argument("--copy", action="store_true", help="Copy password to clipboard")
    
    args = parser.parse_args()

    if args.length and args.complexity:
        try:
            password = generate_password(args.length, args.complexity, args.base)
            print(password)
            if args.copy:
                pyperclip.copy(password)
                print("Password copied to clipboard!")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        display_menu()


if __name__ == "__main__":
    cli()