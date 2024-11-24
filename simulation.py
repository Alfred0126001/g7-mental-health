
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Simulation parameters

# Initial mental health state distribution
healthy_population = 800000  # Number of healthy individuals
mild_cases = 20000           # Number of mild cases
moderate_cases = 5000        # Number of moderate cases
severe_cases = 3000          # Number of severe cases

# Scenario selection
scenario = 'peace'  # Choose between 'peace' (stable) or 'crisis' (crisis)

# Initial resource allocation coefficients (ensure the sum is 1.0)
allocation_mild = 0.7        # Resource allocation ratio for mild cases
allocation_moderate = 0.2    # Resource allocation ratio for moderate cases
allocation_severe = 0.1      # Resource allocation ratio for severe cases

# Total number of mental health professionals
total_doctors = 1000  # Total number of doctors

# Service rate per doctor (number of patients cured daily)
service_rate_mild = 10       # Mild cases cured per doctor per day
service_rate_moderate = 5    # Moderate cases cured per doctor per day
service_rate_severe = 1      # Severe cases cured per doctor per day

# Simulation time (in days)
SIM_TIME = 365  # Simulate for one year

# Adjust the transition matrix based on the scenario
if scenario == 'peace':
    T = np.array([
        [0.995, 0.005, 0.00, 0.00],  # Healthy individuals transition probabilities
        [0.1, 0.7, 0.2, 0.00],       # Mild cases transition probabilities
        [0.0, 0.1, 0.7, 0.2],        # Moderate cases transition probabilities
        [0.00, 0.00, 0.0, 1.00]      # Severe cases transition probabilities
    ])
elif scenario == 'crisis':
    T = np.array([
        [0.99, 0.01, 0.00, 0.00],  # Healthy individuals transition probabilities
        [0.10, 0.75, 0.15, 0.0],   # Mild cases transition probabilities
        [0.0, 0.10, 0.85, 0.05],   # Moderate cases transition probabilities
        [0.0, 0.0, 0.05, 0.95]     # Severe cases transition probabilities
    ])

# Initialize the state vector S = [Healthy, Mild, Moderate, Severe]
S = np.array([healthy_population, mild_cases, moderate_cases, severe_cases], dtype=float)

# Compute the initial doctor allocation
doctors_mild = int(total_doctors * allocation_mild)           # Doctors allocated to mild cases
doctors_moderate = int(total_doctors * allocation_moderate)   # Doctors allocated to moderate cases
doctors_severe = total_doctors - doctors_mild - doctors_moderate  # Doctors allocated to severe cases

# Compute the service rates for each group
mu_mild = doctors_mild * service_rate_mild           # Daily service capacity for mild cases
mu_moderate = doctors_moderate * service_rate_moderate   # Daily service capacity for moderate cases
mu_severe = doctors_severe * service_rate_severe       # Daily service capacity for severe cases

# Initialize lists for resource allocation ratios
allocation_mild_list = []
allocation_moderate_list = []
allocation_severe_list = []

# Initialize waiting queues for each group
queue_mild = 10000
queue_moderate = 5000
queue_severe = 1000

# Initialize lists to record queue lengths
queue_lengths_mild = []
queue_lengths_moderate = []
queue_lengths_severe = []

# Initialize lists to track the number of active cases
active_mild = [mild_cases]
active_moderate = [moderate_cases]
active_severe = [severe_cases]

# Initialize lists to record daily net new cases
daily_net_new_mild = []
daily_net_new_moderate = []
daily_net_new_severe = []

# Initialize lists to record cumulative cured cases
cumulative_cured_mild = [0]
cumulative_cured_moderate = [0]
cumulative_cured_severe = [0]

