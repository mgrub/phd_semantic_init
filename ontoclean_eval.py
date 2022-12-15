import os

import owlready2 as owl
import owlready2.sparql.parser

owlready2.sparql.parser._DATA_PROPS = set()
owl.onto_path.append("ontologies")

# required ontologies
ontologies = [
    os.path.abspath("ontologies/ontoclean-dl.owl"),
    os.path.abspath("ontologies/scal_punned.rdf"),
    #os.path.abspath("ontologies/trans.rdf"),
]

# load the above listed rdf files
for path in ontologies:
    onto = owl.get_ontology("file://" + path).load()
    with onto:
        owl.sync_reasoner()

#owl.sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)
print(list(owl.default_world.inconsistent_classes()))

query = """
PREFIX ontoclean: <http://www.meteck.org/teaching/ontologies/ontoclean-dl/>

SELECT ?s ?o
WHERE {
    ?s ontoclean:hasSubClass ?o 
}
"""

res = owl.default_world.sparql(query)
for item in list(res):
    print(item)
