#####################################################
# Comparison of Conversion Rates between AB Testing and Bidding Methods
#####################################################

#####################################################
# Business Problem
#####################################################

# Facebook recently introduced a new bidding type called "average bidding" as an alternative to the existing
# "maximum bidding" type. One of our clients, bombabomba.com, has decided to test this new feature and wants to conduct
# an A/B test to determine if average bidding results in more conversions than maximum bidding. The A/B test has been
# running for 1 month, and bombabomba.com now wants you to analyze the results of this A/B test. The ultimate success
# metric for bombabomba.com is Purchase,so the focus should be on the Purchase metric for statistical testing.

#####################################################
# Dataset Story
#####################################################

# This dataset contains information about a company's website, including the number of ad impressions and clicks by
# users, as well as revenue generated from these ads. There are two separate data sets: Control and Test groups. These
# data sets are located on separate sheets in the ab_testing.xlsx Excel file. Maximum Bidding was applied to the
# Control group, while Average Bidding was applied to the Test group."

# Impression: The number of times an ad was displayed to users.
# Click: The number of times users clicked on the displayed ad.
# Purchase: The number of products purchased after clicking on the ads.
# Earning: The revenue earned from the products purchased after clicking on the ads.

#####################################################
# Project Tasks
#####################################################

######################################################
# AB Testing (Independent Two Sample T Test)
######################################################

# 1. Formulate Hypotheses
# 2. Assumption Checks
#   - 1. Normality Assumption (shapiro)
#   - 2. Homogeneity of Variance (levene)
# 3. Apply the Hypothesis Test (
#   - 1. If assumptions are met, use independent two-sample t-test (parametric test).
#   - 2. If assumptions are not met, use Mann-Whitney U test (non-parametric test).
# 4. Interpret the results based on the p-value.

# Note:
# - If normality assumption is not met, go directly to step 2.
#   If homogeneity of variance assumption is not met, enter the argument to step 1.
# - It may be useful to examine and correct outliers before examining normality.

#####################################################
# Task 1:  Data Preparation and Analysis
#####################################################

# Step 1:Read the dataset consisting of control and test group data named 'ab_testing_data.xlsx'.
#        Assign the Control and Test group data to separate variables.


import pandas as pd
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
# from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

control_df = pd.read_excel("location.xlsx", sheet_name="Control Group")
test_df = pd.read_excel("location.xlsx", sheet_name="Test Group")


# Step 2: Analyze the Control and Test group data.

control_df.head() # maximum bidding is applied
test_df.head() # average bidding is applied


def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    print("##################### Statistical Description #####################")
    print(dataframe.describe().T)


check_df(control_df)
check_df(test_df)

# We should control the Purchase averages because we are using Independent Two Sample T Test.
control_df["Purchase"].mean()
test_df["Purchase"].mean()

# In the test group, where average bidding is used,the average of Purchase transactions appears to have increased.
# Making a direct conclusion that average bidding is more beneficial than maximum bidding simply because the average
# has increased would not be very scientific. To support this intuition with more scientific evidence,
# we will formulate our hypothesis and perform AB testing. Confidence intervallara da göz atalım:

sms.DescrStatsW(control_df["Purchase"]).tconfint_mean()
sms.DescrStatsW(test_df["Purchase"]).tconfint_mean()

# Since the standard deviation of the test group is higher than that of the control group, it is already expected
# that the confidence interval will have a wider range.

# "The purchase value resulting from selecting any of the 40 observations in these groups is within these intervals
# with a 5% margin of error."

# Step 3: After the analysis process, merge the Control and Test group data
# using the concat method.

# After merging, let's create a new column to identify which row belongs to which group. We will stack the dataframes
# on top of each other, and reset the index when switching to the test group

control_df["Group"] = "control group(max bidding)"
test_df["Group"] = "test group(avg bidding)"

df = pd.concat([control_df, test_df], axis=0, ignore_index=False)
df.head()
df.tail()

#####################################################
# Task 2: A/B Test Hypothesis Definition
#####################################################

# Step 1: Define hypothesis

# H0: M1 = M2 (M = mean)
# There is no statistically significant difference between the average Purchase values of the control group
# and the test group.

