'''
Healthcare Analytics
Student: Maria Navarro
Date: Jan 19, 2024
HW 2
Topic: Insurance Market Data & Analytics
'''

import pandas as pd
import re
import geopandas as gpd
import matplotlib.pyplot as plt

''' Question 1: Finding a partner for a “private single-payer” proposal 
If in the future states want to move to a private quasi single payer model, which insurance company in each state is the best candidate to partner with?
'''

# Read enrollment by counties
raw_enrollment_by_county = pd.read_csv('G:/My Drive/Spring 2024/Healthcare/Week2/CPSC_Enrollment_2024_01/CPSC_Enrollment_2024_01/CPSC_Enrollment_Info_2024_01.csv')

# Define a regular expression pattern
pattern = re.compile(r'[HRE]\d{4}')

# Use str.match to filter rows based on pattern
matches = raw_enrollment_by_county['Contract Number'].str.match(pattern, na=False)

# Filter the dataframe to include rows with matches and non-empty enrollment
enrollment_by_county = raw_enrollment_by_county[matches & (raw_enrollment_by_county['Enrollment'] != '*')]

# Read enrollment by plan
raw_enrollment_by_plan = pd.read_excel('G:/My Drive/Spring 2024/Healthcare/Week2/Monthly_Report_By_Plan_2024_01/Monthly_Report_By_Plan_2024_01/Monthly_Report_By_Plan_2024_01.xlsx', skiprows = 4)
raw_enrollment_by_plan.columns = raw_enrollment_by_plan.iloc[0]
raw_enrollment_by_plan = raw_enrollment_by_plan[1:].reset_index(drop=True)

matches2 = raw_enrollment_by_plan['Contract Number'].str.match(pattern, na=False)
enrollment_by_plan = raw_enrollment_by_plan[matches2]

# Read major insurance orgs
orgs = pd.read_excel('G:/My Drive/Spring 2024/Healthcare/Week2/MajorInsuranceOrgs.xlsx')

# Merge major insurance orgs with enrollment by plan
merged_df = pd.merge(enrollment_by_plan, orgs, on='Organization Marketing Name', how='left')
# keep it mind that merged_df has unique contract number and plan ID pairs

# Merge a second time with enrollment_by_county (not sure???)
merged_df2 = pd.merge(enrollment_by_county, merged_df, on=['Contract Number', 'Plan ID'], how='left', suffixes=('_1', '_2'))
merged_df2_sorted = merged_df2.sort_values(by=['State', 'County'])
#print(merged_df2['MajorInsuranceOrgName'].isnull().sum())
merged_df2_sorted['Enrollment'] = merged_df2_sorted['Enrollment'].astype(int)

# Keeping just necessary columns ang aggregating to calculate the total enrollments by state and major org
final_df = merged_df2_sorted.groupby(['State', 'MajorInsuranceOrgName'])['Enrollment'].sum().reset_index()

# Calculating the totals by state
aggr_final_df = final_df.groupby('State')['Enrollment'].sum().reset_index()
# Renaming the total column
aggr_final_df.rename(columns={'Enrollment': 'Total Enrollment'}, inplace=True)

# Merging results together
market_share = pd.merge(final_df, aggr_final_df, on='State', how='left')
market_share['Market_Share'] = market_share['Enrollment'] / market_share['Total Enrollment']

# Which is the company with the largest market share?
# Filter data to focus on specific states
states = ['AZ', 'GA', 'KY', 'NV', 'RI', 'TX', 'VT', 'WV', 'WI']
market_share = market_share[market_share['State'].isin(states)].copy()
print(market_share.sort_values(by='Market_Share', ascending=False).head())

# Calculating the HHI
'''
Below 1,500: Low concentration (competitive market).
1,500 to 2,500: Moderate concentration.
Above 2,500: High concentration (less competitive market).
'''
hhi_df = market_share[['State','Market_Share']].copy()
hhi_df['Market_Share'] = hhi_df['Market_Share']*100
hhi_df['Squared_market_share'] = hhi_df['Market_Share']**2
Final_HHI = hhi_df.groupby('State')[['Squared_market_share']].sum()
Final_HHI = Final_HHI.rename(columns={'Squared_market_share': 'HHI'}).sort_values(by='HHI', ascending=False)

