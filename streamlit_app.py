import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy_financial as npf


@st.cache_data
def annuity_loan_calculator_df(loan_amount, nominal_interest_rate, repayment_period):
    monthly_interest = nominal_interest_rate / 100 / 12
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
            "Year": (month - 1) // 12 + 1,
            "Principal Payment": round(principal_payment, 2),
            "Interest": round(interest, 2),
            "Total Paid": round(monthly_payment, 2),
            "Cumulative Interest": round(cumulative_interest, 2),
            "Remaining Debt": round(max(remaining_debt, 0), 2)
        })

    return pd.DataFrame(data)


def simulate_repayment_strategies(loan_amount, interest_rate, repayment_period, extra_payment, annual_years_reduction):
    remaining_debt = loan_amount
    cumulative_interest = 0
    year = 0
    strategy_data = []

    while remaining_debt > 0 and repayment_period > 0:
        year += 1

        annual_df = annuity_loan_calculator_df(remaining_debt, interest_rate, repayment_period)
        yearly_interest = annual_df['Interest'].iloc[:12].sum()
        yearly_principal = annual_df['Principal Payment'].iloc[:12].sum()
        monthly_payment = annual_df['Total Paid'].iloc[0]
        yearly_regular_payment = yearly_interest + yearly_principal

        remaining_debt -= (yearly_principal + extra_payment)
        cumulative_interest += yearly_interest

        repayment_period = max(1, repayment_period - annual_years_reduction)

        strategy_data.append({
            'Year': year,
            'Monthly Payment': round(monthly_payment, 2),
            'Yearly Interest': round(yearly_interest, 2),
            'Regular Principal Payment': round(yearly_principal, 2),
            'Extra Payment': round(extra_payment, 2),
            'Total Yearly Payment': round(yearly_regular_payment + extra_payment, 2),
            'Remaining Debt': round(max(remaining_debt, 0), 2),
            'Cumulative Interest': round(cumulative_interest, 2),
            'Remaining Years': repayment_period
        })

        if remaining_debt <= 0:
            break

    return pd.DataFrame(strategy_data)


st.title("Boliglånkalkulator / Mortgage Loan Calculator")

col1, col2 = st.columns([1, 2])

with col1:
    loan_amount = st.number_input("Lånebeløp (kroner) / Loan amount (NOK):", min_value=0.0, value=2500000.0, step=10000.0)
    nominal_interest_rate = st.number_input("Nominell rente (%) / Nominal interest rate (%):", min_value=0.0, value=3.5, step=0.1)
    repayment_period = st.number_input("Nedbetalingstid (år) / Repayment period (years):", min_value=1, max_value=50, value=25, step=1)
    extra_payment = st.number_input("Årlig ekstra betaling (kroner) / Annual extra payment (NOK):", min_value=0.0, value=50000.0, step=5000.0)
    annual_years_reduction = st.number_input("Årlig reduksjon i nedbetalingstid (år) / Annual repayment period reduction (years):", min_value=0, max_value=repayment_period-1, value=1, step=1)

# Automatically trigger calculations
df = annuity_loan_calculator_df(loan_amount, nominal_interest_rate, repayment_period)
strategy_df = simulate_repayment_strategies(loan_amount, nominal_interest_rate, repayment_period, extra_payment, annual_years_reduction)

with col2:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Interest'], mode='lines', name='Akkumulert rente'))
    fig1.add_trace(go.Scatter(x=df['Month'], y=df['Remaining Debt'], mode='lines', name='Restgjeld'))
    fig1.update_layout(title='Akkumulert rente og restgjeld',
                      xaxis_title='Måned', yaxis_title='Beløp (NOK)', hovermode="x unified",
                      legend=dict(x=0.05, y=0.95))
    st.plotly_chart(fig1, use_container_width=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Interest'], mode='lines', name='Uten ekstra betaling'))
fig2.add_trace(go.Scatter(x=strategy_df['Year']*12, y=strategy_df['Cumulative Interest'], mode='lines', name='Med ekstra betaling'))
fig2.update_layout(title='Sammenligning av akkumulert rente',
                  xaxis_title='Måned', yaxis_title='Beløp (NOK)', hovermode="x unified",
                  legend=dict(x=0.05, y=0.95))
st.plotly_chart(fig2, use_container_width=True)

# Aggregate per year based on strategy_df (not df)
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=strategy_df['Year'], y=strategy_df['Yearly Interest'], name='Renter'))
fig3.add_trace(go.Bar(x=strategy_df['Year'], y=strategy_df['Regular Principal Payment'], name='Avdrag'))
fig3.update_layout(barmode='stack', title='Årlig fordeling renter og avdrag (strategi)',
                   xaxis_title='År', yaxis_title='Beløp (NOK)', hovermode="x unified",
                   legend=dict(x=0.05, y=0.95))
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Detaljert betalingsplan")
st.dataframe(strategy_df)