# H1: M1 != M2
# There is statistically significant difference between the average Purchase values of the control group
# and the test group.


# Step 2: analyze the Purchase averages for the control and test groups

df.groupby("Group").agg({"Purchase": "mean"})

# "The comment we made above is: The average of Purchase transactions appears to have increased in the test group where
# average bidding is used. Making a direct conclusion that average bidding is more beneficial than
# maximum bidding simply because the average has increased would not be very scientific. To support this intuition
# with more scientific evidence, we will formulate our hypothesis and perform AB testing."

#####################################################
# TASK 3: Apply Hypothesis
#####################################################

######################################################
# AB Testing (Independent Two Sample T Test)
######################################################


# Step 1: Before conducting the hypothesis test, perform assumption checks.
# These include Normality Assumption and Homogeneity of Variance."

#  Normality Assumption:

# H0: Normality Assumption is being met.
# H1: Normality Assumption is not being met.

# p-value < 0.05 HO is rejected.
# p-value > 0.05 HO is not rejected.

# shapiro method is used

test_stat, pvalue = shapiro(df.loc[df["Group"] == "control group(max bidding)", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

test_stat, pvalue = shapiro(df.loc[df["Group"] == "test group(avg bidding)", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# Results:
# Test Stat = 0.9773, p-value = 0.5891
# Test Stat = 0.9589, p-value = 0.1541

# p-value > 0.05 for both cases, HO is not rejected for both cases.
# so, "Normality Assumption is being met" for both cases

# Homogeneity of Variance:

# H0: Variances are homogenous.
# H1: Variances are not homogenous.

# p-value < 0.05 HO is rejected.
# p-value > 0.05 HO is not rejected.

# levene method is used

test_stat, pvalue = levene(df.loc[df["Group"] == "control group(max bidding)", "Purchase"],
                           df.loc[df["Group"] == "test group(avg bidding)", "Purchase"])
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# Test Stat = 2.6393, p-value = 0.1083
# p-value > 0.05, HO is not rejected.
# Variances are homogenous.

# Step 2: Based on the results of the Normality Assumption and Homogeneity of Variance, select the appropriate test.

# "Since both assumptions are met, an independent two-sample t-test, which is a parametric test, can be used."

# Hypothesis:

# H0: M1 = M2 (M = mean)
# There is no statistically significant difference between the average Purchase values of the control group
# and the test group.

# H1: M1 != M2
# There is statistically significant difference between the average Purchase values of the control group
# and the test group.

test_stat, pvalue = ttest_ind(df.loc[df["Group"] == "control group(max bidding)", "Purchase"],
                              df.loc[df["Group"] == "test group(avg bidding)", "Purchase"],
                              equal_var=True)
print('Test Stat = %.4f, p-value = %.4f' % (test_stat, pvalue))

# "If Homogeneity of Variance was not met, we should have used equal_var=False in our test."
# Test Stat = -0.9416, p-value = 0.3493

# Step 3: Interpret whether there is a statistically significant difference between the mean purchase values of the
# control and test groups based on the p-value obtained from the test results.

# p-value > 0.05 H0 is not rejected.

# H0: M1 = M2 (M = mean)
# There is no statistically significant difference between the average Purchase values of the control group
# and the test group.

# "We can say with 95% confidence that the difference in means occurred by chance."
##############################################################
# Task 4 : Analysis of the Results
##############################################################

# Step 1: Hangi testi kullandınız, sebeplerini belirtiniz.

# "The Shapiro-Wilk test was used for normality assumption and the Levene's test was used for homogeneity of variances
# assumption. Since both assumptions were met, Independent Two-Sample T Test was used.
# If the assumptions were not met, we should have used a non-parametric test instead,
# as the Independent Two-Sample T Test is a parametric test."

# Step 2: Provide advice to your customer according to test results.

# Based on the analysis, there is no statistically significant difference between the conversions brought by maximum
# bidding and average bidding in terms of purchase value.

# However, since the test group has only been present for 1 month, there are only 40 observations available.
# If there are enough resources, A/B testing can be continued for a while longer with more data to reach a
# more realistic conclusion.

# Also, the single metric should not necessarily be purchase. Click and impression rates may have improved.
# To investigate this, a Two-Sample Proportion Test can be applied.
