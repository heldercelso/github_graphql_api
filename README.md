## Introduction

This mini project creates a GraphQL API using Ariadne and requests libraries.
It aims to consume the official Github API to create new responses.


## Steps to run this project:

1. Create a venv and install the required libs: pip install -r requirements.txt (or install manually: ariadne, requests and uvicorn);
2. Start the server using the command: uvicorn gitapi_schema:app;
3. Open the browser at 127.0.0.1:8000;
4. Now it is ready to run the commands of this schema.

### Commands examples:

1. `{rate_limit}`:

Check your remaining requests to Github API.
PS: Without login you can request 60/hour, if logged then it is 5000/hour (`https://docs.github.com/pt/rest/overview/resources-in-the-rest-api#rate-limiting`).

2. `{login(token: "your_token")}`:

To login it is necessary to create an Oauth token: `https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token`

PS: It is necessary to be made manually because it is not possible to create Oauth tokens using Github API anymore: `https://docs.github.com/pt/enterprise-server@3.5/rest/oauth-authorizations#create-a-new-authorization`

3. `{user_repos(username:"heldercelso"){repo_names}}`:

It is listing the names of all repositories of the user heldercelso

4. `{user_repos(username:"heldercelso"){repo_field(field:"language")}}`:

It is listing all programming languages of each repository of the user heldercelso

5. `mutation{create_repo(token:"your_token", repo_name: "New_repo_name")}`:

It will create a repository named 'New_repo_name' for the user of the token.


## Putting in production:

It is necessary to attach the web server (wsgi or asgi) to the graphql schema.

### Example for Django:

It will be necessary to modidy your `wsgi.py` file to connect to both: first your web server and second to the graphql.

- Default configuration:
    * Code:
        ```django_application = get_wsgi_application()```
    * Gunicorn command:
        ```gunicorn wsgi:application```

- Changing to include this API:
    * Code:
        ```
        django_application = get_wsgi_application()
        graphql_application = GraphQL(schema)
        application = GraphQLMiddleware(django_application, graphql_application)
        ```
    * Gunicorn command (same as before):
        ```gunicorn wsgi:application```

