import rdflib


def run_query(graph, query, query_num):
    graph.parse("ontology.nt", format="nt")
    x1 = graph.query(query)
    print ('query ' + query_num + ' results:')
    count = 0
    for row in x1:
        print (row)
        count+=1
    print('num rows is ' + count)

# All prime ministers
q_a = "select DISTINCT (?a) where { ?a <http://example.org/prime_minister> ?country }"

# All countries
q_b = "select ?country where { ?country <http://example.org/area> ?b }"
#TODO: this should maybe be changed

# All countries that are republics
q_c = "select ?country where { ?country <http://example.org/government> ?b." \
      "FILTER (contains(str(?b), republic)) }"

# All countries that are monarchies
q_d = "select ?country where { ?country <http://example.org/government> ?b." \
      "FILTER (contains(str(?b), monarchy)) }"

graph = rdflib.Graph()
run_query(graph, q_a, '1')
run_query(graph, q_b, '2')
run_query(graph, q_c, '3')
run_query(graph, q_d, '4')