import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def annuity_loan_calculator_df(loan_amount, interest_rate, repayment_period):
    monthly_interest = interest_rate / 100 / 12
    total_payments = repayment_period * 12
    monthly_payment = loan_amount * (monthly_interest / (1 - (1 + monthly_interest) ** -total_payments))

    remaining_debt = loan_amount
    cumulative_interest = 0
    data = []

    for month in range(1, total_payments + 1):
        interest = remaining_debt * monthly_interest
        principal_payment = monthly_payment - interest
        remaining_debt -= principal_payment
        cumulative_interest += interest

        data.append({
            "Month": month,
            "Principal Payment": round(principal_payment, 2),
            "Interest": round(interest, 2),
            "Total Paid": round(monthly_payment, 2),
            "Cumulative Interest": round(cumulative_interest, 2),
            "Remaining Debt": round(remaining_debt, 2)
        })

    return pd.DataFrame(data)

st.title("Boliglånkalkulator / Mortgage Loan Calculator")

col1, col2 = st.columns([1, 2])

with col1:
    loan_amount = st.number_input("Lånebeløp (kroner) / Loan amount (NOK):", min_value=0.0, value=2500000.0, step=10000.0)
    interest_rate = st.number_input("Årlig rente (%) / Annual interest rate (%):", min_value=0.0, value=3.5, step=0.1)
    repayment_period = st.number_input("Nedbetalingstid (år) / Repayment period (years):", min_value=1, max_value=50, value=25, step=1)

df = annuity_loan_calculator_df(loan_amount, interest_rate, repayment_period)

# Interactive Plotly Line Graph
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Interest'], mode='lines', name='Akkumulert rente / Cumulative Interest'))
fig.add_trace(go.Scatter(x=df['Month'], y=df['Remaining Debt'], mode='lines', name='Restgjeld / Remaining Debt'))
fig.update_layout(title='Utvikling av akkumulert rente og restgjeld over tid / Cumulative Interest and Debt Development Over Time',
                  xaxis_title='Måned / Month',
                  yaxis_title='Beløp (kroner) / Amount (NOK)',
                  hovermode="x unified",
                  legend=dict(x=0.05, y=0.95))

with col2:
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Fordeling av renter og avdrag per måned / Monthly Interest and Principal Breakdown")

# Interactive Plotly Histogram
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=df['Month'], y=df['Interest'], name='Renter / Interest'))
fig2.add_trace(go.Bar(x=df['Month'], y=df['Principal Payment'], name='Avdrag / Principal'))

fig2.update_layout(barmode='stack',
                   title='Fordeling av renter og avdrag måned for måned / Interest and Principal Distribution Month-by-Month',
                   xaxis_title='Måned / Month',
                   yaxis_title='Beløp (kroner) / Amount (NOK)',
                   hovermode="x unified",
                   legend=dict(x=0.05, y=0.95))

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Betalingsplan / Payment Schedule")
st.dataframe(df)

#csv = df.to_csv(index=False).encode('utf-8')
#st.download_button(
#    label="Last ned betalingsplan som CSV / Download payment schedule as CSV",
#    data=csv,
#    file_name='loan_schedule.csv',
#    mime='text/csv',
#)
