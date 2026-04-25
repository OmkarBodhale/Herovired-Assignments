# Write a Python program that validates a user's login credentials based on specific security requirements.

# Requirements:
# Create a function validate_login(username, password) that takes username and password as input

# The function should validate:

# Validation 1: Username length must be at least 5 characters

# If invalid: Print "Error: Username must be at least 5 characters"

# Return False

# Validation 2: Password length must be at least 8 characters

# If invalid: Print "Error: Password must be at least 8 characters"

# Return False

# Validation 3: Password must contain at least one digit (0-9)

# Use a loop to check each character

# Use char.isdigit() method to check if character is a digit

# If invalid: Print "Error: Password must contain at least one digit"

# Return False

# If all validations pass:

# Print "Login successful"

# Return True

# Validations should be checked in order. Stop at first failure.

# Input:
# Accept username from user using input()

# Accept password from user using input()

# Test Cases:
# Test Case 1:

# Input: 

# username: john_doe

# password: Pass1234


# Expected Output:

# Login successful

# Return: True

# ----------------------------------------------------------------

def validate_login(username, password):
    if len(username) < 5:
        print("Error: Username must be at least 5 characters")
        return False
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return False
        
    # Check for at least one digit using a simple loop
    has_digit = False
    for char in password:
        if char.isdigit():
            has_digit = True
            break
    
    if not has_digit:
        print("Error: Password must contain at least one digit")
        return False
    print("Login successful")
    return True

validate_login(input("Enter username: "), input("Enter password: "))