# Write a Python program that simulates an ATM withdrawal system. The program should validate the withdrawal request based on multiple conditions before processing it.

# Requirements:
# Create a function atm_withdrawal(withdrawal_amount) that takes withdrawal amount as input

# The current balance in the account is fixed at 5000

# The function should validate:

# Validation 1: Withdrawal amount must be greater than 0

# If invalid: Print "Error: Withdrawal amount must be greater than 0"

# Validation 2: Withdrawal amount must be a multiple of 500

# If invalid: Print "Error: Withdrawal amount must be multiple of 500"

# Validation 3: Account balance must be sufficient for withdrawal

# If invalid: Print "Error: Insufficient balance. Available: {current_balance}"

# If all validations pass:

# Calculate remaining balance

# Print "Withdrawal successful. Amount: {withdrawal_amount}"

# Print "Remaining balance: {remaining_balance}"

# Return True

# If any validation fails:

# Print the specific error message

# Return False

# ------------------------------------------------

def atm_withdrawal(withdrawal_amount):
    current_balance = 5000
    if withdrawal_amount > 0:
        if withdrawal_amount > current_balance:
            print(f"Error: Insufficient balance. Available: {current_balance}")
            return False
        if withdrawal_amount % 500 == 0:
            current_balance -= withdrawal_amount
            print(f"Withdrawal successful.")
            print(f"Remaining balance: {current_balance}")
            return True
        else:
            print("Error: Withdrawal amount must be a multiple of 500.")
            return False
    else:
        print("Error: Withdrawal amount must be greater than 0.")
        return False
    
atm_withdrawal(int(input("Enter the withdrawal amount: ")))