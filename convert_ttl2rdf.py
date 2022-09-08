import rdflib
import glob
import os

# find all turtle files
cwd = "*"
turtle_file_paths = glob.glob(os.path.join(cwd, "*.ttl"))


for onto_path in turtle_file_paths:
    # get ontology name
    onto_name = os.path.splitext(os.path.basename(onto_path))[0]

    # check if already converted
    converted_onto_path = os.path.join(os.path.dirname(onto_path), f"{onto_name}.rdf")
    if True: #not os.path.exists(converted_onto_path):
        # convert
        g = rdflib.Graph()
        g.parse(onto_path)
        g.serialize(destination=converted_onto_path, format='xml')
        print(f"Converted '{onto_name}' to rdf/xml in {converted_onto_path}")
