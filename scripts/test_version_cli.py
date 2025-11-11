"""
Test expert-neo4j version via CLI (which filters thinking/reasoning)

This script uses the CLI to test the expert, which automatically filters
thinking/reasoning blocks and provides cleaner Cypher output.
"""

import subprocess
import json
import sys
from pathlib import Path
import argparse

# Configuration
CLI_PATH = Path("../../cli/target/release/expert-cli.exe")
BASE_MODEL_PATH = "../../models/Qwen3-0.6B"

# Generation config - increased max_tokens for better context
GEN_CONFIG = {
    "max_tokens": "500",  # Increased from 300
    "temperature": "0.1",  # Low for consistent output
    "top_p": "0.95",
    "top_k": "20",
}

# Test cases (same as before)
TEST_CASES = [
    # Basic MATCH (10 tests)
    {"id": "match_001", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find all people"},
    {"id": "match_002", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "List all movies"},
    {"id": "match_003", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Get all products"},
    {"id": "match_004", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Show all users"},
    {"id": "match_005", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Find all books"},
    {"id": "match_006", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "List all cities"},
    {"id": "match_007", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Company**\n  - `name`: STRING\n  - `industry`: STRING\nRelationships:\nNone", "user_prompt": "Get all companies"},
    {"id": "match_008", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\nRelationships:\nNone", "user_prompt": "Find all orders"},
    {"id": "match_009", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Show all employees"},
    {"id": "match_010", "category": "basic_match", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "List all customers"},
    
    # WHERE filters (15 tests)
    {"id": "where_001", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find people older than 30"},
    {"id": "where_002", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price less than 100"},
    {"id": "where_003", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "Find movies released after 2000"},
    {"id": "where_004", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40"},
    {"id": "where_005", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Find products in Electronics category"},
    {"id": "where_006", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find employees with salary greater than 50000"},
    {"id": "where_007", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\nNone", "user_prompt": "Find books published before 2010"},
    {"id": "where_008", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `active`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find active users"},
    {"id": "where_009", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\n  - `status`: STRING\nRelationships:\nNone", "user_prompt": "Find orders with status 'completed'"},
    {"id": "where_010", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people living in New York"},
    {"id": "where_011", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find products with price between 50 and 200"},
    {"id": "where_012", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find movies with rating above 8.0"},
    {"id": "where_013", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40 living in New York"},
    {"id": "where_014", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Find employees in Sales department with salary over 60000"},
    {"id": "where_015", "category": "where_filter", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `in_stock`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find products in stock with price less than 50"},
    
    # Relationship traversal (15 tests)
    {"id": "rel_001", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Find all actors in movies"},
    {"id": "rel_002", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people who know each other"},
    {"id": "rel_003", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT]->(:Company)", "user_prompt": "Find all employees"},
    {"id": "rel_004", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Author**\n  - `name`: STRING\n- **Book**\n  - `title`: STRING\nRelationships:\n(:Author)-[:WROTE]->(:Book)", "user_prompt": "Find all authors and their books"},
    {"id": "rel_005", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Find customers who placed orders"},
    {"id": "rel_006", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find all directors"},
    {"id": "rel_007", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)", "user_prompt": "Find students enrolled in courses"},
    {"id": "rel_008", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Post**\n  - `title`: STRING\nRelationships:\n(:User)-[:POSTED]->(:Post)", "user_prompt": "Find users who posted"},
    {"id": "rel_009", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who follow others"},
    {"id": "rel_010", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n- **Category**\n  - `name`: STRING\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find products and their categories"},
    {"id": "rel_011", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find people who both acted and directed"},
    {"id": "rel_012", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n- **Country**\n  - `name`: STRING\nRelationships:\n(:City)-[:LOCATED_IN]->(:Country)", "user_prompt": "Find cities and their countries"},
    {"id": "rel_013", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n- **Department**\n  - `name`: STRING\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)", "user_prompt": "Find employees and their departments"},
    {"id": "rel_014", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT {start_date: DATE}]->(:Company)", "user_prompt": "Find people who work at companies"},
    {"id": "rel_015", "category": "relationship", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Group**\n  - `name`: STRING\nRelationships:\n(:User)-[:MEMBER_OF]->(:Group)", "user_prompt": "Find users who are members of groups"},
    
    # Aggregations (15 tests)
    {"id": "agg_001", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `name`: STRING\nRelationships:\nNone", "user_prompt": "Count total users"},
    {"id": "agg_002", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Sum of all order totals"},
    {"id": "agg_003", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate average rating of all movies"},
    {"id": "agg_004", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the maximum product price"},
    {"id": "agg_005", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the minimum employee salary"},
    {"id": "agg_006", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `genre`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find the average rating for each genre"},
    {"id": "agg_007", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\n  - `status`: STRING\nRelationships:\nNone", "user_prompt": "Count orders by status"},
    {"id": "agg_008", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `category`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate total price per category"},
    {"id": "agg_009", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Count people by city"},
    {"id": "agg_010", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `department`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find average salary per department"},
    {"id": "agg_011", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `year`: INTEGER\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Calculate average rating per year"},
    {"id": "agg_012", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Count orders per customer"},
    {"id": "agg_013", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find total products per category"},
    {"id": "agg_014", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find average age of all people"},
    {"id": "agg_015", "category": "aggregation", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Count movies per actor"},
    
    # ORDER BY and LIMIT (10 tests)
    {"id": "order_001", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Find top 5 most expensive products"},
    {"id": "order_002", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Show the 3 highest paid employees"},
    {"id": "order_003", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Find top 10 highest rated movies"},
    {"id": "order_004", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\nNone", "user_prompt": "Show 5 most recent books"},
    {"id": "order_005", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\nNone", "user_prompt": "Find 10 oldest people"},
    {"id": "order_006", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\nRelationships:\nNone", "user_prompt": "Show 5 orders with highest total"},
    {"id": "order_007", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "Find 3 most populated cities"},
    {"id": "order_008", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\nNone", "user_prompt": "Show cheapest 5 products"},
    {"id": "order_009", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\nNone", "user_prompt": "Find lowest paid 3 employees"},
    {"id": "order_010", "category": "ordering", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\nRelationships:\nNone", "user_prompt": "Show 5 oldest movies"},
    
    # Multi-hop relationships (10 tests)
    {"id": "multihop_001", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows another person"},
    {"id": "multihop_002", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find actors who also directed movies"},
    {"id": "multihop_003", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\n- **Teacher**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)\n(:Teacher)-[:TEACHES]->(:Course)", "user_prompt": "Find students and their teachers"},
    {"id": "multihop_004", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Post**\n  - `title`: STRING\n- **Comment**\n  - `text`: STRING\nRelationships:\n(:User)-[:POSTED]->(:Post)\n(:User)-[:COMMENTED_ON]->(:Post)", "user_prompt": "Find users who posted and commented"},
    {"id": "multihop_005", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows them"},
    {"id": "multihop_006", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\n- **Product**\n  - `name`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)\n(:Order)-[:CONTAINS]->(:Product)", "user_prompt": "Find customers and products they ordered"},
    {"id": "multihop_007", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n- **Department**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)\n(:Department)-[:PART_OF]->(:Company)", "user_prompt": "Find employees and their companies"},
    {"id": "multihop_008", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Author**\n  - `name`: STRING\n- **Book**\n  - `title`: STRING\n- **Publisher**\n  - `name`: STRING\nRelationships:\n(:Author)-[:WROTE]->(:Book)\n(:Publisher)-[:PUBLISHED]->(:Book)", "user_prompt": "Find authors and their publishers"},
    {"id": "multihop_009", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **City**\n  - `name`: STRING\n- **Country**\n  - `name`: STRING\nRelationships:\n(:Person)-[:LIVES_IN]->(:City)\n(:City)-[:LOCATED_IN]->(:Country)", "user_prompt": "Find people and their countries"},
    {"id": "multihop_010", "category": "multi_hop", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n- **Group**\n  - `name`: STRING\n- **Permission**\n  - `name`: STRING\nRelationships:\n(:User)-[:MEMBER_OF]->(:Group)\n(:Group)-[:HAS]->(:Permission)", "user_prompt": "Find users and their permissions"},
    
    # Complex queries (15 tests)
    {"id": "complex_001", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\nNone", "user_prompt": "Find people aged between 25 and 40 living in New York"},
    {"id": "complex_002", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\n  - `in_stock`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find products in Electronics category that are in stock and cost less than 500"},
    {"id": "complex_003", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\n  - `active`: BOOLEAN\nRelationships:\nNone", "user_prompt": "Find active employees in Sales department with salary between 50000 and 100000"},
    {"id": "complex_004", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\n  - `rating`: FLOAT\n  - `genre`: STRING\nRelationships:\nNone", "user_prompt": "Find action movies released after 2010 with rating above 7.5"},
    {"id": "complex_005", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Order**\n  - `id`: STRING\n  - `total`: FLOAT\n  - `status`: STRING\n  - `date`: DATE\nRelationships:\nNone", "user_prompt": "Find completed orders from last month with total over 1000"},
    {"id": "complex_006", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people in New York who know someone older than 30"},
    {"id": "complex_007", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\nRelationships:\n(:Product)-[:BELONGS_TO]->(:Category)", "user_prompt": "Find products with price less than 100 in Electronics category"},
    {"id": "complex_008", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\nRelationships:\n(:Employee)-[:WORKS_IN]->(:Department)", "user_prompt": "Find employees in Engineering department with salary above 80000"},
    {"id": "complex_009", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `rating`: FLOAT\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)\n(:Person)-[:DIRECTED]->(:Movie)", "user_prompt": "Find movies with rating above 8.0 where the director also acted"},
    {"id": "complex_010", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `active`: BOOLEAN\nRelationships:\n(:User)-[:POSTED]->(:Post)", "user_prompt": "Find active users who posted more than 10 posts"},
    {"id": "complex_011", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\nRelationships:\n(:Person)-[:KNOWS]->(:Person)\n(:Person)-[:FOLLOWS]->(:Person)", "user_prompt": "Find people who know someone who follows someone else"},
    {"id": "complex_012", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `total`: FLOAT\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Find customers who placed orders totaling more than 5000"},
    {"id": "complex_013", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `year`: INTEGER\nRelationships:\n(:Author)-[:WROTE]->(:Book)", "user_prompt": "Find books written by authors born after 1980"},
    {"id": "complex_014", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Student**\n  - `name`: STRING\n- **Course**\n  - `name`: STRING\nRelationships:\n(:Student)-[:ENROLLED_IN]->(:Course)", "user_prompt": "Find students enrolled in more than 3 courses"},
    {"id": "complex_015", "category": "complex", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `city`: STRING\nRelationships:\n(:Person)-[:KNOWS]->(:Person)", "user_prompt": "Find people in San Francisco who know someone in New York"},
    
    # Pattern matching (10 tests)
    {"id": "pattern_001", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)", "user_prompt": "Find all restaurants in cities"},
    {"id": "pattern_002", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Find products whose name contains 'laptop'"},
    {"id": "pattern_003", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `genre`: STRING\nRelationships:\nNone", "user_prompt": "Find movies with title starting with 'The'"},
    {"id": "pattern_004", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Find people with email ending in '@gmail.com'"},
    {"id": "pattern_005", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\nRelationships:\nNone", "user_prompt": "Find books with title containing 'Python'"},
    {"id": "pattern_006", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Company**\n  - `name`: STRING\n  - `industry`: STRING\nRelationships:\nNone", "user_prompt": "Find companies in Technology industry"},
    {"id": "pattern_007", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\nRelationships:\nNone", "user_prompt": "Find users with username starting with 'admin'"},
    {"id": "pattern_008", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `description`: STRING\nRelationships:\nNone", "user_prompt": "Find products with description containing 'wireless'"},
    {"id": "pattern_009", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Business**\n  - `name`: STRING\n  - `category`: STRING\nRelationships:\n(:Business)-[:LOCATED_IN]->(:City)", "user_prompt": "Find coffee shops in cities"},
    {"id": "pattern_010", "category": "pattern", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Find movies with actors whose name contains 'Smith'"},
    
    # RETURN projections (10 tests)
    {"id": "return_001", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n  - `age`: INTEGER\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Get names and emails of all people"},
    {"id": "return_002", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Movie**\n  - `title`: STRING\n  - `released`: INTEGER\n  - `rating`: FLOAT\nRelationships:\nNone", "user_prompt": "Get title and rating of all movies"},
    {"id": "return_003", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Product**\n  - `name`: STRING\n  - `price`: FLOAT\n  - `category`: STRING\nRelationships:\nNone", "user_prompt": "Get product name and price"},
    {"id": "return_004", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Employee**\n  - `name`: STRING\n  - `salary`: FLOAT\n  - `department`: STRING\nRelationships:\nNone", "user_prompt": "Get employee name and department"},
    {"id": "return_005", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\nRelationships:\n(:Person)-[:ACTED_IN]->(:Movie)", "user_prompt": "Get actor names and movie titles"},
    {"id": "return_006", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Customer**\n  - `name`: STRING\n- **Order**\n  - `id`: STRING\nRelationships:\n(:Customer)-[:PLACED]->(:Order)", "user_prompt": "Get customer names and order IDs"},
    {"id": "return_007", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Book**\n  - `title`: STRING\n  - `author`: STRING\nRelationships:\nNone", "user_prompt": "Get book titles and authors"},
    {"id": "return_008", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **City**\n  - `name`: STRING\n  - `population`: INTEGER\nRelationships:\nNone", "user_prompt": "Get city names and populations"},
    {"id": "return_009", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **User**\n  - `username`: STRING\n  - `email`: STRING\nRelationships:\nNone", "user_prompt": "Get usernames and emails"},
    {"id": "return_010", "category": "return", "system_prompt": "Dialect: cypher\nSchema:\nNode properties:\n- **Person**\n  - `name`: STRING\n- **Company**\n  - `name`: STRING\nRelationships:\n(:Person)-[:WORKS_AT]->(:Company)", "user_prompt": "Get person names and company names"},
]

def run_cli_chat(expert_version: str, full_prompt: str) -> str:
    """Run CLI chat command and return cleaned output"""
    cmd = [
        str(CLI_PATH),
        "chat",
        "--experts", f"expert-neo4j@{expert_version}",
        "--prompt", full_prompt,
        "--max-tokens", GEN_CONFIG["max_tokens"],
        "--temperature", GEN_CONFIG["temperature"],
        "--top-p", GEN_CONFIG["top_p"],
        "--top-k", GEN_CONFIG["top_k"],
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        # CLI already filters thinking/reasoning, so just return the output
        output = result.stdout.strip()
        # Remove any "Assistant:" prefix if present
        if "Assistant:" in output:
            output = output.split("Assistant:", 1)[1].strip()
        return output
    except subprocess.CalledProcessError as e:
        return f"[ERROR: {e.stderr}]"
    except FileNotFoundError:
        return f"[ERROR: CLI not found at {CLI_PATH}]"

def main():
    parser = argparse.ArgumentParser(description='Test expert-neo4j version via CLI')
    parser.add_argument('version', help='Expert version to test (e.g., 0.2.3)')
    parser.add_argument('--output', type=str, default='version_cli_test_results.json', help='Output JSON file')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    args = parser.parse_args()
    
    print("=" * 80)
    print(f"CLI TESTING - EXPERT NEO4J v{args.version}")
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Max tokens: {GEN_CONFIG['max_tokens']}")
    print("=" * 80)
    print()
    
    results = []
    for idx, test in enumerate(TEST_CASES, 1):
        if args.verbose or idx % 10 == 0:
            print(f"[{idx}/{len(TEST_CASES)}] {test['id']} ({test['category']})...", end=' ', flush=True)
        
        # Combine system and user prompt
        full_prompt = f"{test['system_prompt']}\n\n{test['user_prompt']}"
        
        output = run_cli_chat(args.version, full_prompt)
        
        if args.verbose or idx % 10 == 0:
            print("DONE")
        
        results.append({
            'test_id': test['id'],
            'category': test['category'],
            'system_prompt': test['system_prompt'],
            'user_prompt': test['user_prompt'],
            'output': output
        })
    
    # Save results
    output_data = {
        'version': args.version,
        'test_config': GEN_CONFIG,
        'total_tests': len(TEST_CASES),
        'results': results
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Results saved to: {args.output}")
    print("Note: LLM will analyze results for correctness")
    print("=" * 80)

if __name__ == "__main__":
    main()

