#!/usr/bin/env python3
"""
Python script that provides some stats about Nginx logs stored in MongoDB
"""


from pymongo import MongoClient


def log_stats():
    """
    provides some stats about Nginx logs stored in MongoDB
    """
    client = MongoClient()
    db = client.logs
    collection = db.nginx
    
    # Get the total number of logs
    total_logs = collection.count_documents({})
    print(f"{total_logs} logs")
    
    # Print the methods count
    print("Methods:")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods:
        count = collection.count_documents({"method": method})
        print(f"\tmethod {method}: {count}")
    
    # Count status check logs
    status_check_count = collection.count_documents({"method": "GET", "path": "/status"})
    print(f"{status_check_count} status check")

if __name__ == "__main__":
    log_stats()
