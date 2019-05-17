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

q_a = "select DISTINCT ?a where { ?a <http://example.org/prime_minister> ?country }"

q_b = "select ?country where {  }"


q_c = "select ?country where { ?country <http://example.org/government> ?b." \
      "filter (contains(str(?b), republic)) }"

q_d = "select ?country where { ?country <http://example.org/government> ?b." \
      "filter (contains(str(?b), monarchy)) }"

graph = rdflib.Graph()
run_query(graph, q_a, '1')
run_query(graph, q_b, '2')
run_query(graph, q_c, '3')
run_query(graph, q_d, '4')