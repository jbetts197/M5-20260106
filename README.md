# M5-20260106

**Brief:** 
A library wants to improve their current quality analysis. They are looking for an automated way of cleaning and filtering data.
- Create User Story
- Create Architecture Diagram
- Create Project Plan / KanBan Board

**User Story:**
- A customer borrows a book
- A customer returns a book
- A customer has an allocated amount of time allowed to borrow the book

**Repo structure:**
- `Diagrams` directory stores infrastructure and kanban diagrams
- `Helpers` directory stores helper files to understand libraries
- `Juypter_notebooks` directory has the notebooks used to describe cleansing/transformations
- `main_scripts` directory has scripts which perform the cleansing as a script, also contains unittesting
- `Output_cleansed_data` directory has the cleansed and enriched data outputted from `main_scripts'
- `dockerized_script` directory contains a dockerized version of the main script. see execution instructions below on how to use.

**Execution instructions:**

- Pre-req, you must have an API token, you can get one for free:
    1. Go to https://huggingface.co/settings/tokens
    2. Create a Read token

- Pre-req, you must have some libraries installed in your venv, from the root directory run:
`pip install -r requirements.txt`

- To execute the main script, run the following command from the `main_scripts` directory (note that currently the book description enrichment stage takes approx 2-3 mins, and the ai_api_key should be provided):
`python .\cleanse_library_data.py --customers-input "./raw_data/03_Library SystemCustomers.csv" --customers-output "./output_cleansed_data/cleansed_system_customers.csv" --ai_api_key "hf_XXXX"`

- To execute the tests, run the following command from the `main_scripts` directory:
- `$env:AI_API_KEY="sk-xxxx"` (to set API key variable)
- `python unittest_functions.py`

- To run the juypter notebook that demos hugging face, you will require a .env file with the `AI_API_KEY`. This can be set by configuring `.vscode/settings.json`. These files have been excluded from git using gitignore.

- To run example docker, use the following command:
`docker run --rm -v ${PWD}/data:/data myfirstcontainer --number1 6 --number2 7`

- To run main script dockerized, do the following:
1. `cd dockerized_script` - move to the correct directory
2. `docker compose build library_cleanser` - this will build the container for the main script, the container will be called library_cleanser
3. `docker compose run --rm library_cleanser` - this will run the main script container (note that a .env file is required for the AI_API_KEY)
4. `docker compose build sqlite_web` - this will build the container for the sqlite web app
5. `docker compose run --rm --service-ports sqlite_web` - this will run the sqlite web app whilst keeping the service ports that were defined in the compose yaml file.