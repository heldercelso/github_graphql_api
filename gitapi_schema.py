from ariadne import ObjectType, QueryType, MutationType, gql, make_executable_schema
from ariadne.asgi import GraphQL
import requests, json

'''
# Steps to run this project:
# 1. create a venv and install the required libs: pip install -r requirements.txt (or install manually: ariadne, requests and uvicorn)
# 2. start the server: uvicorn gitapi_schema:app
# 3. open the browser at 127.0.0.1:8000
# 4. now it is ready to run the commands of this schema
'''

# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback
type_defs = gql("""
    type Query {
        user_repos(username: String!): [Repo_details]
        login(token: String!): Boolean
        rate_limit: String
    }
    type Repo_details {
        repo_field(field: String!): String
        repo_names: String
    }
    type Mutation {
        create_repo(token: String!, repo_name: String!): Boolean
    }
""")

# Map resolver functions to Query fields using QueryType
query = QueryType()
# Map resolver functions to custom type fields using ObjectType
query_repo_details = ObjectType("Repo_details")
# Mutation type to perform server-side modifications
mutation = MutationType()

# Header to http request
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': ''
}

# Resolvers are simple python functions

# This method does not implement a direct query, it is used by the others
@query.field("user_repos")
def resolve_user_repos(*_, username):
    request = requests.get(url='https://api.github.com/users/'+ username +'/repos', headers=headers)
    result = request.json()
    return result

# Query all repositories names of the specified user
# Usage: {user_repos(username:"some_username"){repo_names}}
@query_repo_details.field("repo_names")
def resolve_repo(user_repos, *_):
    if "full_name" in user_repos:
        return user_repos["full_name"]
    else:
        return user_repos

# Query a specific field in repositories of the specified user
# Usage: {user_repos(username:"some_username"){repo_field(field:"some_field")}}
@query_repo_details.field("repo_field")
def resolve_repo_details(user_repos, *_, field):
    request = requests.get(url='https://api.github.com/repos/'+ user_repos["full_name"], headers=headers)
    result = request.json()
    return result[field]

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

# Query just to login
# Usage: {login(token: "your_token")}
@query.field("login")
def resolve_login(*_, token):
    headers['Authorization'] = 'token ' + token

    request = requests.get('https://api.github.com/user', headers=headers)
    if request.status_code == 200:
        return True
    return False

# Mutation to create a repository
# Usage: mutation{create_repo(token:"your_token", repo_name: "some_repo_name")}
@mutation.field("create_repo")
def resolve_repo(*_, token, repo_name):
    data = {'name': repo_name}
    headers['Authorization'] = 'token ' + token

    request = requests.post(url='https://api.github.com/user/repos', data=json.dumps(data), headers=headers)
    if request.status_code == 201:
        return True
    return False

# Query to check requests remaining
# Usage: {rate_limit}
@query.field("rate_limit")
def resolve_rate_limit(*_):
    request = requests.get(url='https://api.github.com/rate_limit', headers=headers)
    result = request.json()
    return result["resources"]["core"]["remaining"]


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, [query, query_repo_details, mutation])

# Create an ASGI app using the schema
app = GraphQL(schema, debug=False)