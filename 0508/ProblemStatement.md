20 Complex SQL Problems for Ecommerce Database
1. Customer Lifetime Value Analysis
Problem: Find the top 10 customers by lifetime value (total spent), along with their average order value, total number of orders, and the time between their first and last order. Include only customers who have made more than 3 orders.
2. Product Performance with Category Hierarchy
Problem: Create a report showing each product's performance metrics including total revenue, units sold, average rating, and its category path (parent category → child category). Include products that have been ordered at least once in the last 6 months.
3. Monthly Revenue Trend with Growth Rate
Problem: Calculate monthly revenue for the last 12 months, along with month-over-month growth rate percentage and a 3-month moving average. Include the number of unique customers and average order value for each month.
4. Customer Segmentation Based on Purchase Behavior
Problem: Segment customers into groups (High Value, Medium Value, Low Value, At Risk) based on their total spent, recency of last purchase, and frequency of purchases. Show the count and percentage of customers in each segment.
5. Product Recommendation Based on Co-purchases
Problem: Find products that are frequently bought together. For each product, show the top 3 products that are most commonly purchased in the same order, along with the co-purchase frequency percentage.
6. Inventory Management Alert System
Problem: Create a comprehensive inventory report showing products that need attention: products below minimum stock level, products with zero sales in the last 30 days, and products with high sales velocity (sold more than 50% of stock in last 30 days).
7. Customer Churn Analysis
Problem: Identify customers who are likely to churn (haven't made a purchase in the last 90 days but were active before). Calculate their historical average purchase frequency and total value, and rank them by churn risk.
8. Seasonal Sales Pattern Analysis
Problem: Analyze sales patterns by quarter for each product category over the last 2 years. Show the seasonal index (quarter performance vs annual average) and identify which categories are most seasonal.
9. Advanced Review Analytics
Problem: Create a comprehensive review analysis showing: average rating by product category, correlation between price and ratings, products with significantly improving/declining ratings over time, and the impact of verified vs unverified reviews.
10. Customer Purchase Journey Analysis
Problem: Analyze the customer purchase journey by calculating the average time between registration and first purchase, average time between purchases, and the typical progression of order values (increasing, decreasing, or stable) for each customer.
11. Dynamic Pricing Impact Analysis
Problem: For products that have had price changes, analyze the impact on sales volume, revenue, and customer behavior. Compare sales performance for 30 days before and after each price change.
12. Loyalty Program Effectiveness
Problem: Analyze the effectiveness of the loyalty program by comparing customer behavior before and after earning/spending loyalty points. Include metrics like order frequency, average order value, and retention rate.
13. Geographic Sales Distribution (if location data available)
Problem: Assuming shipping addresses contain city/state information, analyze sales distribution by geographic region. Show top-performing regions by revenue, average order value, and customer acquisition cost.
14. Product Category Cross-sell Analysis
Problem: Identify cross-selling opportunities by analyzing which product categories are purchased together. Create a matrix showing the probability of Category B being purchased when Category A is in the cart.
15. Customer Retention Cohort Analysis
Problem: Perform a cohort analysis based on customer registration month. Show the percentage of customers from each cohort who made purchases in subsequent months (Month 1, Month 3, Month 6, Month 12).
16. Order Fulfillment Performance
Problem: Analyze order fulfillment metrics including average processing time, shipping time, and delivery time by order value ranges and shipping methods. Identify bottlenecks in the fulfillment process.
17. Product Profitability Analysis
Problem: Calculate product profitability considering cost price, selling price, discount amounts, and return rates. Rank products by profit margin and identify the most and least profitable products in each category.
18. Customer Service Impact on Sales
Problem: Analyze the relationship between customer reviews (especially negative ones) and subsequent sales performance. Show how products recover or decline after receiving poor reviews.
19. Advanced ABC Analysis for Inventory
Problem: Perform an ABC analysis of products based on multiple criteria: revenue contribution (40%), profit margin (35%), and sales velocity (25%). Categorize products into A, B, and C classes with appropriate inventory management strategies.
20. Predictive Customer Lifetime Value
Problem: Calculate predicted customer lifetime value using historical data. For each customer, predict their future value based on purchase frequency, average order value, and the trend of their purchase behavior over time.

Bonus Advanced Problems:
21. Market Basket Analysis with Association Rules
Problem: Implement market basket analysis to find association rules (if Product A is purchased, then Product B is likely to be purchased with X% confidence) with minimum support of 1% and confidence of 30%.
22. Customer Journey Funnel Analysis
Problem: Create a funnel analysis showing: visitors who viewed products, added to cart (if cart data available), placed orders, and completed payments. Calculate conversion rates at each stage.
23. Dynamic Customer Scoring
Problem: Create a dynamic customer scoring system that updates customer scores based on recent activity, purchase history, review contributions, and payment reliability. Use this score to identify VIP customers and potential issues.

Tips for Solving These Problems:

Use Window Functions: Many problems require ROW_NUMBER(), RANK(), LAG(), LEAD(), and aggregate window functions
CTEs (Common Table Expressions): Break complex queries into manageable parts
Subqueries and Joins: Master different types of joins and correlated subqueries
Date Functions: Become proficient with date arithmetic and formatting
Conditional Aggregation: Use CASE statements within aggregate functions
Performance Considerations: Think about indexes and query optimization