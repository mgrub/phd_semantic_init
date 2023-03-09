import os

import owlready2 as owl
import owlready2.sparql.parser

owlready2.sparql.parser._DATA_PROPS = set()
owl.onto_path.append("ontologies")

# required ontologies
ontologies = [
    os.path.abspath("ontologies/scal.rdf"),
    os.path.abspath("ontologies/trans.rdf"),
]

# load the above listed rdf files
for path in ontologies:
    onto = owl.get_ontology("file://" + path).load()
    with onto:
        owl.sync_reasoner()

#owl.sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)
print(list(owl.default_world.inconsistent_classes()))


prefixes = """
PREFIX owl:        <http://www.w3.org/2002/07/owl#>
PREFIX rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema:     <https://schema.org/>
PREFIX om:         <http://www.ontology-of-units-of-measure.org/resource/om-2/>
PREFIX sosa:       <http://www.w3.org/ns/sosa/>
PREFIX ssn:        <http://www.w3.org/ns/ssn/>
PREFIX ssn-system: <http://www.w3.org/ns/ssn/systems/>
PREFIX scal:       <http://www.example.com/ns/scal/>
PREFIX trans:      <http://www.example.com/ns/trans/>
PREFIX si:         <https://ptb.de/si#>
"""

# evaluate OntoQA schema metrics 
onto_ns = "http://www.example.com/ns/scal/"



## Relationship Richness
### query number of class / subclass relations
query_SC = f'''
SELECT (SAMPLE(?s) AS ?subject) (COUNT(?o) as ?n_props)
WHERE {{
    ?s a/rdfs:subClassOf* ?o .
    FILTER(STRSTARTS(STR(?s), "{onto_ns}"))
}}
GROUP BY ?s
'''
res_sc = list(owl.default_world.sparql(prefixes + query_SC))

### query number of all relations
query_ALL = f'''
SELECT (SAMPLE(?s) AS ?subject) (COUNT(?o) as ?n_props)
WHERE {{
    ?s ?p ?o .
    FILTER(STRSTARTS(STR(?s), "{onto_ns}"))
}}
GROUP BY ?s
'''
res_all = list(owl.default_world.sparql(prefixes + query_ALL))

### calculate RR
### RR = P / (P + SC) = 1 - SC / (P + SC)    (tartir_2005, OntoQA paper)
SC = sum([item[1] for item in res_sc])
P_plus_SC = sum([item[1] for item in res_all])
RR = 1 - SC / P_plus_SC
print(RR)  # close to zero -> taxonomy alike, close to one -> 



## Attribute Richness
### query classes that are labeled
query_att = f'''
SELECT (SAMPLE(?s) AS ?subject) (COUNT(?att) as ?n_att)
WHERE {{
    {{
        ?s a owl:Class ;
        rdfs:comment ?att 
    }}
    UNION
    {{
        ?s a owl:Class ;
        rdfs:label ?att 
    }} .
    FILTER(STRSTARTS(STR(?s), "{onto_ns}")) 
}}
GROUP BY ?s
'''
res_att = list(owl.default_world.sparql(prefixes + query_att))

### query classes in onto_ns
query_C = f'''
SELECT DISTINCT ?s
WHERE {{
    ?s a owl:Class .
    FILTER(STRSTARTS(STR(?s), "{onto_ns}"))
}}
'''
res_c = list(owl.default_world.sparql(prefixes + query_C))

### calculate AR
att = sum([item[1] for item in res_att])
AR = len(res_att) / len(res_c)
print(AR)  # higher -> indicates higher quality of ontology



## Inheritance Richness
### query how many subclasses a class has
query_sum_H = f'''
SELECT (SAMPLE(?s1) AS ?subject) (COUNT(?s2) as ?n_subclasses)
WHERE {{
    ?s1 a owl:Class .
    ?s2 rdfs:subClassOf+ ?s1 .
    FILTER(STRSTARTS(STR(?s2), "{onto_ns}")) 
}}
GROUP BY ?s1
'''
res_sumH = list(owl.default_world.sparql(prefixes + query_sum_H))

### calculate IR
IRs = sum([item[1] for item in res_sumH]) / len(res_c)
print(IRs)  # lower -> more detailed ontology, higher -> more general knowledge
