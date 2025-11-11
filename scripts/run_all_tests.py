"""
Run all tests from checklist via CLI and update checklist with results
"""

import subprocess
import re
from pathlib import Path
import json

CLI_PATH = Path("../../cli/target/release/expert-cli.exe")
VERSION = "0.2.3"
CHECKLIST_MD = Path(__file__).parent.parent / "test_checklist.md"

# Test cases mapping
TEST_CASES = {
    "match_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find all people"},
    "match_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "List all movies"},
    "match_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Get all products"},
    "match_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Show all users"},
    "match_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Find all books"},
    "match_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "List all cities"},
    "match_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Company**\n  - `name`: STRING\n  - `industry`: STRING\nRelationships:\nNone", "user_prompt": "Get all companies"},
    "match_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\nRelationships:\nNone", "user_prompt": "Find all orders"},
    "match_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Show all employees"},
    "match_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "List all customers"},
    
    "where_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find people older than 30"},
    "where_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price less than 100"},
    "where_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "Find movies released after 2000"},
    "where_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40"},
    "where_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Find products in Electronics category"},
    "where_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find employees with salary greater than 50000"},
    "where_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\nNone", "user_prompt": "Find books published before 2010"},
    "where_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `active`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find active users"},
    "where_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\n  - `status`: STRING\nRelationships:\nNone", "user_prompt": "Find orders with status 'completed'"},
    "where_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people living in New York"},
    "where_011": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price between 50 and 200"},
    "where_012": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find movies with rating above 8.0"},
    "where_013": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40 living in New York"},
    "where_014": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Find employees in Sales department with salary over 60000"},
    "where_015": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `in_stock`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find products in stock with price less than 50"},
    
    "rel_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Find all actors in movies"},
    "rel_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people who know each other"},
    "rel_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT]->(:Company)", "user_prompt": "Find all employees"},
    "rel_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Author**\n  - `name`: STRING\n- **Book**\n  - `title`: STRING\nRelationships:\n(:Author)-[:WROTE]->(:Book)", "user_prompt": "Find all authors and their books"},
    "rel_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Find customers who placed orders"},
    "rel_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find all directors"},
    "rel_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)", "user_prompt": "Find students enrolled in courses"},
    "rel_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Post**\n  - `title`: STRING\nRelationships:\n(:User)-[:POSTED]->(:Post)", "user_prompt": "Find users who posted"},
    "rel_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who follow others"},
    "rel_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n- **Category**\n  - `name`: STRING\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find products and their categories"},
    "rel_011": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find people who both acted and directed"},
    "rel_012": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n- **Country**\n  - `name`: STRING\nRelationships:\n(:City)-[:LOCATED_IN]->(:Country)", "user_prompt": "Find cities and their countries"},
    "rel_013": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n- **Department**\n  - `name`: STRING\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)", "user_prompt": "Find employees and their departments"},
    "rel_014": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT {start_date: DATE}]->(:Company)", "user_prompt": "Find people who work at companies"},
    "rel_015": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Group**\n  - `name`: STRING\nRelationships:\n(:User)-[:MEMBER_OF]->(:Group)", "user_prompt": "Find users who are members of groups"},
    
    "agg_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `name`: STRING\nRelationships:\nNone", "user_prompt": "Count total users"},
    "agg_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Sum of all order totals"},
    "agg_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate average rating of all movies"},
    "agg_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the maximum product price"},
    "agg_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the minimum employee salary"},
    "agg_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `genre`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the average rating for each genre"},
    "agg_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\n  - `status`: STRING\nRelationships:\nNone", "user_prompt": "Count orders by status"},
    "agg_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `category`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate total price per category"},
    "agg_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Count people by city"},
    "agg_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `department`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find average salary per department"},
    "agg_011": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `year`: INTEGER\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate average rating per year"},
    "agg_012": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Count orders per customer"},
    "agg_013": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find total products per category"},
    "agg_014": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find average age of all people"},
    "agg_015": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Count movies per actor"},
    
    "order_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find top 5 most expensive products"},
    "order_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Show the 3 highest paid employees"},
    "order_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find top 10 highest rated movies"},
    "order_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\nNone", "user_prompt": "Show 5 most recent books"},
    "order_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find 10 oldest people"},
    "order_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\nRelationships:\nNone", "user_prompt": "Show 5 orders with highest total"},
    "order_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "Find 3 most populated cities"},
    "order_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Show cheapest 5 products"},
    "order_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find lowest paid 3 employees"},
    "order_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "Show 5 oldest movies"},
    
    "multihop_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows another person"},
    "multihop_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find actors who also directed movies"},
    "multihop_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\n- **Teacher**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)\n(:Teacher)-[:TEACHES]->(:Course)", "user_prompt": "Find students and their teachers"},
    "multihop_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Post**\n  - `title`: STRING\n- **Comment**\n  - `text`: STRING\nRelationships:\n(:User)-[:POSTED]->(:Post)\n(:User)-[:COMMENTED_ON]->(:Post)", "user_prompt": "Find users who posted and commented"},
    "multihop_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows them"},
    "multihop_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\n- **Product**\n  - `name`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)\n(:Order)-[:CONTAINS]->(:Product)", "user_prompt": "Find customers and products they ordered"},
    "multihop_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n- **Department**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)\n(:Department)-[:PART_OF]->(:Company)", "user_prompt": "Find employees and their companies"},
    "multihop_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Author**\n  - `name`: STRING\n- **Book**\n  - `title`: STRING\n- **Publisher**\n  - `name`: STRING\nRelationships:\n(:Author)-[:WROTE]->(:Book)\n(:Publisher)-[:PUBLISHED]->(:Book)", "user_prompt": "Find authors and their publishers"},
    "multihop_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **City**\n  - `name`: STRING\n- **Country**\n  - `name`: STRING\nRelationships:\n(:Person)-[:LIVES_IN]->(:City)\n(:City)-[:LOCATED_IN]->(:Country)", "user_prompt": "Find people and their countries"},
    "multihop_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Group**\n  - `name`: STRING\n- **Permission**\n  - `name`: STRING\nRelationships:\n(:User)-[:MEMBER_OF]->(:Group)\n(:Group)-[:HAS]->(:Permission)", "user_prompt": "Find users and their permissions"},
    
    "complex_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40 living in New York"},
    "complex_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\n  - `in_stock`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find products in Electronics category that are in stock and cost less than 500"},
    "complex_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\n  - `active`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find active employees in Sales department with salary between 50000 and 100000"},
    "complex_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\n  - `rating`: FLOAT\n  - `genre`: STRING\nRelationships:\nNone", "user_prompt": "Find action movies released after 2010 with rating above 7.5"},
    "complex_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\n  - `status`: STRING\n  - `date`: DATE\nRelationships:\nNone", "user_prompt": "Find completed orders from last month with total over 1000"},
    "complex_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people in New York who know someone older than 30"},
    "complex_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find products with price less than 100 in Electronics category"},
    "complex_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)", "user_prompt": "Find employees in Engineering department with salary above 80000"},
    "complex_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find movies with rating above 8.0 where the director also acted"},
    "complex_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `active`: BOOLEAN\nRelationships:\n(:User)-[:POSTED]->(:Post)", "user_prompt": "Find active users who posted more than 10 posts"},
    "complex_011": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows someone else"},
    "complex_012": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Find customers who placed orders totaling more than 5000"},
    "complex_013": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\n(:Author)-[:WROTE]->(:Book)", "user_prompt": "Find books written by authors born after 1980"},
    "complex_014": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)", "user_prompt": "Find students enrolled in more than 3 courses"},
    "complex_015": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people in San Francisco who know someone in New York"},
    
    "pattern_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)", "user_prompt": "Find all restaurants in cities"},
    "pattern_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Find products whose name contains 'laptop'"},
    "pattern_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `genre`: STRING\nRelationships:\nNone", "user_prompt": "Find movies with title starting with 'The'"},
    "pattern_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Find people with email ending in '@gmail.com'"},
    "pattern_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\nRelationships:\nNone", "user_prompt": "Find books with title containing 'Python'"},
    "pattern_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Company**\n  - `name`: STRING\n  - `industry`: STRING\nRelationships:\nNone", "user_prompt": "Find companies in Technology industry"},
    "pattern_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\nRelationships:\nNone", "user_prompt": "Find users with username starting with 'admin'"},
    "pattern_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `description`: STRING\nRelationships:\nNone", "user_prompt": "Find products with description containing 'wireless'"},
    "pattern_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)", "user_prompt": "Find coffee shops in cities"},
    "pattern_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Find movies with actors whose name contains 'Smith'"},
    
    "return_001": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Get names and emails of all people"},
    "return_002": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Get title and rating of all movies"},
    "return_003": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Get product name and price"},
    "return_004": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Get employee name and department"},
    "return_005": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Get actor names and movie titles"},
    "return_006": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Get customer names and order IDs"},
    "return_007": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Get book titles and authors"},
    "return_008": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "Get city names and populations"},
    "return_009": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Get usernames and emails"},
    "return_010": {"system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT]->(:Company)", "user_prompt": "Get person names and company names"},
}

