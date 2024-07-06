from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def users():
    num_users = int(request.form['num_users'])
    return render_template('users.html', num_users=num_users)

@app.route('/bill', methods=['POST'])
def bill():
    num_users = int(request.form['num_users'])
    names = [request.form[f'name_{i}'] for i in range(num_users)]
    return render_template('bill.html', num_users=num_users, names=names)

@app.route('/payments', methods=['POST'])
def payments():
    num_users = int(request.form['num_users'])
    total_bill = float(request.form['total_bill'])
    names = request.form.getlist('names')
    avg_amount = total_bill / num_users
    return render_template('payments.html', num_users=num_users, names=names, avg_amount=avg_amount, total_bill=total_bill)

@app.route('/split', methods=['POST'])
def split():
    num_users = int(request.form['num_users'])
    names = request.form.getlist('names')
    amounts = [float(request.form[f'amount_{i}']) for i in range(num_users)]
    total_bill = float(request.form['total_bill'])
    total_paid = sum(amounts)

    if total_paid < total_bill:
        return render_template('error.html', message=f"The total amount paid (${total_paid:.2f}) is less than the bill amount (${total_bill:.2f}). Please check the amounts.")

    avg_amount = total_bill / num_users
    balances = {names[i]: amounts[i] - avg_amount for i in range(num_users)}

    messages = {}
    for name, balance in balances.items():
        if balance == 0:
            messages[name] = "has paid the exact amount."
        elif balance > 0:
            messages[name] = f"has overpaid by ${balance:.2f}."
        else:
            messages[name] = f"owes ${-balance:.2f}."

    results = calculate_debts(balances)

    return render_template('result.html', results=results, balances=balances, messages=messages)

def calculate_debts(balances):
    debtors = {k: v for k, v in balances.items() if v < 0}
    creditors = {k: v for k, v in balances.items() if v > 0}
    
    transactions = []
    while debtors and creditors:
        debtor = next(iter(debtors))
        creditor = next(iter(creditors))
        
        debt_amount = min(-debtors[debtor], creditors[creditor])
        
        transactions.append((debtor, creditor, debt_amount))
        
        debtors[debtor] += debt_amount
        creditors[creditor] -= debt_amount
        
        if debtors[debtor] == 0:
            del debtors[debtor]
        if creditors[creditor] == 0:
            del creditors[creditor]

    return transactions

if __name__ == '__main__':
    app.run(debug=True)
