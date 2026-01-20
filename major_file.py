from registration import register_user
from login import login_user
from dashboard import dashboard


print("----------------------- Welcome to Iffy's Money Bank -----------------------------")
print("Your money is safe with us, making banking easy and secure!")

while True:
    print("\n1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Please select an option (1-3): ").strip()

    if choice == '1':
        register_user()

    elif choice == '2':
        user = login_user()   # capture logged-in user

        if user:              # only proceed if login was successful
            dashboard(user)

    elif choice == '3':
        print("Thank you for using Iffy's Money Bank. Goodbye!")
        print("Say No to high fees, Yes to smart banking!")
        break

    else:
        print("Invalid option. Please try again.")
