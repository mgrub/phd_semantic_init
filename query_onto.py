import owlready2 as owl


owl.onto_path.append("ontologies")


scal = owl.get_ontology("file:ontologies/scal.rdf").load()
with scal:
    owl.sync_reasoner()

ex = owl.get_ontology("file:ontologies/rdf_example.rdf").load()
with ex:
    owl.sync_reasoner()

#owl.sync_reasoner_pellet(infer_property_values = True, infer_data_property_values = True)
print(list(owl.default_world.inconsistent_classes()))



prefixes = """
PREFIX  om:    <http://www.ontology-of-units-of-measure.org/resource/om-2/>
PREFIX  sosa:  <http://www.w3.org/ns/sosa/>
PREFIX  ssn:   <http://www.w3.org/ns/ssn/>
PREFIX  dsi:   <http://www.example.com/ns/dsi/>
PREFIX  scal:  <http://www.example.com/ns/scal/>
PREFIX  ex:    <http://www.example.com/ns/example/>
"""

query = """
SELECT ?s ?prop
WHERE {
    ?s a/rdfs:subClassOf* sosa:Sensor .
    ?s ssn:hasProperty ?prop .
    ?prop a/rdfs:subClassOf* scal:CalibrationModel .
    ?s sosa:isHostedBy ex:location_A .
    ?s sosa:observes ex:acceleration_z
}
"""


res = owl.default_world.sparql(prefixes + query)
print(list(res))
