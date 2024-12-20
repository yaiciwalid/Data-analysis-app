import re
import json
import pandasql as ps


def user_intent_detection(client, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories):
    system_prompt = """
You are an intelligent assistant that analyzes user queries. Your task is to:
1. Determine whether the user query is a "General Question" or related to a dataset ("Dataset Analysis").
2. If the query is related to a dataset, further classify it as either:
   - "Graphical Request": If the user asks for a chart, plot, or visual representation.
   - "Textual Request": If the user asks for statistics, summaries, or textual data insights.

3. You are provided with the following dataset informations:
   - Dataset name: {}
   - Dataset shape: {}
   - Column names: {}
   - Column Types: {}
   - Column Categories (Ordinal, Nominal, Discrete, Continuous): {}


4. Always return your response in the following JSON format:
   {{
       "query_type": "General Question" | "Dataset Analysis",
       "sub_type": "Graphical Request" | "Textual Request" | null,
   }}

Please ensure that your analysis is based on the informations about the dataset provided, including the column names and their types.
""".format(dataset_name, data_set_shape, columns_names, column_types, columns_categories)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content


def text_query_processing(client, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories):


    system_prompt = """
You are an intelligent assistant that analyzes user queries related to a dataset. Your task is to:
1. Determine whether the user query can be answered directly based on the provided dataset's column names, column types, and dataset name.
   - If the question asks for statistics (e.g., average, sum, count, etc.) or any other computations that require dataset values, generate a SQL query to retrieve the necessary data.
   - If the question is asking about the structure of the dataset (e.g., column names or types), you can provide a direct answer without the need for SQL.
2. If the question cannot be answered directly based on the available dataset information:
   - Generate a SQL query that can be executed on the dataset and used to answer the question.
3. You are provided with the following dataset:
   - Dataset name: {dataset_name}
   - Dataset shape: {data_set_shape}
   - Column names: {columns_str}
   - Column Types: {column_types_str}
   - Column Categories (Ordinal, Nominal, Discrete, Continuous): {columns_categories}

4. Return your response in the following format:
   {{
       "can_answer_directly": true | false,
       "answer": "Direct answer if possible" | null,
       "sql_query": "SQL query if needed" | null,
       "can_answer_with_sql": true | false,
   }}
If the question need a sql query use 'df' as the name of the dataset. Be sure to respect sql syntax (for example, name of columns should be in double quotes).
""".format(dataset_name=dataset_name, data_set_shape=data_set_shape, columns_str=columns_names, column_types_str=column_types, columns_categories=columns_categories)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content

def sql_natural_response(client, user_prompt, sql_query,sql_result):
    system_prompt = """
You are an intelligent assistant that analyzes user queries related to a dataset. Your task is to:
1. Based on user query and the SQL result, provide a natural language response to the user.
2. If the question cannot be answered directly based on the available SQL result information:
   - Generate a natural language response to say that the question cannot be answered based on the SQL result (include the sql query generated for more context).
3. You are provided with the following dataset:
   - sql result: {sql_result}
   - sql query: {sql_query}

4. Return your response in the following format:
   {{
       "answer": "the natural language response"
   }}
If the question need a sql query use 'df' as the name of the dataset. Be sure to respect sql syntax (for example, name of columns should be in double quotes).
""".format(sql_query=sql_query,sql_result=sql_result)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content


def response(client, df, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories):
    
    try:
        detect_intent = user_intent_detection(client, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories)
        extractedintent = re.search(r'\{.*?\}', detect_intent, re.DOTALL)
        
        if not extractedintent:
            return "Error occured while generating response."
        else:
            json_string = extractedintent.group()
            intent = json.loads(json_string)
            if intent["query_type"] == "General Question":
                return "I'm sorry, I can't answer general questions. Please ask a question related to the dataset."
            elif intent["query_type"] == "Dataset Analysis":
                if intent["sub_type"] == "Graphical Request":
                    return "I'm sorry, graphical requests are not supported yet."
                elif intent["sub_type"] == "Textual Request":
                    response = text_query_processing(client, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories)
                    json_response = re.search(r'\{.*?\}', response, re.DOTALL)
                    if  not json_response:
                        return "Error occured while generating response."
                    else:
                        json_string = json_response.group()
                        text_answer = json.loads(json_string)
                        if text_answer["can_answer_directly"]:  
                            return text_answer["answer"]
                        elif text_answer["can_answer_with_sql"]:
                            print("hhhhhh")
                            sql_query = text_answer["sql_query"]
                            print(sql_query)
                            result = ps.sqldf(sql_query, {"df":df})
                            final_sql_response = sql_natural_response(client, user_prompt, sql_query, result)
                            json_response = re.search(r'\{.*?\}', final_sql_response, re.DOTALL)
                            if  not json_response:
                                return "Error occured while generating response."
                            else:
                                json_string = json_response.group()
                                text_answer = json.loads(json_string)
                            return text_answer["answer"]
                        return "Implementation in process."
                else:
                    return "I'm sorry, I can't answer your question."
            else:
                return "I'm sorry, I can't answer your question."
    except Exception as e: 
        print("kkkkkkk")
        return "Error occured while generating response."