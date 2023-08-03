import streamlit as st
import pandas as pd
from mongodb_connection import MongoDBConnection
from bson.objectid import ObjectId
    
if 'delete_state' not in st.session_state:
    st.session_state.delete_state = False

if 'status' not in st.session_state:
    st.session_state.status = None
    
if 'count' not in st.session_state:
    st.session_state.count = 0
    
if 'user_data_length' not in st.session_state:
    st.session_state.user_data_length = 0
    
def convert_editable_df_to_jsons(df):
    json_list = []
    for index, row in df.iterrows():
        temp_json = {
            "Name": row['Name'],
            "Account_number": row['Account_number'],
            "Bank_name": row["Bank_name"],
            "Money (dollars)": row["Money (dollars)"]
        }
        json_list.append(temp_json)
    return json_list

insert_df = pd.DataFrame([], columns=["Name", "Account_number", "Bank_name", "Money (dollars)"])
conn = st.experimental_connection("mongodb", type=MongoDBConnection)
db, collection = conn.cursor()

st.title("Connections hackathon 🔌")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Fetch Data'):
        st.session_state.status = 'read'

with col2:
    if st.button('Insert Data'):
        st.session_state.status = 'insert'
        
with col3:
    if st.button("Delete Data"):
        st.session_state.status = 'delete'
        st.session_state.delete_state = False
        
if st.session_state.status == 'read':
    results = conn.query(query = "read", count=st.session_state.count)
    st.dataframe(results)
elif st.session_state.status == 'delete':
    if not st.session_state.delete_state:
        results = conn.query(query = "read", count=st.session_state.count)
        results['Delete?'] = [False] * len(results)
        editable_df = st.data_editor(results)
        delete_df = editable_df.loc[editable_df['Delete?'] == True]
        
        if not delete_df.empty:
            if st.button("Delete selected"):
                user_data = delete_df['_id'].tolist()
                for item in user_data:
                    result = conn.query(query='delete', user_data={'_id': ObjectId(item)}, count=st.session_state.count)
                    st.session_state.count += 1
                st.session_state.delete_state = True
                st.session_state.user_data_length = len(user_data)
                st.experimental_rerun()
    else:
        st.subheader(f"Deleted {st.session_state.user_data_length} records from the collection")
    
elif st.session_state.status == 'insert':
    editable_df = st.data_editor(insert_df, num_rows="dynamic")
    
    if not editable_df.empty:
        if st.button("Insert above data"):
            json_list = convert_editable_df_to_jsons(editable_df)
            status = conn.query(query = "insert", user_data=json_list, count=st.session_state.count)
            st.session_state.count += 1
            st.subheader(status)
    else:
        st.subheader("Press Enter or Tab after adding a new data point to confirm your changes.")
else:
    st.subheader("Waiting for an action !")
    
        

