

# curl -X POST http://localhost:8000/api/documents/ \
#   -H "Content-Type: application/json" \
#   -d '{
#     "title": "Django Notes",
#     "content": "Django is a Python web framework designed to help developers build web applications quickly.\n\nDjango follows the model-template-view architecture and includes many features for building web applications.\n\nDjango provides an object-relational mapper, commonly called the ORM, which allows developers to interact with a database using Python objects instead of writing every SQL query manually.\n\nDjango also provides URL routing, views, templates, forms, authentication, and an administrative interface."
#   }' | jq
# {
#   "title": "PostgreSQL Notes",
#   "content": "PostgreSQL is an open-source relational database management system.\n\nPostgreSQL uses SQL to create, read, update, and delete data stored in tables.\n\nIt supports transactions, indexes, constraints, foreign keys, and many advanced database features.\n\nPostgreSQL can be extended with additional functionality through extensions.\n\nOne useful extension is pgvector, which allows PostgreSQL to store vector embeddings and perform similarity searches."
# }

# curl -X POST http://localhost:8000/api/documents/ \
#   -H "Content-Type: application/json" \
#   -d '{
#     "title": "Python Data Types",
#     "content": "Python has several built-in data types that are fundamental to programming.\n\nStrings are sequences of characters, created with single or double quotes. They are immutable, meaning once created they cannot be changed. Common string methods include .upper(), .lower(), .strip(), and .split().\n\nLists are ordered, mutable collections that can hold items of any type. You create them with square brackets: my_list = [1, 2, 3]. Lists support indexing, slicing, and methods like .append(), .pop(), and .sort().\n\nDictionaries are key-value pairs, created with curly braces: my_dict = {\"name\": \"Alice\", \"age\": 30}. Keys must be immutable (strings, numbers, tuples), but values can be any type. Access values with my_dict[\"name\"] or my_dict.get(\"name\").\n\nTuples are like lists but immutable. Once created, you cannot add or remove items. They are created with parentheses: my_tuple = (1, 2, 3). Tuples are often used for fixed collections of related values.\n\nSets are unordered collections of unique items. They are useful for removing duplicates and performing mathematical set operations like union, intersection, and difference."
#   }' | jq