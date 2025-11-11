# Test Checklist - Expert Neo4j v0.2.3

## Status: 2/110 completed

### Basic MATCH (0/10)
- [ ] match_001 - Find all people
- [ ] match_002 - List all movies  
- [ ] match_003 - Get all products
- [ ] match_004 - Show all users
- [ ] match_005 - Find all books
- [ ] match_006 - List all cities
- [ ] match_007 - Get all companies
- [ ] match_008 - Find all orders
- [ ] match_009 - Show all employees
- [ ] match_010 - List all customers

### WHERE Filters (0/15)
- [ ] where_001 - Find people older than 30
- [ ] where_002 - Find products with price less than 100
- [ ] where_003 - Find movies released after 2000
- [ ] where_004 - Find people aged between 25 and 40
- [ ] where_005 - Find products in Electronics category
- [ ] where_006 - Find employees with salary greater than 50000
- [ ] where_007 - Find books published before 2010
- [ ] where_008 - Find active users
- [ ] where_009 - Find orders with status 'completed'
- [ ] where_010 - Find people living in New York
- [ ] where_011 - Find products with price between 50 and 200
- [ ] where_012 - Find movies with rating above 8.0
- [ ] where_013 - Find people aged between 25 and 40 living in New York
- [ ] where_014 - Find employees in Sales department with salary over 60000
- [ ] where_015 - Find products in stock with price less than 50

### Relationships (0/15)
- [ ] rel_001 - Find all actors in movies
- [ ] rel_002 - Find people who know each other
- [ ] rel_003 - Find all employees
- [ ] rel_004 - Find all authors and their books
- [ ] rel_005 - Find customers who placed orders
- [ ] rel_006 - Find all directors
- [ ] rel_007 - Find students enrolled in courses
- [ ] rel_008 - Find users who posted
- [ ] rel_009 - Find people who follow others
- [ ] rel_010 - Find products and their categories
- [ ] rel_011 - Find people who both acted and directed
- [ ] rel_012 - Find cities and their countries
- [ ] rel_013 - Find employees and their departments
- [ ] rel_014 - Find people who work at companies
- [ ] rel_015 - Find users who are members of groups

### Aggregations (0/15)
- [ ] agg_001 - Count total users
- [ ] agg_002 - Sum of all order totals
- [ ] agg_003 - Calculate average rating of all movies
- [ ] agg_004 - Find the maximum product price
- [ ] agg_005 - Find the minimum employee salary
- [ ] agg_006 - Find the average rating for each genre
- [ ] agg_007 - Count orders by status
- [ ] agg_008 - Calculate total price per category
- [ ] agg_009 - Count people by city
- [ ] agg_010 - Find average salary per department
- [ ] agg_011 - Calculate average rating per year
- [ ] agg_012 - Count orders per customer
- [ ] agg_013 - Find total products per category
- [ ] agg_014 - Find average age of all people
- [ ] agg_015 - Count movies per actor

### Ordering (0/10)
- [ ] order_001 - Find top 5 most expensive products
- [ ] order_002 - Show the 3 highest paid employees
- [ ] order_003 - Find top 10 highest rated movies
- [ ] order_004 - Show 5 most recent books
- [ ] order_005 - Find 10 oldest people
- [ ] order_006 - Show 5 orders with highest total
- [ ] order_007 - Find 3 most populated cities
- [ ] order_008 - Show cheapest 5 products
- [ ] order_009 - Find lowest paid 3 employees
- [ ] order_010 - Show 5 oldest movies

### Multi-hop (0/10)
- [ ] multihop_001 - Find people who know someone who follows another person
- [ ] multihop_002 - Find actors who also directed movies
- [ ] multihop_003 - Find students and their teachers
- [ ] multihop_004 - Find users who posted and commented
- [ ] multihop_005 - Find people who know someone who follows them
- [ ] multihop_006 - Find customers and products they ordered
- [ ] multihop_007 - Find employees and their companies
- [ ] multihop_008 - Find authors and their publishers
- [ ] multihop_009 - Find people and their countries
- [ ] multihop_010 - Find users and their permissions

### Complex (0/15)
- [ ] complex_001 - Find people aged between 25 and 40 living in New York
- [ ] complex_002 - Find products in Electronics category that are in stock and cost less than 500
- [ ] complex_003 - Find active employees in Sales department with salary between 50000 and 100000
- [ ] complex_004 - Find action movies released after 2010 with rating above 7.5
- [ ] complex_005 - Find completed orders from last month with total over 1000
- [ ] complex_006 - Find people in New York who know someone older than 30
- [ ] complex_007 - Find products with price less than 100 in Electronics category
- [ ] complex_008 - Find employees in Engineering department with salary above 80000
- [ ] complex_009 - Find movies with rating above 8.0 where the director also acted
- [ ] complex_010 - Find active users who posted more than 10 posts
- [ ] complex_011 - Find people who know someone who follows someone else
- [ ] complex_012 - Find customers who placed orders totaling more than 5000
- [ ] complex_013 - Find books written by authors born after 1980
- [ ] complex_014 - Find students enrolled in more than 3 courses
- [ ] complex_015 - Find people in San Francisco who know someone in New York

### Pattern Matching (0/10)
- [ ] pattern_001 - Find all restaurants in cities
- [ ] pattern_002 - Find products whose name contains 'laptop'
- [ ] pattern_003 - Find movies with title starting with 'The'
- [ ] pattern_004 - Find people with email ending in '@gmail.com'
- [ ] pattern_005 - Find books with title containing 'Python'
- [ ] pattern_006 - Find companies in Technology industry
- [ ] pattern_007 - Find users with username starting with 'admin'
- [ ] pattern_008 - Find products with description containing 'wireless'
- [ ] pattern_009 - Find coffee shops in cities
- [ ] pattern_010 - Find movies with actors whose name contains 'Smith'

### RETURN Projections (0/10)
- [ ] return_001 - Get names and emails of all people
- [ ] return_002 - Get title and rating of all movies
- [ ] return_003 - Get product name and price
- [ ] return_004 - Get employee name and department
- [ ] return_005 - Get actor names and movie titles
- [ ] return_006 - Get customer names and order IDs
- [ ] return_007 - Get book titles and authors
- [ ] return_008 - Get city names and populations
- [ ] return_009 - Get usernames and emails
- [ ] return_010 - Get person names and company names

## Results Summary

### Completed Tests

#### match_001
- **Prompt**: Find all people
- **Output**: ". The user wants me to find all people based on the given dialect and schema. The dialect is cypher, and the schema has a Node properties with Person and Relationships. The Relationships section is empty."
- **Status**: ❌ FAIL - Generated explanation instead of Cypher

#### match_002
- **Prompt**: List all movies
- **Output**: ". Let me check the schema again. The schema has a Node property called Movie with title and released. Relationships are none. So, the task is to retrieve all movies from the Movie node."
- **Status**: ❌ FAIL - Generated explanation instead of Cypher

