import re
import sys
import rdflib

ONTOLOGY_PREFIX = 'http://example.org/'

# Regexps for the queries
WHO_P = "^who is (?P<entity>[\w -.]+)\?*$"
WHO_PRS_P = "^who is the president of (?P<entity>[\w -.]+)\?*$"
WHO_PM_P = "^who is the prime minister of (?P<entity>[\w -.]+)\?*$"
WHAT_POP_P = "^what is the population of (?P<entity>[\w -.]+)\?*$"
WHAT_CAP_P = "^what is the capital of (?P<entity>[\w -.]+)\?*$"
WHAT_AR_P = "^what is the area of (?P<entity>[\w -.]+)\?*$"
WHAT_GOV_P = "^what is the government of (?P<entity>[\w -.]+)\?*$"
WHEN_PRS_P = "^when was the president of (?P<entity>[\w -.]+) born\?*$"
WHEN_PM_P = "^when was the prime minister of (?P<entity>[\w -.]+) born\?*$"

ENTITY_GROUP = "entity"
#RELATION_GROUP = "relation"
NO_RELATION = "no_relation"

# Pattern values for the queries
WHO = 1
WHO_PRES = 2
WHO_PM = 3
WHAT_POP = 4
WHAT_CAP = 5
WHAT_AREA = 6
WHAT_GOV = 7
WHEN_PRES = 8
WHEN_PM = 9
INVALID = -1


def run_sparql_query(graph, sparql_query):
    graph.parse("ontology.nt", format="nt")
    x1 = graph.query(query)
    print ('results:')


def create_sparql_query(query):
    entity = query.entity.lower()
    relation = query.relation
    entity = entity.lower()
    entity_lst = entity.split()
    entity_for_query = "_"
    entity_for_query = entity_for_query.join(entity_lst)
    print("entity_for_query: " + entity_for_query)
    relation_lst = relation.split()
    relation_for_query = "_"
    relation_for_query = relation_for_query.join(relation_lst)
    print("relation_for_query: " + relation_for_query)
    if query.pattern is WHO:
        sparql_query = ' '
        #TODO: TBD
    elif query.pattern is WHO_PRES:
        sparql_query = 'select DISTINCT ?a where { ?a <http://example.org/president> <' + ONTOLOGY_PREFIX + entity + '> }'
    elif query.pattern is WHO_PM:
        sparql_query = 'select DISTINCT ?a where { ?a <http://example.org/prime_minister> <' + ONTOLOGY_PREFIX + entity + '> }'
    elif query.pattern is WHAT_POP:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/population> ?a }'
    elif query.pattern is WHAT_CAP:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/capital> ?a }'
    elif query.pattern is WHAT_AREA:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/area> ?a }'
    elif query.pattern is WHAT_GOV:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/government> ?a }'
    elif query.pattern is WHEN_PRES:
        sparql_query = 'select ?b where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/president> ?a.' \
                        ' ?a <http://example.org/birth_date> ?b}'
    elif query.pattern is WHEN_PM:
        sparql_query = 'select ?b where { <' + ONTOLOGY_PREFIX + entity + '> <http://example.org/prime_minister> ?a.' \
                        ' ?a <http://example.org/birth_date> ?b}'

    return sparql_query



class Query():
    entity = ""
    relation = ""
    pattern = None

    def __init__(self, query, who_reg, who_president_reg, who_prime_min_reg,\
                 what_pop_reg, what_cap_reg, what_area_reg, what_gov_reg,\
                 when_president_reg, when_prime_min_reg):
        if who_president_reg.match(query):
            self.pattern = WHO_PRES
            match = who_president_reg.match(query)
            self.relation = "president"
        elif who_prime_min_reg.match(query):
            self.pattern = WHO_PM
            match = who_prime_min_reg.match(query)
            self.relation = "prime minister"
        elif who_reg.match(query):
            self.pattern = WHO
            match = who_reg.match(query)
        elif what_pop_reg.match(query):
            self.pattern = WHAT_POP
            match = what_pop_reg.match(query)
            self.relation = "population"
        elif what_cap_reg.match(query):
            self.pattern = WHAT_CAP
            match = what_cap_reg.match(query)
            self.relation = "capital"
        elif what_area_reg.match(query):
            self.pattern = WHAT_AREA
            match = what_area_reg.match(query)
            self.relation = "area"
        elif what_gov_reg.match(query):
            self.pattern = WHAT_GOV
            match = what_gov_reg.match(query)
            self.relation = "government"
        elif when_president_reg.match(query):
            self.pattern = WHEN_PRES
            match = when_president_reg.match(query)
            self.relation = "president"
        elif when_prime_min_reg.match(query):
            self.pattern = WHEN_PM
            match = when_prime_min_reg.match(query)
            self.relation = "prime minister"
        else:
            self.pattern = INVALID

        # Get the relation and entity from the query
        if self.pattern is WHO:
            print("pattern is: " + str(self.pattern))
            self.entity = match.group(ENTITY_GROUP)
            print(self.entity)
            self.relation = NO_RELATION
        elif self.pattern is not INVALID:
            print("pattern is: " + str(self.pattern))
            self.entity = match.group(ENTITY_GROUP)
            print("entity: " + self.entity)
            '''
            self.relation = match.group(RELATION_GROUP)
            rel = self.relation
            rel = normalize_query(rel)
            print("relation: " + self.relation)
            if self.pattern is WHEN or self.pattern is WHO:
                if rel != "president" and rel != "prime minister":
                    print("I am here")
                    self.pattern = INVALID
            elif self.pattern is WHAT:
                if rel != "area" and rel != "government" and rel != "capital":
                    self.pattern = INVALID
            '''


def compile_reg_expressions(patterns):
    expressions = []
    if int(sys.version[2]) < 6:
        for pattern in patterns:
            expressions.append(re.compile(pattern, re.IGNORECASE))
    else:
        from re import RegexFlag
        for pattern in patterns:
            expressions.append(re.compile(pattern, RegexFlag.IGNORECASE))
    return expressions


def normalize_query(query):
    if query is None:
        return query
    query = " ".join(query.split())
    return query


def __main__(query_str):
    query_str = normalize_query(query_str)
    reg_expressions = compile_reg_expressions([WHO_P, WHO_PRS_P, WHO_PM_P, \
                                               WHAT_POP_P, WHAT_CAP_P, WHAT_AR_P, WHAT_GOV_P, \
                                               WHEN_PRS_P, WHEN_PM_P])

    [who_reg, who_president_reg, who_prime_min_reg, what_pop_reg, what_cap_reg,\
     what_area_reg, what_gov_reg, when_president_reg, when_prime_min_reg] = reg_expressions

    query = Query(query_str, who_reg, who_president_reg, who_prime_min_reg, what_pop_reg, what_cap_reg,\
     what_area_reg, what_gov_reg, when_president_reg, when_prime_min_reg)
    if query.pattern is INVALID:
        print("Unable to handle query: " + query_str)
        print("Can only handle queries of the form:")
        print("Who is the president of <country>?")
        print("Who is the president/prime minister/ of <country>?")
        print("What is the population/area/government/capital of <country>?")
        print("When was the president/prime minister of <country> born?")
        print("Who is <entity>?")
        return None
    #graph = rdflib.Graph()
    sparql_query = create_sparql_query(query)
    #run_sparql_query(graph, sparql_query)


query_str = " ".join(sys.argv[1:])
__main__(query_str)
