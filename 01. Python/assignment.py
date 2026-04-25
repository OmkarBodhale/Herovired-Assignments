def atm_withdrawal(withdrawal_amount):
    current_balance = 5000
    if withdrawal_amount > 0:
        if withdrawal_amount > current_balance:
            print(f"Error: Insufficient balance. Available: {current_balance}")
            return False
        if withdrawal_amount % 500 == 0:
            current_balance -= withdrawal_amount
            print(f"Withdrawal successful. Remaining balance: {current_balance}")
            return True
        else:
            print("Error: Withdrawal amount must be a multiple of 500.")
            return False

#atm_withdrawal(int(input("Enter the withdrawal amount: ")))

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


