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

## Execution instructions for dockerized app:

Pre-requisits to know:
- The main script runs an enrichment process that uses AI to provide a description of each book more details available [here](/helpers/hugging_face/hugging_face_test_notebook.ipynb). This means that you must have a `.env` file located in `/dockerized_script/.env` which contains the API key. A sample of this is provided at `/dockerized_script/.sample.env`.

- You must have an API token, you can get one for free:
    1. Go to https://huggingface.co/settings/tokens
    2. Create a Read token

Steps to follow after pre-requisits:
1. `cd dockerized_script` - Move to the correct directory
2. `docker compose build library_cleanser` - This will build the container for the main script, the container will be called library_cleanser
3. `docker compose run --rm library_cleanser` - This will run the main script container (Note that an env file is required for the AI_API_KEY as per pre-req section)
4. `docker compose build sqlite_web` - This will build the container for the sqlite web app
5. `docker compose run --rm --service-ports sqlite_web` - This will run the sqlite web app whilst keeping the service ports that were defined in the compose yaml file. Available at localhost:8080
6. `docker compose build streamlit` - This will build the streamlit application
7. `docker compose run --rm --service-ports streamlit` - This will run the streamlit web app.  Available at localhost:8502