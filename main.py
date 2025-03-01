import matplotlib.pyplot as plt
import streamlit as st

class Category:
    def __init__(self, category, ledger=None):
        self.ledger = ledger if ledger is not None else []
        self.category = category

    def __str__(self):
        title = self.category.center(30, "*")  

        items = ""
        for entry in self.ledger:
            description = entry["description"][:23]  
            amount = f"{entry['amount']:7.2f}"  
            items += f"{description:<23}{amount}\n"  

        # Total balance
        total = f"Total: {self.get_balance():.2f}"

        # Return the formatted string
        return f"{title}\n{items}{total}"
    
    def deposit(self, amount, description=''):
        self.ledger.append({'amount': amount, 'description': description})
        
        return self.ledger
    
    def withdraw(self, amount, description=''):
        if self.get_balance() >= amount:
            self.ledger.append({"amount": -amount, "description": description})
            return True
        return False
        
    def get_balance(self):
        return sum(entry['amount'] for entry in self.ledger)

    def transfer(self, amount, category):
        if self.get_balance() >= amount:
            self.withdraw(amount, f"Transfer to {category.category}")
            category.deposit(amount, f"Transfer from {self.category}")
            return True
        return False

    def check_funds(self, amount):
        if self.get_balance() < amount:
            return False
        return True
        

def create_spend_chart(categories):
    # Get category names and spending amounts
    category_names = [category.category for category in categories]
    spent_amounts = [
        sum(-entry["amount"] for entry in category.ledger if entry["amount"] < 0)
        for category in categories
    ]

    # Calculate total spending
    total_spent = sum(spent_amounts)
    if total_spent == 0:
        return None  # Avoid division by zero

    # Calculate percentages
    spending_percentages = [(amount / total_spent) * 100 for amount in spent_amounts]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(7, 5))

    # Create horizontal bars
    ax.barh(category_names, spending_percentages, color="skyblue")

    # Labels and formatting
    ax.set_xlabel("Percentage Spent")
    ax.set_title("Percentage Spent by Category")
    ax.invert_yaxis()  # Highest percentage at the top

    # Add percentage labels on bars
    for index, value in enumerate(spending_percentages):
        ax.text(value + 1, index, f"{value:.1f}%", va='center')

    return fig  # Return the figure to be displayed in Streamlit


categories = {}

# Ensure categories persist across interactions
if "categories" not in st.session_state:
    st.session_state.categories = {}

st.set_page_config(page_title="Budget Tracker", page_icon="💰", layout="wide")

st.title("Welcome to the Budget Tracker App!")

st.divider()


# Input for new category
category_name = st.text_input("Enter category name:")
if st.button("Create Category", use_container_width=True):
    if category_name:
        if category_name not in st.session_state.categories:
            st.session_state.categories[category_name] = Category(category_name)
            st.success(f"Category '{category_name}' created successfully!")
        else:
            st.warning("Category already exists!")
    else:
        st.error("Please enter a category name.")

st.divider()

# Dropdown to select an existing category
if st.session_state.categories:
    selected_category = st.selectbox("Select a category:", list(st.session_state.categories.keys()))
    current_category = st.session_state.categories[selected_category]

    # Deposit Section
    st.divider()
    st.subheader("📥 Deposit Money")

    col1, col2 = st.columns(2)

    with col1:
        deposit_amount = st.number_input("Deposit Amount:", min_value=0.0, step=10.0)
    with col2:
        deposit_description = st.text_input("Deposit Description", key="dep_desc")

    # Full-width button for deposit
    if st.button("Deposit", use_container_width=True):
        if deposit_amount > 0:
            current_category.deposit(deposit_amount, deposit_description)
            st.success(f"Deposited {deposit_amount} to {selected_category}")


    # Withdraw Section
    st.divider()
    st.subheader("📤 Withdraw Money")

    col3, col4 = st.columns(2)

    with col3:
        withdraw_amount = st.number_input("Withdraw Amount:", min_value=0.0, step=10.0)
    with col4:
        withdraw_description = st.text_input("Withdraw Description", key="with_desc")
        
    if st.button("Withdraw", use_container_width=True):
        if withdraw_amount > 0 and current_category.withdraw(withdraw_amount, withdraw_description):
            st.success(f"Withdrew {withdraw_amount} from {selected_category}")
        else:
            st.error("Insufficient funds!")

    st.divider()
    # 3️⃣ Transfer Money Between Categories
    st.subheader("💸 Transfer Money")

    # Select category to transfer to
    transfer_to_name = st.selectbox("Transfer to:", list(st.session_state.categories.keys()))

    # Get the actual Category instance
    transfer_to_category = st.session_state.categories[transfer_to_name]

    # Input for transfer amount
    transfer_amount = st.number_input("Transfer Amount:", min_value=0.0, step=10.0)

    # Transfer button
    if st.button("Transfer", use_container_width=True):
        if transfer_amount > 0 and current_category.transfer(transfer_amount, transfer_to_category):
            st.success(f"Transferred {transfer_amount} from {selected_category} to {transfer_to_name}")
        else:
            st.error("Insufficient funds for transfer!")


    st.divider()
    # 4️⃣ View Ledger
    st.subheader(f"Transaction History of {selected_category}")
    st.write(current_category)

    st.divider()
    # 5️⃣ Show Budget Summary
    total_balance = sum(category.get_balance() for category in st.session_state.categories.values())
    st.subheader("Total Balance Across All Categories")
    st.write(f"💰 Total Balance: {total_balance}")


st.divider()
# 6️⃣ Spending Chart Section
st.subheader("📊 Spending Distribution")

if st.session_state.categories:
    fig = create_spend_chart(list(st.session_state.categories.values()))
    if fig:
        st.pyplot(fig)  # Display the chart
    else:
        st.warning("No spending data available.")
else:
    st.warning("No categories found. Please add some categories first!")

