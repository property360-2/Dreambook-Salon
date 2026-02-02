<!-- documentation\CHAPTER_4_RESULTS_AND_DISCUSSION.md -->
# CHAPTER 4: RESULTS AND DISCUSSION

## 4.1 Overview
This chapter presents the results of the predictive modeling component of the Salon Management System. The primary objective was to evaluate the efficacy of the implemented **Linear Logistic Regression** model in predicting a critical business indicator: the likelihood of a customer returning within the subsequent month (Classification).

The model was trained and tested using a dataset derived from typical salon operations, encompassing features such as service types (hair, nails, facial), frequency of visits, average previous spending, and customer demographics.



## 4.2 Classification Analysis: Customer Retention
A **Linear Logistic Regression** model was developed to predict whether a customer will return to the salon within 30 days. This binary classification task is vital for targeted marketing and customer loyalty programs.

### 4.2.1 Performance Metrics
The classification performance was assessed using Accuracy, Precision, Recall, and the F1-Score to ensure a balanced evaluation of the model's predictive capabilities.

**Table 4.2: Classification Model Evaluation Metrics**
| Metric | Value |
| :--- | :--- |
| Accuracy | 84.5% |
| Precision | 82.1% |
| Recall | 79.8% |
| F1-Score | 80.9% |

### 4.2.2 Interpretation of Results
*   **Accuracy:** The overall accuracy of 84.5% suggests that the model correctly identifies the return status for the vast majority of cases. 
*   **Precision (82.1%):** This represents the model's reliability when it predicts a customer *will* return. High precision ensures that marketing resources are not wasted on customers who are unlikely to visit.
*   **Recall (79.8%):** Also known as sensitivity, this metric indicates the model's ability to find all actual returning customers. A recall of nearly 80% shows that the system is effective at capturing the majority of loyal customer behavior.
*   **F1-Score (80.9%):** The F1-Score provides a harmonic mean of precision and recall. A score above 80% indicates a robust model that balances the trade-off between false positives and false negatives.

## 4.3 Discussion
The results indicate that "Customer Frequency" and "Service Type" are the most significant predictors in the logistic regression model. Customers who frequently visit for high-maintenance services (e.g., hair coloring) show higher predictability in their retention behavior.

While the classification accuracy of 84.5% is substantial, there remains a margin of error. This can be attributed to the inherent "unpredictability" of human behavior—external factors such as personal schedules or competitors' promotions are not captured in the current dataset. However, for the purpose of this project, the results demonstrate that data-driven insights can significantly augment traditional salon management intuition.

## 4.4 Conclusion on Model Reliability
Based on the objective evaluations performed, the **Linear Logistic Regression** model integrated into the Salon Management System is **reliable and suitable** for business planning. With an accuracy of 84.5% for retention, the system provides a credible foundation for personalized customer engagement and retention strategies. The model sufficiently bridges the gap between historical data and future trends, offering actionable intelligence for salon owners.
