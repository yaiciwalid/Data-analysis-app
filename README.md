# Data Analysis Platform (ongoing development)

![Screenshot from 2024-12-20 19-03-39](https://github.com/user-attachments/assets/228baad2-0ad4-43ce-acd9-1e1b04b8a5ea)


A comprehensive data analysis platform that enables users to import, transform, analyze, and model data for machine learning projects. A new chatbot feature now allows querying and analyzing the dataset in natural language, making the platform more intuitive for users.

## Description

This platform provides a suite of tools to streamline the data analysis process, from data import and transformation to training and testing machine learning models. A new chatbot feature allows users to interact with the data using natural language queries, making it more accessible for non-technical users.

## Features

* **Data Import**: Import data from various sources, including CSV, Excel, and databases.
* **Data Transformation**: Transform and preprocess data to prepare it for machine learning algorithms.
* **Intelligent Chatbot**: Query and analyze data using natural language:
  * Describe me the dataset.
  * Propose me a data analysis process.
  * Average column1 group by column2.
* **Univariate Analysis**: Perform univariate analysis to understand the distribution of individual variables.
* **Bivariate Analysis**: Perform bivariate analysis to understand the relationships between pairs of variables.
* **Machine Learning**: Train and test machine learning models using various algorithms, including classification, regression, clustering, and more.

## Technologies Used

* Python
* Dash
* Pandas
* Plotly
* Scikit-learn
* LLM API


## Installation

To install and run this project, follow these steps:

1. Clone the repository: `git clone https://github.com/yaiciwalid/Data-analysis-app.git`
2. Create a virtual environment: `python -m venv env`
3. Activate the virtual environment: `source env/bin/activate` (Linux/Mac) or `env\Scripts\activate` (Windows)
4. Install the requirements: `pip install -r requirements.txt`
5. Run the application: `python app.py`

## Usage

Once the application is running, you can access it in your web browser at `http://localhost:8050`.

## Contributing

If you would like to contribute to this project, please follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/my-feature`
3. Make your changes and commit them: `git commit -am 'Add my feature'`
4. Push to your fork: `git push origin feature/my-feature`
5. Submit a pull request
