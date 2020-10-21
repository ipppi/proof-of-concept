from importlib.resources import path

with path('ipppi_proof_of_concept.static', 'register.html') as p:
    with open(p) as f: register_html = f.read()

with path('ipppi_proof_of_concept.static', 'login.html') as p:
    with open(p) as f: login_html = f.read()
