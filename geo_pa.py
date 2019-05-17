import re
import sys

ONTOLOGY_PREFIX = 'http://example.org/'

# Regex for the queries
WHO_PATTERN = "^who is the (?P<relation>[\w -.]+)of (?P<entity>[\w -.]+)\?*$"
WHO_PATTERN2 = "^who is (?P<entity>[\w -.]+)\?*$"
WHAT_PATTERN = "^what is the (?P<relation>[\w -.]+)of (?P<entity>[\w -.]+)\?*$"
WHEN_PATTERN = "^when was the (?P<relation>[\w -.]+)of (?P<entity>[\w -.]+) born\?*$"

ENTITY_GROUP = "entity"
RELATION_GROUP = "relation"
NO_RELATION = "no_relation"

# Pattern values for the queries
WHO = 1
WHO_2 = 2
WHAT = 3
WHEN = 4
INVALID = -1


def create_sparql_query(entity, relation):
    entity = entity.lower()
    entity_lst = entity.split()
    entity_for_query = "_"
    entity_for_query = entity_for_query.join(entity_lst)
    print("entity_for_query: " + entity_for_query)
    relation_lst = relation.split()
    relation_for_query = "_"
    relation_for_query = relation_for_query.join(relation_lst)
    print("relation_for_query: " + relation_for_query)





class Query():
    entity = ""
    relation = ""
    pattern = None

    def __init__(self, query, who_regex, who_regex2, what_regex, when_regex):
        if who_regex.match(query):
            self.pattern = WHO
            match = who_regex.match(query)
        elif who_regex2.match(query):
            self.pattern = WHO_2
            match = who_regex2.match(query)
        elif what_regex.match(query):
            self.pattern = WHAT
            match = what_regex.match(query)
        elif when_regex.match(query):
            self.pattern = WHEN
            match = when_regex.match(query)
        else:
            self.pattern = INVALID

        # Get the relation and entity from the query
        if self.pattern is WHO_2:
            print("pattern is: " + str(self.pattern))
            self.entity = match.group(ENTITY_GROUP)
            print(self.entity)
            self.relation = NO_RELATION
        elif self.pattern is not INVALID:
            print("pattern is: " + str(self.pattern))
            self.entity = match.group(ENTITY_GROUP)
            print("entity: " + self.entity)
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
    reg_expressions = compile_reg_expressions([WHO_PATTERN, WHO_PATTERN2, WHAT_PATTERN, WHEN_PATTERN])
    [who_regex, who_regex2, what_regex, when_regex] = reg_expressions

    query = Query(query_str, who_regex, who_regex2, what_regex, when_regex)
    if query.pattern is INVALID:
        print("Unable to handle query: " + query_str)
        print("Can only handle queries of the form:")
        print("Who is the president of <country>?")
        print("Who is the president/prime minister/ of <country>?")
        print("What is the population/area/government/capital of <country>?")
        print("When was the president/prime minister of <country> born?")
        print("Who is <entity>?")
        return None

    entity = query.entity
    relation = query.relation
    create_sparql_query(entity,relation)


query_str = " ".join(sys.argv[1:])

__main__(query_str)