# Pick the top 4 states in terms of market concentration (highest HHIs)
print('These are the top 4 states with the highest market concentration')
print(Final_HHI.head(4))

top_states = list(Final_HHI.head(4)['State'])

# For top 4 states, print the company with the lion share and its market share
for state in top_states:
    print(state)
    top_state_info = market_share[market_share['State']==state].sort_values(by='Market_Share', ascending=False).head(1)
    print('State: {} - Company: {} - Lion Share: {} - HHI: {}'.format(state, top_state_info.iloc[0,1], round(top_state_info.iloc[0,4],3), round(Final_HHI.loc[state,'HHI'],3) ) )

# Plot a bar graph
ax = Final_HHI['HHI'].plot(kind='bar', figsize=(15,8), color='skyblue')
# Plotting line to indicate high concentration threshold and coloring area above it to show states with high concentration (low competitive market)
ax.axhspan(ymin=2500, ymax=max(Final_HHI['HHI']), color='red', alpha=0.2)
ax.axhline(y=2500, color='red', linestyle='--', label='High Concentration')
# Labeling graph
plt.title('HHI by U.S. State')
plt.xlabel('State')
plt.ylabel('HHI')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.show()

''' Question 2: Examine the insurance benefit package
'''
# List the top 5 major insurance companies in terms of market share
top_5_companies = market_share.sort_values(by='Market_Share', ascending=False).head(5)
print("These are the top 5 major insurance companies in terms of market share:")
print(top_5_companies)

# Read the file with tab as delimiter and first row as headers
dental_benefits = pd.read_csv('G:/My Drive/Spring 2024/Healthcare/Week2/PBP_Benefits_2024/pbp_b16_dental.txt', sep='\t', header=0)
dental_benefits['pbp_a_plan_identifier'] = dental_benefits['pbp_a_plan_identifier'].astype(int)

# Find the index of the row with the lowest segment number for each contract and plan id pair
min_segment_index = dental_benefits.groupby(['pbp_a_hnumber', 'pbp_a_plan_identifier'])['segment_id'].idxmin()

# Use the index to filter the data and keep only the rows with the lowest segment number
filtered_dental_benefits = dental_benefits.loc[min_segment_index]

# Looking for duplicates
duplicates_in_merged_df2 = merged_df2[merged_df2.duplicated(subset=['Contract Number', 'Plan ID'], keep=False)]

# Displaying duplicate rows in merged_df2
print("Duplicate Rows in merged_df2:")
print(duplicates_in_merged_df2)

# Looking for duplicates
duplicates_in_dental_benefits = filtered_dental_benefits[filtered_dental_benefits.duplicated(subset=['pbp_a_hnumber', 'pbp_a_plan_identifier'], keep=False)]

# Displaying duplicate rows in dental_benefits
print("\nDuplicate Rows in dental_benefits:")
print(duplicates_in_dental_benefits)

# Link the dental benefit database with the enrollment database on both Contract Number and Plan ID
enrollment_n_dental = pd.merge(merged_df2, filtered_dental_benefits, left_on = ('Contract Number', 'Plan ID'), right_on = ('pbp_a_hnumber', 'pbp_a_plan_identifier') , how='left')

# WORK ON IT!!!!!!!!
# What percentage of the enrollees enjoy the Preventive Dental Items as a supplemental benefit under Part C?
#pbp_b16a_bendesc_yn = Does the plan provide Preventive Dental Items as a supplemental benefit under Part C? 1 = Yes, 2 = No
test1 = enrollment_n_dental[(enrollment_n_dental['State']=='VT') & (enrollment_n_dental['MajorInsuranceOrgName']=='UnitedHealthcare')]
total_enrollees = test1['Enrollment'].astype(int).sum()
benefited_enrollees = len(test1[test1['pbp_b16a_bendesc_yn'] == 1])
perc_preventive_dental = benefited_enrollees /  total_enrollees

# i have the workflow. now i just need to do it for all the top 5 firms


#pbp_b16b_bendesc_yn = Does the plan provide Comprehensive Dental Items as a supplemental benefit under Part C? 1 = Yes, 2 = No


