import owlready2 as owl
import glob
import os

owl.onto_path.append("ontologies")

# required ontologies
ontologies = [
    os.path.abspath("ontologies/scal.rdf"),
    os.path.abspath("ontologies/trans.rdf"),
]

# sensor self descriptions of interest
example_sensors = [
    os.path.abspath("example_sensors/sensor_1.rdf"),
    os.path.abspath("example_sensors/sensor_2.rdf"),
    os.path.abspath("example_sensors/sensor_3.rdf"),
    os.path.abspath("example_sensors/sensor_4.rdf"),
    os.path.abspath("example_sensors/sensor_5.rdf"),
    os.path.abspath("example_sensors/sensor_6.rdf"),
]

# load the above listed rdf files
for path in ontologies + example_sensors:
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

PREFIX  local:    <http://www.example.com/ns/local/>
PREFIX  sensor_1: <http://www.example.com/ns/S1/>
PREFIX  sensor_2: <http://www.example.com/ns/S2/>
PREFIX  sensor_3: <http://www.example.com/ns/S3/>
PREFIX  sensor_4: <http://www.example.com/ns/S4/> 
PREFIX  sensor_5: <http://www.example.com/ns/S5/>
PREFIX  sensor_6: <http://www.example.com/ns/S6/>
"""

query_same_location = """
SELECT ?s
WHERE {{
    ?s sosa:isHostedBy ?l1 .
    {TARGET} sosa:isHostedBy ?l2 .
    FILTER( SAMETERM(?l1, ?l2) && !SAMETERM(?s, {TARGET}) )
}}
"""

    # FILTER( ?l1 = ?l2 ) .
    # FILTER( ?s != {TARGET} )

query_same_observable_property = """
SELECT ?s
WHERE {{
    {TARGET} sosa:observes ?m1 .
    ?s sosa:observes ?m2 .
    FILTER( SAMETERM(?m1, ?m2) && !SAMETERM(?s, {TARGET}) )
}}
"""

query_same_observed_quantity = """
SELECT DISTINCT ?s
WHERE {{
    {TARGET} sosa:observes ?m1 .
    ?s sosa:observes ?m2 .
    ?m1 om:hasDimension ?d1 .
    ?m2 om:hasDimension ?d2 .
    FILTER( SAMETERM(?d1, ?d2) && !SAMETERM(?s, {TARGET}) )
}}
"""

query_calibrated_sensors = """
SELECT ?s
WHERE {
    ?s a/rdfs:subClassOf* sosa:Sensor ;
        ssn:hasProperty ?prop .
    ?prop a/rdfs:subClassOf* scal:CalibrationModel .
}
"""

query_valid_calibrated_sensors = """
SELECT ?s
WHERE {
    ?s a/rdfs:subClassOf* sosa:Sensor ;
        ssn:hasProperty ?prop .
    ?prop a/rdfs:subClassOf* scal:CalibrationModel .
}
"""

# according to owlready2-documentation instead of the string-replacement above it should
# be also possible to use a "??" / "??1" direct replacement method provided by owlready.



# execute the queries
flatten_list = lambda l : [item[0] for item in l]

# sensors at same location as "TARGET"
res = owl.default_world.sparql(prefixes + query_same_location.format(TARGET="sensor_1:sensor"))
same_location = flatten_list(res)

# sensors measuring same measurand as "TARGET"
res = owl.default_world.sparql(prefixes + query_same_observable_property.format(TARGET="sensor_1:sensor"))
same_measurand = flatten_list(res)

# sensors measuring same quantity kind as "TARGET"
res = owl.default_world.sparql(prefixes + query_same_observed_quantity.format(TARGET="sensor_1:sensor"))
same_quantity = flatten_list(res)

# sensors with calibration models
res = owl.default_world.sparql(prefixes + query_calibrated_sensors)
with_calibration_model = flatten_list(res)


# get the intersection of the relevant results
result = list(set.intersection(*map(set, [same_location, same_measurand, with_calibration_model])))
print(result)