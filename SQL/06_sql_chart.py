import streamlit as st
import os
# import openai
import sqlite3
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt

client = OpenAI()

st.title("Create Sqlite3 Query and Chart ")
st.write("----------")

sql = "sqlite3"
 
st.header("Create Sqlite3 Query")
question = st.text_input("질문해보세요.")
st.write("table: 전통주 정보, 전통주 평가, 사용자별 주류별 코멘트 및 평가 & 즐겨찾는 술 쿼리")


contents = '''
### Instructions:`
Your task is convert a question into a SQL query, given a {sql} database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float

### Input:
Generate a SQL query about the `{question}`.
This query will run on a database whose schema is represented in this string:

Table Name: soolpan_user
    Column: id, Type: integer, PRIMARY KEY, -- Unique ID for each user
    Column: email, Type: varchar(254),  -- user`s email
    Column: password, Type: varchar(128), -- user`s password
    Column: level, Type: varchar(8),  -- level of user
    Column: register_date, Type: datetime, -- user`s register_date
Table Name: Comments_data
    Column: id, Type: integer, PRIMARY KEY -- Unique ID for each comment
    Column: body, Type: text,  -- Comment body
    Column: created_at, Type: datetime, -- Date of comment written
    Column: name_id, Type: bigint,  -- Unique ID for each user
    Column: post_id, Type: integer, -- Unique ID for each product
    Column: carbon, Type: integer, -- carbonation rating of alcohol in the comments
    Column: color, Type: integer, --  color rating of the alcohol in the comments
    Column: flavor, Type: integer, -- Taste rating of alcohol in the comments
    Column: sour, Type: integer,  -- Sour rating of alcohol in the comments
    Column: sweet, Type: integer,  -- Sweet rating of alcohol in the comments
    Column: total, Type: integer, -- Total rating of alcohol in the comments
Table Name: favorite_database
    Column: id, Type: integer, PRIMARY KEY -- Unique ID for each product
    Column: like, Type: integer, -- number of times a product has been favorited
    Column: register_date, Type: datetime, -- Date the user liked
    Column: name_id, Type: bigint, -- Unique ID for each user
    Column: post_id, Type: integer, -- Unique ID for each product
Table Name: traditional_liq 
    Column: id, Type: integer, PRIMARY KEY -- Unique ID for each product
    Column: name, Type: varchar(256),  -- name of each product
    Column: company, Type: varchar(256),  -- The company that created the product
    Column: mtrl, Type: varchar(256), -- raw materials for products
    Column: dsc, Type: varchar(512), -- Detailed description of product
    Column: img, Type: varchar(256), -- Image link for product
    Column: std, Type: varchar(256), -- Product capacity and strength
    Column: like, Type: integer, -- Total number of times a product has been favorited
### Answer:
'''.format(question=question, sql=sql)

# encoded_prompt = contents.encode('utf-8').decode('utf-8')


if st.button("질문하기"):
    with st.spinner("Wait for it..."):           
        response =  client.completions.create(
            model="gpt-3.5-turbo-instruct",
        prompt=contents,    
        temperature=0,
        max_tokens=2000
        )

        try:
            print(response.choices[0].text.split(":")[3])
            query = response.choices[0].text.split(":")[3]
        except:
            try:
                print(response.choices[0].text.split(":")[2])
                query = response.choices[0].text.split(":")[2]
            except:
                try:
                    print(response.choices[0].text.split(":")[1])
                    query = response.choices[0].text.split(":")[1]
                except:
                    query = response.choices[0].text
        
        st.header("Sqlite3 Query")
        st.write(query.replace("\n","\n\n"))
        
        conn = sqlite3.connect('./data/db.sqlite3')
        cursor = conn.cursor()
        df = pd.read_sql_query(query, conn)
        st.header("Sqlite3 dataframe")
        st.write(df)
        print(df)        
        contents2 = '''
        ### Instructions: You are a python code writer.
        Your task is writing python simple code for matplotlib chart with given a dataframe.
        Adhere to these rules:
        Don't indent when writing code, especially at the beginning of the code.
        Do not write annotations and Don`t use #.
        Make code with simple and basic function of matplotlib.
        You must use "import matplotlib.pyplot as plt", "import pandas as pd", "import numpy as np".
        df must be defined in python code with using a given df.
        Use parameter "font='Malgun Gothic'" for xticks and yticks and title.
        Before save the plt, "plt.tight_layout()" must be written.
        Save the plt name as "test.png" with dpi=50, and the file must create.
                        
        ### Input:
        {df} is a dataframe that you generate python code for plotly chart.
        df={df}
        ### Solution:
        '''.format(df=df)
        with st.spinner("Wait for it..."):           
            response2 = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=contents2,    
            temperature=0.1,
            max_tokens=1500
            )
                        
            python_code = response2.choices[0].text
            python_code2 = python_code.encode('utf-8')
            
            # python_code = python_code.replace("\u00A0", "")
            # python_code = python_code.replace("\u0009", "\n")
            # python_code = python_code.replace("\u0020", " ")            
            # python_code = python_code.replace("\u2028", "\n\n")          
            
            st.header("Python code")
            st.write(python_code.replace("\n","\n\n"))
            print(python_code)                
            
            
            try:             
                exec(python_code2)
                # run_python_code(python_code, df)
                
                # st.image("test.png")
                try:
                    st.image("test.png")
                    # Specify the file path you want to delete
                    file_path = "test.png"
                    
                    # Check if the file exists before attempting to delete it
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"{file_path} has been deleted.")
                    else:
                        print(f"{file_path} does not exist.")
                except Exception as e:
                    st.header(f"오류 발생: {str(e)}")
            except Exception as e:
                st.header(f"작성코드 에러: {str(e)}")