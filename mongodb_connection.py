from streamlit.connections import ExperimentalBaseConnection
import streamlit as st
from pymongo import MongoClient
import pandas as pd

class MongoDBConnection(ExperimentalBaseConnection):
    def _connect(self, **kwargs):
        conn_string = self._secrets['connection_string']
        self.cluster = MongoClient(conn_string)
        return self.cluster

    def cursor(self, collection_name="Bank_data", db_name="Hackathon_test"):
        self.db = self.cluster[db_name]
        self.collection = self.db[collection_name]
        
        return self.db, self.collection

    def query(self, ttl: int = 3600, user_data=None, query="read", **kwargs):
        @st.cache_data(ttl=ttl)
        def _query(query, _user_data, **kwargs):
            if query == "insert":
                self.collection.insert_many(user_data)
                status = f"Updated Collection by adding {len(user_data)} records !"
            elif query == "delete":
                self.collection.delete_one(user_data)
                status = f"Updated Collection by deleting {user_data} !"
            else:
                find = self.collection.find()
                status = pd.DataFrame(find)
            return status
        
        return _query(query, user_data, **kwargs)
        