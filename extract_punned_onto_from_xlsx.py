import os
import pandas as pd

# what to load
input_path = os.path.abspath("ontologies/scal_punned.xlsx")
output_path = os.path.splitext(input_path)[0] + ".ttl"

# read in excel file
sheets = ["preamble", "meta_properties"]
doc = pd.read_excel(input_path, sheet_name=sheets, dtype="str", header=0)

# prepare output doc
turtle_file_content = []

# combine preamble into turtle syntax
preamble = doc[sheets[0]].fillna("")
for i, row in preamble.iterrows():
    turtle_line = " ".join(row.values)
    turtle_file_content.append(turtle_line)

# create main meta property values
meta_properties = doc[sheets[1]].fillna("")

for group_name, group in meta_properties.groupby("Category"):
    turtle_file_content.append("\n\n### " + group_name + "\n")
    for _, row in group.iterrows():
        c = row["Class"]
        r = row["Rigidity"]
        i = row["Identity"]
        u = row["Unity"]
        d = row["Dependence"]
        cat = row["Category"]
        subof = row["subClassOf"]
        hassub = row["hasSubClass"]


        print(f"\\texttt{{{c}}} {'$^*$' if cat == 'Assumed external meta properties' else ''} & \\texttt{{{r}}} & \\texttt{{{u}}} & \\texttt{{{i}}} & \\texttt{{{d}}} \\\\")

        # translate into ontoclean classes
        ## rigidity
        if r == "+R":
            R_CLASS = "ontoclean:RigidClass"
        elif r == "-R":
            R_CLASS = "ontoclean:NonRigidClass"
        elif r == "~R":
            R_CLASS = "ontoclean:AntiRigidClass"
        else:
            R_CLASS = ""

        ## unity
        if u == "+U":
            U_CLASS = "ontoclean:UnityClass"
        elif u == "-U":
            U_CLASS = "ontoclean:NonUnityClass"
        elif u == "~U":
            U_CLASS = "ontoclean:AntiUnityClass"
        else:
            U_CLASS = ""

        ## identity / sortal
        if i == "+I":
            I_CLASS = "ontoclean:SortalClass"
        elif i == "-I":
            I_CLASS = "ontoclean:NonSortalClass"
        else:
            I_CLASS = ""

        ## dependence
        if d == "+D":
            D_CLASS = "ontoclean:DependentClass"
        elif d == "-D":
            D_CLASS = "ontoclean:NonDependentClass"
        else:
            D_CLASS = ""

        # generate triples
        triples = []
        triples.append([c, "a", "owl:NamedIndividual"])
        triples.append([" ", "a", "ontoclean:Class"])
        if R_CLASS:
            triples.append([" ", "a", R_CLASS])
        if U_CLASS:
            triples.append([" ", "a", U_CLASS])
        if I_CLASS:
            triples.append([" ", "a", I_CLASS])
        if D_CLASS:
            triples.append([" ", "a", D_CLASS])
        if subof:
            triples.append([" ", "ontoclean:subClassOf", subof])
        if hassub:
            triples.append([" ", "ontoclean:hasSubClass", subof])
        
        # convert triples to turtle lines with correct line delimiter (; or .)
        for i, triple in enumerate(triples):
            turtle_line = " ".join(triple)
            if i == len(triples) - 1:  # last line
                turtle_line += " .\n"
            else:
                turtle_line += " ;"
            turtle_file_content.append(turtle_line)
    
# write result to file
f = open(output_path, "w")
output = "\n".join(turtle_file_content)
f.write(output)
f.close()