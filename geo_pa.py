import re
import sys
import rdflib

ONTOLOGY_PREFIX = 'http://en.wikipedia.org/'

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

def extract_from_query_result(query_result_row):
    query_result_row_str = str(query_result_row)
    query_result_row_str = query_result_row_str.split('/')
    query_result_row_str[3] = query_result_row_str[3].split('\'')
    str_query = query_result_row_str[3][0]
    str_query = str_query.replace("_"," ")
    return str_query


def reply_to_user(query, query_results_1, num_results_1, query_results_2, num_results_2):
    reply_str = ""
    if query.pattern is WHO:
        if num_results_1 == 0:
            reply_str += "Prime minister of "
            for query_result_row in query_results_2:
                curr_reply_str = extract_from_query_result(query_result_row)
                reply_str += curr_reply_str
                reply_str += ", "
        elif num_results_2 == 0:
            reply_str += "President of "
    if query.pattern is not WHO or num_results_2 == 0:
        for query_result_row in query_results_1:
            curr_reply_str = extract_from_query_result(query_result_row)
            reply_str += curr_reply_str
            reply_str += ", "
    reply_str = reply_str[:-2]
    if query.pattern is WHAT_AREA:
        reply_str += " km2"
    print(reply_str)
    return reply_str


def run_sparql_query(graph, sparql_query):
    cnt = 0
    graph.parse("ontology.nt", format="nt")
    x1 = graph.query(sparql_query)
    #print ('results:')
    for row in x1:
        #print(row)
        cnt += 1
    return [x1, cnt]


def create_sparql_query(query):
    entity = query.entity
    relation = query.relation
    entity_lst = entity.split()
    entity_for_query = "_"
    entity_for_query = entity_for_query.join(entity_lst)
    if query.pattern is WHO:
        sparql_query_pres = 'select ?a where { ?a <http://en.wikipedia.org/president> <' + ONTOLOGY_PREFIX + entity_for_query + '> }'
        sparql_query_pm = 'select ?a where { ?a <http://en.wikipedia.org/prime_minister> <' + ONTOLOGY_PREFIX + entity_for_query + '> }'
        return [sparql_query_pres, sparql_query_pm]
    elif query.pattern is WHO_PRES:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/president> ?a }'
    elif query.pattern is WHO_PM:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/prime_minister> ?a  }'
    elif query.pattern is WHAT_POP:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/population> ?a }'
    elif query.pattern is WHAT_CAP:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/capital> ?a }'
    elif query.pattern is WHAT_AREA:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/area> ?a }'
    elif query.pattern is WHAT_GOV:
        sparql_query = 'select ?a where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/government> ?a }'
    elif query.pattern is WHEN_PRES:
        sparql_query = 'select ?b where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/president> ?a.' \
                        ' ?a <http://en.wikipedia.org/birthDate> ?b}'
    elif query.pattern is WHEN_PM:
        sparql_query = 'select ?b where { <' + ONTOLOGY_PREFIX + entity_for_query + '> <http://en.wikipedia.org/prime_minister> ?a.' \
                        ' ?a <http://en.wikipedia.org/birthDate> ?b}'

    return [sparql_query, sparql_query]



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
            self.entity = match.group(ENTITY_GROUP)
            self.relation = NO_RELATION
        elif self.pattern is not INVALID:
            self.entity = match.group(ENTITY_GROUP)



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
    #TODO: merge files
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
    graph = rdflib.Graph()
    [sparql_1, sparql_2] = create_sparql_query(query)
    [query_results_1, num_results_1] = run_sparql_query(graph, sparql_1)
    if query.pattern is WHO:
        [query_results_2, num_results_2] = run_sparql_query(graph, sparql_2)
        return reply_to_user(query, query_results_1, num_results_1, query_results_2, num_results_2)
    return reply_to_user(query, query_results_1, num_results_1, None, 0)


query_str = " ".join(sys.argv[1:])
__main__(query_str)