def run_cli_test(test_id: str, full_prompt: str) -> tuple[str, bool]:
    """Run test via CLI and return output and validity"""
    cmd = [
        str(CLI_PATH),
        "chat",
        "--experts", f"neo4j@{VERSION}",
        "--prompt", full_prompt,
        "--max-tokens", "500",
        "--temperature", "0.1",
        "--top-p", "0.95",
        "--top-k", "20",
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True,
            timeout=60
        )
        output = result.stdout.strip()
        if "Assistant:" in output:
            output = output.split("Assistant:", 1)[1].strip()
        
        # Check if output is valid Cypher
        is_valid = is_valid_cypher(output)
        return output, is_valid
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]", False
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr[:100]}]", False
    except FileNotFoundError:
        return f"[ERROR: CLI not found]", False

def is_valid_cypher(output: str) -> bool:
    """
    Manual validation - returns False by default, will be updated manually
    This function is kept for structure but actual validation is done manually
    """
    # Always return False - manual analysis will determine pass/fail
    return False

def update_checklist_markdown(test_id: str, passed: bool, output: str):
    """Update checklist markdown file"""
    checklist_path = Path(__file__).parent.parent / "test_checklist.md"
    if not checklist_path.exists():
        return
    
    content = checklist_path.read_text(encoding='utf-8')
    
    # Find the test line and update it
    pattern = rf'(- \[ \]) {re.escape(test_id)}'
    replacement = f'- [{"x" if passed else " "}] {test_id}'
    content = re.sub(pattern, replacement, content)
    
    # Update status count
    total_match = re.search(r'## Status: (\d+)/(\d+) completed', content)
    if total_match:
        current = int(total_match.group(1))
        total = int(total_match.group(2))
        new_current = current + 1
        content = re.sub(
            r'## Status: \d+/\d+ completed',
            f'## Status: {new_current}/{total} completed',
            content
        )
    
    # Add result to Results Summary section
    result_section = "## Results Summary\n\n### Completed Tests\n\n"
    if result_section in content:
        # Find where to insert
        status_icon = "[OK]" if passed else "[FAIL]"
        status_text = "PASS" if passed else "FAIL"
        result_entry = f"#### {test_id}\n- **Prompt**: {TEST_CASES[test_id]['user_prompt']}\n- **Output**: {output[:200]}{'...' if len(output) > 200 else ''}\n- **Status**: {status_icon} {status_text}\n\n"
        
        # Insert after "### Completed Tests\n\n"
        insert_pos = content.find(result_section) + len(result_section)
        content = content[:insert_pos] + result_entry + content[insert_pos:]
    
    checklist_path.write_text(content, encoding='utf-8')

