import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
import seaborn as sns
import matplotlib.pyplot as plt

'''
Analyzing the national registry of healthcare providers "National Plan & Provider Enumeration System NPPES"
Data analytics project on a 2.5 billion-cell database
'''

# Data Processing
'''
file_path = "G://My Drive//Spring 2024//Healthcare//Week1//NPPES_Data_Dissemination_January_2024//npidata_pfile_20050523-20240107.csv"

# Specify columns to load
columns_to_load = ['NPI',
                   'Entity Type Code',
                   'Provider Organization Name (Legal Business Name)',
                   'Provider Last Name (Legal Name)',
                   'Provider First Name',
                   'Provider Middle Name',
                   'Provider Business Mailing Address City Name',
                   'Provider Business Mailing Address State Name',
                   'Provider Business Practice Location Address State Name',
                   'Provider Gender Code',
                   'Healthcare Provider Taxonomy Code_1',
                   'Provider License Number State Code_1',
                   'Is Sole Proprietor']

# Read CSV file with selected columns
data = pd.read_csv(file_path, usecols=columns_to_load)
print(data.head())

# Save file
data.to_csv('filtered_data', index = False)
'''
####################
# Reading the data
data = pd.read_csv('G://My Drive//Spring 2024//Healthcare//Week1//New folder//filtered_data')

# Question 1
# Dictionary to store NDI of the PCP for each student
npi_dict = {'MN': 1922486554, 'KA': 1073008777, 'SH' : 1679603757, 'SV': 1760647770, 'DN' : 1740283555}

for student, npi_code in npi_dict.items():
    print(student, data.loc[data['NPI'] == npi_code, 'Provider License Number State Code_1'].values)

# Question 2: Fisher's Exact Test
'''
Running a statistical test exploring gender differences in practicing as a Sole Proprietor using the Fisher's Exact Test
Null hypothesis (H0): Assumes that there is no association between gender and sole proprietor status
Alternative Hypothesis (H1): Assumes that there is a significant association between gender and sole proprietor status
P-value: The probability of obtaining results as extreme as the observed results, assuming the null hypothesis is true
'''

# Building the 2x2 table
states = ['AZ', 'GA', 'KY', 'NV', 'RI', 'TX', 'VT', 'WV', 'WI']
data_filtered_states = data[data['Provider Business Practice Location Address State Name'].isin(states)]
columns_to_keep = ['Provider Gender Code', 'Is Sole Proprietor']

# Create a new dataframe by keeping only necessary rows and columns
data_q2 = data_filtered_states[
    (data_filtered_states['Provider Gender Code'].isin(['M', 'F'])) &
    (data_filtered_states['Is Sole Proprietor'].isin(['Y', 'N'])) &
    (data_filtered_states['Entity Type Code'] == 1)][columns_to_keep]

# Create a 2x2 contingency table with counts. Rows represent genders (M or F) and columns represent sole proprietor (Y or N)
data_q2_counts = pd.crosstab(data_q2['Provider Gender Code'], data['Is Sole Proprietor'])

print(data_q2_counts)

# Perform Fisher's Exact Test
odds_ratio, p_value = fisher_exact(data_q2_counts, alternative='two-sided')
alpha = 0.05

# Output the odds ratio and p-value based on the counts in the contingency table
print(f'Alpha: {alpha}')
print(f'P-value: {p_value}')

if p_value < alpha:
    print('The p-value is much smaller than alpha, which suggests that the observed data is unlikely under the assumption of the null hypothesis, leading to the rejection of the null hypothesis in favor of the alternative hypothesis. Therefore, there is a significant association between gender and sole proprietor.')
else:
    print('The p-value is greater than alpha, which suggests that the observed data is likely under the assumption of the null hypothesis, failing to reject the null hypothesis. Therefore, there is a not significant association between gender and sole proprietor.')

# Question 3
'''
Running a statistical test to test whether male doctors are more likely than their female peers to choose the practices associated with higher risk for a higher reward

Low risk/reward: Obstetrics & gynecology + Pediatrics
High risk/reward: Surgery + Orthopaedic Surgery

H0: Male doctors are equally likely than female doctors to choose the practices that are associated with higher risk for a higher reward.
H1: Male doctors are more likely than female doctors to choose the practices that are associated with higher risk for a higher reward.
'''

low_risk = ['207V00000X', '208000000X']
high_risk = ['208600000X', '207X00000X']

# Create a new dataframe by keeping only necessary rows and columns
data_q3 = data_filtered_states[
    (data_filtered_states['Provider Gender Code'].isin(['M', 'F'])) &
    (data_filtered_states['Entity Type Code'] == 1) &
    (data_filtered_states['Healthcare Provider Taxonomy Code_1'].isin(low_risk) | data_filtered_states['Healthcare Provider Taxonomy Code_1'].isin(high_risk))].copy()

data_q3 = data_filtered_states[data_filtered_states['Healthcare Provider Taxonomy Code_1'].isin(low_risk) | data_filtered_states['Healthcare Provider Taxonomy Code_1'].isin(high_risk)].copy()
data_q3.loc[:, 'Risk/Reward'] = np.where(data_q3['Healthcare Provider Taxonomy Code_1'].isin(low_risk), 'low', 'high')

data_q3_counts = pd.crosstab(data_q3['Provider Gender Code'], data_q3['Risk/Reward'])

print(data_q3_counts)

# Perform Fisher's Exact Test
odds_ratio_q3, p_value_q3 = fisher_exact(data_q3_counts, alternative='greater')
alpha = 0.05
res = fisher_exact(data_q3_counts, alternative='greater')
print(res.pvalue)

# Output the odds ratio and p-value based on the counts in the contingency table
print(f'Alpha: {alpha}')
print(f'One-sided p-value: {p_value_q3}')

if p_value < alpha:
    print('The p-value is smaller than alpha, which suggests that the observed data is unlikely under the assumption of the null hypothesis, leading to the rejection of the null hypothesis in favor of the alternative hypothesis.')
else:
    print('The p-value is greater than alpha, which suggests that the observed data is likely under the assumption of the null hypothesis, failing to reject the null hypothesis.')

# Question 4
# Graphing the MRI density per 1 million people across the 50 US States

# Finding MRI centers (healthcare facilities not individual providers)
data_q4 = data[(data['Entity Type Code'] == 2) &
               (data['Healthcare Provider Taxonomy Code_1'] == '261QM1200X')]

# Calculating the number of MRI centers per state
data_q4_grouped = data_q4.groupby('Provider Business Practice Location Address State Name')['Healthcare Provider Taxonomy Code_1'].count().sort_index().reset_index(name = 'MRI Counts')

# Importing the population data
pop_data = pd.read_excel('G://My Drive//Spring 2024//Healthcare//Week1//New folder//Population_US.xlsx', sheet_name = 1)
pop_data.drop(columns='Geographic Area', inplace=True)

# Merging two datasets to calculate the MRI density per 1 million people
data_q4_merged = pd.merge(data_q4_grouped, pop_data, left_on='Provider Business Practice Location Address State Name', right_on='State Code', how='inner')
data_q4_merged['Population in millions'] = data_q4_merged['Population'] / 1000000
data_q4_merged['MRI density per 1mill population'] = data_q4_merged['MRI Counts'] / data_q4_merged['Population in millions']
data_q4_merged.sort_values(by='MRI density per 1mill population', ascending = False, inplace=True)

# Graphing the results in a bar plot
sns.barplot(y=data_q4_merged['State Code'], x=data_q4_merged['MRI density per 1mill population'], palette='viridis', legend=False)
plt.show()
