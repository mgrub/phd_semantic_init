import datetime
import json
import os

import jellyfish
import owlready2 as owl
import pdfplumber
import yake
import numpy as np

onto_prefix = "trans"
onto_ns = "http://www.example.com/ns/trans/"

if True:
    owl.onto_path.append("ontologies")

    # extract classes from ontology to evaluate

    onto = owl.get_ontology(f"file://ontologies/{onto_prefix}.rdf").load()
    with onto:
        owl.sync_reasoner()

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

    query_classes = f'''
    SELECT ?s
    WHERE {{
        ?s a owl:Class .
        FILTER(STRSTARTS(STR(?s), "{onto_ns}")) 
    }}
    '''

    classes = list(owl.default_world.sparql(prefixes + query_classes))
    class_names = [c[0]._name for c in classes]


# extract corpus data from pdf
pdf_path = r"C:\Users\gruber04\PTBbox\home\documentation\Zotero\storage\8KSSI35M\Oppenheim et al. - 1996 - Signals & systems (2nd ed.).pdf"
base = os.path.splitext(os.path.basename(pdf_path))[0]
tmp_file = f"{base}_tmp.json"
load_from_tmp = os.path.exists(tmp_file)

# load corpus
if load_from_tmp:
    file_name = os.path.basename(pdf_path)
    f = open(tmp_file, "r")
    content = json.load(f)
    f.close()
else:
    with pdfplumber.open(pdf_path) as pdf:
        content = []
        for i, page in enumerate(pdf.pages):  # [18:951]
            content.append(page.extract_text().lower())
            if i % 10 == 0:
                progress = int(100 * i / len(pdf.pages))
                print(f"{progress:02d}%", datetime.datetime.now())
    # dump text content for easier later use
    f = open(tmp_file, "w")
    json.dump(content, f)
    f.close()

# extract keywords
keywords_file = f"{base}_keywords.json"
load_from_kwfile = os.path.exists(keywords_file)

if load_from_kwfile:
    f = open(keywords_file, "r")
    keywords = json.load(f)
    f.close()
else:
    kwex = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.5, top=1000, features=None)
    keywords = kwex.extract_keywords(" ".join(content))
    f = open(keywords_file, "w")
    json.dump(keywords, f)
    f.close()

# check for closest match by comparing strings
results_file = f"{onto_prefix}_results.json"
#class_names = ["butterbrot", "TransferModel", "FilterType", "Butterworth"]

results = {}
for c in class_names:
    res = [jellyfish.jaro_winkler_similarity(c.lower(), kw[0]) for kw in keywords]
    best = np.argmax(res)
    #print(c, res[best], keywords[best])

    results[c] = {
        "jaro_winkler_partner" : keywords[best][0],
        "jaro_winkler_similarity": res[best],
    }

    print(f"{c},{keywords[best][0]},{res[best]:0.2f}")


f = open(results_file, "w")
json.dump(results, f, indent=4)
f.close()