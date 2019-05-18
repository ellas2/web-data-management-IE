import requests 
import lxml.html 
import rdflib
from multiprocessing.dummy import Pool as ThreadPool
import threading, re

lock = '' # Define lock for sync
wiki_prefix = "http://en.wikipedia.org"
g = '' # main ontology graph
president = rdflib.URIRef(wiki_prefix + '/president')
prime_minister = rdflib.URIRef(wiki_prefix + '/prime_minister')
population = rdflib.URIRef(wiki_prefix + '/population')
area = rdflib.URIRef(wiki_prefix + '/area')
government = rdflib.URIRef(wiki_prefix + '/government')
capital = rdflib.URIRef(wiki_prefix + '/capital')
birth_date = rdflib.URIRef(wiki_prefix + '/birthDate')


def add_birth_date_information(graph, person, relation, url, xpath_query):
    new_res = requests.get(url)
    page = lxml.html.fromstring(new_res.content)
    info_bday_q = page.xpath(xpath_query)
    if len(info_bday_q) > 0:
        info_bday = info_bday_q[0].lstrip(' ').rstrip(' ').replace(' ', '_')
        info_bday = rdflib.Literal(info_bday, datatype=rdflib.XSD.date)
        with lock:
            graph.add((person, relation, rdflib.URIRef(wiki_prefix + "/" + info_bday)))

def add_country_info_to_ontology(graph, country, relation, page, xpath_query):
    info_country_q = page.xpath(xpath_query)
    if len(info_country_q) > 0:
        info_country = info_country_q[0].lstrip(' ').rstrip(' ').replace(' ', '_')
        if relation == area or relation == population:
            info_country = re.sub(r'[^\d,]', r'', info_country)
        entity_to_write = rdflib.URIRef(wiki_prefix + "/" + info_country)
        with lock:
            graph.add((country, relation, entity_to_write))
        return entity_to_write
    else:
        return None


def extract_country_info(objects):
    graph = objects[0]
    country_element = objects[1]
    country_url = country_element.xpath("@href") # Extract team url
    country_name_q = country_element.xpath("text()") # Extract team name
    if len(country_url) > 0 and len(country_name_q) > 0:
        new_url = wiki_prefix + country_url[0]
        country_name = country_name_q[0].lstrip(' ').rstrip(' ').replace(' ', '_')
        new_res = requests.get(new_url)
        country_page = lxml.html.fromstring(new_res.content)
        curr_country = rdflib.URIRef(wiki_prefix + "/" + country_name)
        add_country_info_to_ontology(graph, curr_country, capital, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[contains(th//text(),'Capital')]/td/a/text()")
        add_country_info_to_ontology(graph, curr_country, area, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[contains(th//text(),'Area')]/following-sibling::tr[1]/td/text()[1]")
        add_country_info_to_ontology(graph, curr_country, population, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[contains(th//text(),'Population')]/following-sibling::tr[1]/td/text()[1]")
        add_country_info_to_ontology(graph, curr_country, government, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[contains(th//text(),'Government')]/td//text()")
        president_entity = add_country_info_to_ontology(graph, curr_country, president, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[th//a/text() ='President']/td//a/@title")
        prime_minister_entity = add_country_info_to_ontology(graph, curr_country, prime_minister, country_page,
                                     "//table[contains(@class, 'infobox')]//tr[th//a/text() ='Prime Minister']/td//a/@title")

        country_president_url_q = country_page.xpath("//table[contains(@class, 'infobox')]//tr[th//a/text() ='President']/td//a/@href")
        if len(country_president_url_q) > 0 and president_entity:
            add_birth_date_information(graph, president_entity, birth_date, wiki_prefix + country_president_url_q[0],
                                     "//span[contains(@class,'bday')]/text()")

        country_prime_minister_url_q = country_page.xpath("//table[contains(@class, 'infobox')]//tr[th//a/text() ='Prime Minister']/td//a/@href")
        if len(country_prime_minister_url_q) > 0 and prime_minister_entity:
            add_birth_date_information(graph, prime_minister_entity, birth_date, wiki_prefix + country_prime_minister_url_q[0],
                                     "//span[contains(@class,'bday')]/text()")


# Extract all data about the countries
def extract_countries(countries_url, graph):
    res = requests.get(countries_url)
    doc = lxml.html.fromstring(res.content)
    countries_q = doc.xpath("//table[contains(caption/text(), 'Countries')]//tr/td[2][contains(span/@class,'flagicon')]/a")
    arr_for_multi = []
    for line in countries_q: #Iterate through all teams
        arr_for_multi.append((graph, line))
    pool = ThreadPool(5)
    results = pool.map(extract_country_info, arr_for_multi) # Use multi-thread to process all countries
    pool.close()
    pool.join() # Join all threads
    graph.serialize("ontology.nt", format="nt")

if __name__ == "__main__":
    g = rdflib.Graph()
    lock = threading.Lock()
    url = 'https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)'
    extract_countries(url, g)