def main():
    print("=" * 80)
    print(f"RUNNING ALL TESTS - EXPERT NEO4J v{VERSION}")
    print("=" * 80)
    print()
    
    # Get all test IDs from checklist
    checklist_path = Path(__file__).parent.parent / "test_checklist.md"
    if not checklist_path.exists():
        print(f"Error: Checklist not found at {checklist_path}")
        return
    
    content = checklist_path.read_text(encoding='utf-8')
    
    # Extract test IDs that are not yet completed
    test_ids = []
    for test_id in TEST_CASES.keys():
        # Check if test is marked as incomplete in checklist
        pattern = rf'- \[ \] {re.escape(test_id)}'
        if re.search(pattern, content):
            test_ids.append(test_id)
    
    print(f"Found {len(test_ids)} tests to run")
    print()
    
    passed = 0
    failed = 0
    
    for idx, test_id in enumerate(test_ids, 1):
        test_case = TEST_CASES[test_id]
        full_prompt = f"{test_case['system_prompt']}\n\n{test_case['user_prompt']}"
        
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(test_ids)}] TEST: {test_id}")
        print(f"{'='*80}")
        print(f"Category: {test_id.split('_')[0]}")
        print(f"User Prompt: {test_case['user_prompt']}")
        print(f"\nRunning CLI test...")
        
        output, _ = run_cli_test(test_id, full_prompt)
        
        print(f"\n{'='*80}")
        print("OUTPUT:")
        print(f"{'='*80}")
        print(output)
        print(f"{'='*80}")
        
        # Manual analysis - ask user or analyze manually
        # For now, mark as FAIL and update checklist with output
        # User will manually review and update
        is_valid = False  # Default to False, will be updated manually
        
        # Update checklist with output (marked as FAIL initially)
        update_checklist_markdown(test_id, is_valid, output)
        
        if is_valid:
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tests: {len(test_ids)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed/len(test_ids)*100):.1f}%")
    print()
    print(f"Checklist updated: {checklist_path}")

if __name__ == "__main__":
    main()

