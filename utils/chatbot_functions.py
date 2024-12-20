import re
import json
import pandasql as ps
from textwrap import dedent
import ast


def user_intent_detection(client, user_prompt, dataset_name, data_set_shape, columns_names, column_types, columns_categories):
    system_prompt = """
You are an intelligent assistant that analyzes user queries. Your task is to:
1. Determine whether the user query is a:
   - "Chitchat Question": If the user asks a question that does not relate to dataset analysis or data insights, such as greetings or general conversation.
   - "Dataset Analysis": If the user asks a question related to the dataset, including questions about its structure, contents, statistics, or any type of data insight, whether directly or indirectly phrased.
   
2. If the query is related to a "Dataset Analysis", further classify it as either:
   - "Graphical Request": If the user asks for a chart, plot, or any visual representation of the data.
   - "Textual Request": If the user asks for textual information, such as statistics, summaries, or detailed data insights.

3. You are provided with the following dataset information:
   - Dataset name: {}
   - Dataset shape: {}
   - Column names: {}
   - Column Types: {}
   - Column Categories (Ordinal, Nominal, Discrete, Continuous): {}

4. Your response should classify the query based on the information above and return the classification in the following JSON format:
   {{
       "query_type": "Chitchat Question" | "Dataset Analysis",
       "sub_type": "Graphical Request" | "Textual Request",
   }}

Please ensure that your classification is accurate, even if the user does not directly ask about the dataset but implies it in their query. For example, greetings or casual phrases like 'infos about the dataset' should be classified as "Dataset Analysis".

Respect the return JSON format.
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
    result = re.search(r'\{(.*?)\}', response.choices[0].message.content, re.DOTALL).group()
    try:
        return eval(result)
    except:
        return {"query_type": "Chitchat Question", "sub_type": None}


def text_query_processing(client, user_prompt, dataset_name, data_set_shape, columns_names, column_types, columns_categories):

    system_prompt = """
You are an intelligent assistant that analyzes user queries related to a dataset. Your task is to:
1. Determine whether the user query can be answered directly based on the provided dataset's column names, column types, and dataset name.
   - If the question asks for statistics (e.g., average, sum, count, etc.) or any other computations that require dataset values, generate a SQL query to retrieve the necessary data. make sure to include infos about ordinal or nominal columns (their categories) if needed.
   - If the question is asking about the structure of the dataset (e.g., column names or types), provide the details in a structured JSON response.
2. If the question cannot be answered directly based on the available dataset information:
   - Generate a SQL query that can be executed on the dataset and used to answer the question. Make sure to include info about ordinal or nominal columns (their categories) if needed.
3. You are provided with the following dataset:
   - Dataset name: {dataset_name}
   - Dataset shape: {data_set_shape}
   - Column names: {columns_str}
   - Column Types: {column_types_str}
   - Column Categories (Ordinal, Nominal, Discrete, Continuous): {columns_categories}

4. Return your response in the following JSON format:
   {{
       "can_answer_directly": true | false,
       "answer": "Direct answer and in markdown format, using idealy tables markdown. The response will be printed in a chat, so make a beautiful response format." | null,
       "sql_query": "SQL query if needed" | null,
       "can_answer_with_a_single_sql": true | false
   }}
   - If the question is asking for dataset details like column names, types, or structure, include that in the "answer" field as a markdown formatted string and make sure it is wrapped in proper JSON format.
   - The answer should be in JSON format so the markdown string should be compatible to be loaded in a string (for example, for line breaks use '\\n').
   - If the question need a sql query use 'df' as the name of the dataset. Be sure to respect sql syntax (for example, name of columns should be in double quotes).
   - Make sure the response is always formatted as valid JSON, including for dataset structure questions.
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

def sql_natural_response(client, user_prompt, sql_query, sql_result):
    system_prompt = """
You are an intelligent assistant that analyzes user queries related to a dataset. Your task is to:
1. Based on the user query and the SQL result, provide a natural language response to the user. Include the SQL query syntax in your response. Make sure to avoid abbreviations, omissions like '...' or '---', and provide a complete, clear, and coherent explanation.
2. If the question cannot be answered directly based on the available SQL result information:
   - Generate a natural language response to explain that the question cannot be answered based on the SQL result (include the SQL query generated for more context).
3. You are provided with the following dataset:
   - SQL result: {sql_result}
   - SQL query: {sql_query}

4. Return your response in the following format:
   {{
       "The natural language response in markdown format. The response should contain full results and not use abbreviations. Ensure a clear explanation of all the data without shortcuts."
   }}
If the question needs a SQL query, use 'df' as the name of the dataset. Be sure to respect SQL syntax for pandas dataframe query (for example, column names should be in double quotes).
The response will be printed in a chat, so make sure to format it beautifully, without any abbreviations or omissions.
Provide a complete and coherent response and do not use abbreviations, ellipses, or dashes for missing data.
""".format(sql_query=sql_query, sql_result=sql_result)

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
        
        if not detect_intent:
            return "Error occured while generating response."
        else:
            
            intent = detect_intent
            if intent["query_type"] == "Chitchat Question":
                return "I'm sorry, I can't answer general questions. Please ask a question related to the dataset."
            elif intent["query_type"] == "Dataset Analysis":
                if intent["sub_type"] == "Graphical Request":
                    return "I'm sorry, graphical requests are not supported yet."
                elif intent["sub_type"] == "Textual Request":
                    response = text_query_processing(client, user_prompt, dataset_name, data_set_shape,columns_names, column_types, columns_categories)
                    json_response = re.search(r'\{.*?\}', response, re.DOTALL)
                    if  not json_response:
                        return response
                    else:
                        json_string = json_response.group()
                        text_answer = json.loads(json_string)
                        if text_answer["can_answer_directly"]:  
                            return text_answer["answer"]
                        elif text_answer["can_answer_with_a_single_sql"]:
                            sql_query = text_answer["sql_query"]
                            try:
                                result = ps.sqldf(sql_query, {"df":df})
                            except:
                                error_message = dedent("""\
                                    ### Error occurred while executing SQL query needed to answer the question.
                                    ```sql
                                    {sql_query}
                                    ```
                                """.format(sql_query=sql_query))
                                return error_message
                                
                            final_sql_response = sql_natural_response(client, user_prompt, sql_query, result)
                            return  final_sql_response
                        else:
                            return text_answer["answer"]
                else:
                    return "I'm sorry, I can't answer your question."
            else:
                return "I'm sorry, I can't answer your question."
    except Exception as e: 
        return "Error occured while generating response."