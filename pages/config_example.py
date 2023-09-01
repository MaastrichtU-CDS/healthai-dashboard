# config.py

# Central server
server_url = "http://localhost"
server_port = 5000
server_api = "/api"
privkey_path = None

# Credentials
username = "username"
password = "password"

# Collaboration
collaboration = 1
org_ids = [2, 3]

# Input for statistics
image_stat = 'ghcr.io/maastrichtu-cds/v6-healthai-dashboard-py:latest'
cutoff = 730
delta = 30

# Input for similarity
image_sim = 'ghcr.io/maastrichtu-cds/v6-healthai-patient-similarity-py:latest'
k = 4
epsilon = 0.01
max_iter = 50
columns = ['t', 'n', 'm']
