import rdflib


def run_query(graph, query, query_num):
    graph.parse("ontology.nt", format="nt")
    x1 = graph.query(query)
    print ('query ' + query_num + ' results:')
    for row in x1:
        print (row)

# All prime ministers
q_a = "select (count(?a) AS ?triples) where { ?country <http://en.wikipedia.org/prime_minister> ?a }"

# All countries
q_b = "select (count(?country) AS ?triples) where { ?country <http://en.wikipedia.org/country> ?country }"
#TODO: this should maybe be changed

# All countries that are republics
q_c = "select (count(?country) AS ?triples) where { ?country <http://en.wikipedia.org/government> ?b." \
      "FILTER (contains(str(?b), \"republic\")) }"

# All countries that are monarchies
q_d = "select (count(?country) AS ?triples) where { ?country <http://en.wikipedia.org/government> ?b." \
      "FILTER (contains(str(?b), \"monarchy\")) }"

graph = rdflib.Graph()
run_query(graph, q_a, '1')
run_query(graph, q_b, '2')
run_query(graph, q_c, '3')
run_query(graph, q_d, '4')