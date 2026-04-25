# Write a Python program that calculates the total restaurant bill including service charge, tax, and tip.

# Requirements:
# Create a function calculate_restaurant_bill(meal_cost) that takes meal cost as input

# The tip is fixed at 5%

# Calculate the following in order:

# Service Charge: 10% of meal cost

# Amount after Service: Meal cost + Service charge

# Tax: 5% of amount after service

# Tip: 5% of amount after service

# Total Bill: Amount after service + Tax + Tip

# Output Format:
# Meal Cost: {meal_cost}

# Service Charge (10%): {service_charge}

# Amount after Service: {amount_after_service}

# Tax (5%): {tax}

# Tip (5%): {tip_amount}

# Total Bill: {total}


# Input:
# Accept meal cost from user using input() and convert to float

# Test Cases:
# Test Case 1:

# Input: 500

# Expected Output:

# Meal Cost: 500.0

# Service Charge (10%): 50.0

# Amount after Service: 550.0

# Tax (5%): 27.5

# Tip (5%): 27.5

# Total Bill: 605.0

# Return: 605.0

#-----------------------------------------------------------

def calculate_restaurant_bill(meal_cost):
    serviceCharge = 0.1 * meal_cost
    amount_after_service_charge = meal_cost + serviceCharge
    tax = 0.05 * amount_after_service_charge
    tip=0.05 * amount_after_service_charge
    total_bill = amount_after_service_charge + tax + tip
    if meal_cost < 0:
        print("Error: Meal cost cannot be negative.")
        return False
    else:
        print(f"Meal Cost: {meal_cost}")
        print(f"Service Charge (10%): {serviceCharge}")
        print(f"Tax (5%): {tax}")
        print(f"Tip (5%): {tip}")
        print(f"Total Bill: {total_bill}")
        return True

calculate_restaurant_bill(float(input("Enter the meal cost: "))) 