# Simulation loop
for day in range(SIM_TIME):
    # Update mental health states (one step in the Markov chain)
    S = np.dot(S, T)
    
    # Ensure no negative values in S
    S = np.maximum(S, 0)
    
    # Compute the total population
    total_population = S.sum()

    if total_population == 0:
        print(f"Total population is zero on day {day}.")
        new_mild = 0
        new_moderate = 0
        new_severe = 0
    else:
        # Compute proportions for each state
        fraction_mild = S[1] / total_population       # Proportion of mild cases
        fraction_moderate = S[2] / total_population   # Proportion of moderate cases
        fraction_severe = S[3] / total_population     # Proportion of severe cases

        # Compute new cases for each group
        new_mild = S[0] * (T[0,1] + T[0,2] + T[0,3])  # Healthy transitioning to mild/moderate/severe
        new_moderate = S[1] * (T[1,2] + T[1,3])       # Mild transitioning to moderate/severe
        new_severe = S[2] * T[2,3]                   # Moderate transitioning to severe

    # Ensure arrival rates are non-negative
    lambda_mild = max(new_mild, 0)
    lambda_moderate = max(new_moderate, 0)
    lambda_severe = max(new_severe, 0)

    try:
        num_arrivals_mild = np.random.poisson(lambda_mild)
        num_arrivals_moderate = np.random.poisson(lambda_moderate)
        num_arrivals_severe = np.random.poisson(lambda_severe)
    except ValueError as e:
        print(f"Day {day}, failed to generate Poisson distribution: {e}")
        num_arrivals_mild = 0
        num_arrivals_moderate = 0
        num_arrivals_severe = 0

    # Update waiting queues
    queue_mild += num_arrivals_mild
    queue_moderate += num_arrivals_moderate
    queue_severe += num_arrivals_severe

    # Check if it's the weekend (assume day 0 is Monday)
    if day % 7 in [5, 6]:  # 5 and 6 correspond to Saturday and Sunday
        patients_served_mild = 0
        patients_served_moderate = 0
        patients_served_severe = 0
    else:
        # Compute patients served per group based on service capacity
        patients_served_mild = min(queue_mild, mu_mild)
        patients_served_moderate = min(queue_moderate, mu_moderate)
        patients_served_severe = min(queue_severe, mu_severe)

    # Update queue lengths
    queue_mild -= patients_served_mild
    queue_moderate -= patients_served_moderate
    queue_severe -= patients_served_severe

    # Compute daily net new cases (arrivals - treated)
    net_new_mild = num_arrivals_mild - patients_served_mild
    net_new_moderate = num_arrivals_moderate - patients_served_moderate
    net_new_severe = num_arrivals_severe - patients_served_severe

    # Record daily net new cases
    daily_net_new_mild.append(net_new_mild)
    daily_net_new_moderate.append(net_new_moderate)
    daily_net_new_severe.append(net_new_severe)

    # Update treated and recovered counts
    recovered_mild = patients_served_mild
    S[0] += recovered_mild      
    S[1] -= recovered_mild      

    recovered_moderate = patients_served_moderate
    S[0] += recovered_moderate  
    S[2] -= recovered_moderate  

    recovered_severe = patients_served_severe
    S[0] += recovered_severe    
    S[3] -= recovered_severe    

    cumulative_cured_mild.append(cumulative_cured_mild[-1] + recovered_mild)
    cumulative_cured_moderate.append(cumulative_cured_moderate[-1] + recovered_moderate)
    cumulative_cured_severe.append(cumulative_cured_severe[-1] + recovered_severe)

    queue_lengths_mild.append(queue_mild)
    queue_lengths_moderate.append(queue_moderate)
    queue_lengths_severe.append(queue_severe)

    allocation_mild_list.append(allocation_mild)
    allocation_moderate_list.append(allocation_moderate)
    allocation_severe_list.append(allocation_severe)

    active_mild.append(S[1])
    active_moderate.append(S[2])
    active_severe.append(S[3])

    if day % 30 == 0 and day > 0:
        avg_wait_mild = np.mean(queue_lengths_mild[-30:]) / mu_mild if mu_mild > 0 else 0
        avg_wait_moderate = np.mean(queue_lengths_moderate[-30:]) / mu_moderate if mu_moderate > 0 else 0
        avg_wait_severe = np.mean(queue_lengths_severe[-30:]) / mu_severe if mu_severe > 0 else 0

        adjust = True
        delta = 0.05  

        if avg_wait_severe > 7:
            allocation_severe = min(allocation_severe + delta, 1.0)
            allocation_mild = max(allocation_mild - delta / 2, 0)
            allocation_moderate = max(allocation_moderate - delta / 2, 0)
            adjust = True

        if avg_wait_moderate > 14:
            allocation_moderate = min(allocation_moderate + delta, 1.0)
            allocation_mild = max(allocation_mild - delta / 2, 0)
            allocation_severe = max(allocation_severe - delta / 2, 0)
            adjust = True

        if avg_wait_mild > 20:
            allocation_mild = min(allocation_mild + delta, 1.0)
            allocation_moderate = max(allocation_moderate - delta / 2, 0)
            allocation_severe = max(allocation_severe - delta / 2, 0)
            adjust = True

        if adjust:
            doctors_mild = int(total_doctors * allocation_mild)
            doctors_moderate = int(total_doctors * allocation_moderate)
            doctors_severe = total_doctors - doctors_mild - doctors_moderate

            mu_mild = doctors_mild * service_rate_mild
            mu_moderate = doctors_moderate * service_rate_moderate
            mu_severe = doctors_severe * service_rate_severe

