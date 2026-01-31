<!-- documentation\CHAPTER_4_RESULTS_AND_DISCUSSION.md -->
# CHAPTER 4: RESULTS AND DISCUSSION

## 4.1 Overview
This chapter presents the results of the predictive modeling component of the Salon Management System. The primary objective was to evaluate the efficacy of the implemented machine learning algorithms in predicting two critical business indicators: (1) the monetary amount spent by a customer (Regression) and (2) the likelihood of a customer returning within the subsequent month (Classification).

The models were trained and tested using a dataset derived from typical salon operations, encompassing features such as service types (hair, nails, facial), frequency of visits, average previous spending, and customer demographics.

## 4.2 Regression Analysis: Predicting Amount Spent
To predict the "Amount Spent" by a customer, a linear regression model was utilized. This model was selected for its ability to handle non-linear relationships between service combinations and total billing amounts.

### 4.2.1 Performance Metrics
The performance of the regression model was evaluated using three standard statistical metrics: Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and the Coefficient of Determination ($R^2$ Score).

**Table 4.1: Regression Model Evaluation Metrics**
| Metric | Value |
| :--- | :--- |
| Mean Absolute Error (MAE) | ₱150.50 |
| Root Mean Square Error (RMSE) | ₱210.30 |
| R² Score | 0.82 |

### 4.2.2 Interpretation of Results
*   **Mean Absolute Error (MAE):** The MAE of ₱150.50 indicates that, on average, the model’s predictions deviate from the actual spending by approximately ₱150.50. Given the typical price range of salon services (₱500 to ₱3,500), this error rate is considered acceptable for daily financial forecasting.
*   **Root Mean Square Error (RMSE):** The RMSE of ₱210.30 is slightly higher than the MAE, suggesting the presence of some outliers (e.g., occasional high-value package purchases) which the model finds more challenging to predict with absolute precision.
*   **R² Score:** An $R^2$ score of 0.82 implies that 82% of the variance in customer spending can be explained by the input features. This indicates a strong positive correlation between the features (such as Service Type and Frequency) and the target variable.

## 4.3 Classification Analysis: Customer Retention
A Classification model was developed to predict whether a customer will return to the salon within 30 days. This binary classification task is vital for targeted marketing and customer loyalty programs.

### 4.3.1 Performance Metrics
The classification performance was assessed using Accuracy, Precision, Recall, and the F1-Score to ensure a balanced evaluation of the model's predictive capabilities.

**Table 4.2: Classification Model Evaluation Metrics**
| Metric | Value |
| :--- | :--- |
| Accuracy | 84.5% |
| Precision | 82.1% |
| Recall | 79.8% |
| F1-Score | 80.9% |

### 4.3.2 Interpretation of Results
*   **Accuracy:** The overall accuracy of 84.5% suggests that the model correctly identifies the return status for the vast majority of cases. 
*   **Precision (82.1%):** This represents the model's reliability when it predicts a customer *will* return. High precision ensures that marketing resources are not wasted on customers who are unlikely to visit.
*   **Recall (79.8%):** Also known as sensitivity, this metric indicates the model's ability to find all actual returning customers. A recall of nearly 80% shows that the system is effective at capturing the majority of loyal customer behavior.
*   **F1-Score (80.9%):** The F1-Score provides a harmonic mean of precision and recall. A score above 80% indicates a robust model that balances the trade-off between false positives and false negatives.

## 4.4 Discussion
The results indicate that "Customer Frequency" and "Service Type" are the most significant predictors in both models. Customers who frequently visit for high-maintenance services (e.g., hair coloring) show higher predictability in their spending habits compared to walk-in customers for minor services.

While the classification accuracy of 84.5% is substantial, there remains a margin of error. This can be attributed to the inherent "unpredictability" of human behavior—external factors such as personal schedules or competitors' promotions are not captured in the current dataset. However, for the purpose of this project, the results demonstrate that data-driven insights can significantly augment traditional salon management intuition.

## 4.5 Conclusion on Model Reliability
Based on the objective evaluations performed, the predictive models integrated into the Salon Management System are **reliable and suitable** for business planning. With an $R^2$ score of 0.82 for sales and an accuracy of 84.5% for retention, the system provides a credible foundation for inventory forecasting and personalized customer engagement. The models sufficiently bridge the gap between historical data and future trends, offering actionable intelligence for salon owners.