severe_cases_after_one_year = S[3]
mild_cases_after_one_year = S[1]
moderate_cases_after_one_year = S[2]

avg_waiting_time_mild = np.mean(queue_lengths_mild) / mu_mild if mu_mild > 0 else 0
avg_waiting_time_moderate = np.mean(queue_lengths_moderate) / mu_moderate if mu_moderate > 0 else 0
avg_waiting_time_severe = np.mean(queue_lengths_severe) / mu_severe if mu_severe > 0 else 0

avg_queue_length_mild = np.mean(queue_lengths_mild)
avg_queue_length_moderate = np.mean(queue_lengths_moderate)
avg_queue_length_severe = np.mean(queue_lengths_severe)

plt.figure(figsize=(18, 6))
plt.plot(range(len(queue_lengths_mild)), queue_lengths_mild, label='Mild queue length')
plt.plot(range(len(queue_lengths_moderate)), queue_lengths_moderate, label='Moderate queue length')
plt.plot(range(len(queue_lengths_severe)), queue_lengths_severe, label='Severe queue length')
plt.xlabel('Days')
plt.ylabel('Queue Length')
plt.title('Queue length varies with time.')
plt.legend()
plt.show()

plt.figure(figsize=(18, 6))
plt.plot(range(len(allocation_mild_list)), allocation_mild_list, label='Mild resource allocation ratio')
plt.plot(range(len(allocation_moderate_list)), allocation_moderate_list, label='Moderate resource allocation ratio')
plt.plot(range(len(allocation_severe_list)), allocation_severe_list, label='Severe resource allocation ratio')
plt.xlabel('Days')
plt.ylabel('Resource allocation coefficient')
plt.title('The allocation ratio of resources changes over time.')
plt.legend()
plt.show()

plt.figure(figsize=(18, 6))
plt.plot(range(len(daily_net_new_mild)), daily_net_new_mild, label='Daily net increase of mild queue patients')
plt.plot(range(len(daily_net_new_moderate)), daily_net_new_moderate, label='Daily net increase of moderate queue patients')
plt.plot(range(len(daily_net_new_severe)), daily_net_new_severe, label='Daily net increase in severe queue patients')
plt.xlabel('Days')
plt.ylabel('Net increase in number of patients')
plt.title('The net increase in the number of patients in each queue per day')
plt.legend()
plt.show()

plt.figure(figsize=(18, 6))
plt.plot(range(len(cumulative_cured_mild)), cumulative_cured_mild, label='Mild queue cumulative number of cured people')
plt.plot(range(len(cumulative_cured_moderate)), cumulative_cured_moderate, label='Cumulative number of moderate cases recovered')
plt.plot(range(len(cumulative_cured_severe)), cumulative_cured_severe, label='Severe queue cumulative number of cured people')
plt.xlabel('Days')
plt.ylabel('Cumulative number of recovered cases')
plt.title('Cumulative number of cured people in each queue')
plt.legend()
plt.show()

print(f"Number of mild cases after one year: {mild_cases_after_one_year:.0f}")
print(f"Number of moderate cases after one year: {moderate_cases_after_one_year:.0f}")
print(f"Number of severe cases after one year: {severe_cases_after_one_year:.0f}")
print(f"Average waiting time for mild cases: {avg_waiting_time_mild:.2f} days")
print(f"Average waiting time for moderate cases: {avg_waiting_time_moderate:.2f} days")
print(f"Average waiting time for severe cases: {avg_waiting_time_severe:.2f} days")
print(f"Average queue length for mild cases: {avg_queue_length_mild:.2f}")
print(f"Average queue length for moderate cases: {avg_queue_length_moderate:.2f}")
print(f"Average queue length for severe cases: {avg_queue_length_severe:.2f}")

monthly_allocations = pd.DataFrame({
    'Day': range(len(allocation_mild_list)),
    'Mild': allocation_mild_list,
    'Moderate': allocation_moderate_list,
    'Severe': allocation_severe_list
})
monthly_allocations = monthly_allocations[monthly_allocations['Day'] % 30 == 0]
print("\nMonthly resource allocation ratios:")
print(monthly_allocations)
