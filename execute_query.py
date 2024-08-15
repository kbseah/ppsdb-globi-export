#!/usr/bin/env python3

import json
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_login
from wikibaseintegrator import WikibaseIntegrator, datatypes, wbi_helpers

wbi_config["MEDIAWIKI_API_URL"] = "https://ppsdb.wikibase.cloud/w/api.php"
wbi_config["SPARQL_ENDPOINT_URL"] = "https://ppsdb.wikibase.cloud/query/sparql"
wbi_config["WIKIBASE_URL"] = "https://ppsdb.wikibase.cloud"
wbi_config["MEDIAWIKI_INDEX_URL"] = "https://ppsdb.wikibase.cloud/w/index.php"
wbi_config["MEDIAWIKI_REST_URL"] = ("https://ppsdb.wikibase.cloud/w/rest.php",)

with open("secrets/bot_password.json", "r") as fh:
    pw = json.load(fh)
login = wbi_login.Login(user=pw["user"], password=pw["password"])

sparql_prefixes = """
PREFIX pp: <https://ppsdb.wikibase.cloud/entity/>
PREFIX ppt: <https://ppsdb.wikibase.cloud/prop/direct/>
PREFIX pps: <https://ppsdb.wikibase.cloud/prop/>
PREFIX ppss: <https://ppsdb.wikibase.cloud/prop/statement/>
PREFIX ppsq: <https://ppsdb.wikibase.cloud/prop/qualifier/>
PREFIX ppsr: <https://ppsdb.wikibase.cloud/prop/reference/>
"""

query = """
#List all interactions, optionally the localization, interaction type, and references
SELECT DISTINCT ?argumentTypeId ?argumentTypeName ?sourceTaxonName ?sourceTaxonId ?sourceTaxonWd_qid ?sourceTaxonPpsdb_qid ?interactionTypeName ?interactionTypeId ?targetTaxonName ?targetTaxonId ?targetTaxonWd_qid ?targetTaxonPpsdb_qid ?sourceBodyPartName ?sourceBodyPartId ?referenceDoi ?referenceCitation WHERE {
  ?sourceTaxon pps:P19 ?interaction.
  ?interaction ppss:P19 ?targetTaxon.
  OPTIONAL {
    ?interaction ppsq:P20 ?sourceBodyPart. 
    ?sourceBodyPart rdfs:label ?sourceBodyPartName.
    OPTIONAL { ?sourceBodyPart ppt:P17 ?sourceBodyPartId. }
    OPTIONAL { ?sourceBodyPart ppt:P44 ?sourceBodyPartId. }
  }
  OPTIONAL {
    ?interaction ppsq:P26 ?type. 
    ?type rdfs:label ?typeLabel. 
    OPTIONAL { ?type ppt:P16 ?interactionTypeId. }
  }
  # if no interaction type is given, then default to "host of"
  BIND (EXISTS { ?interaction ppsq:P26 ?type. } AS ?existsType )
  BIND (IF(?existsType, ?typeLabel, "host of") AS ?interactionTypeName)
  OPTIONAL {
    ?interaction prov:wasDerivedFrom ?refnode.
    # OPTIONAL { ?refnode ppsr:P27 ?doi }
    OPTIONAL {
      ?refnode ppsr:P23 ?statedIn.
      OPTIONAL { ?statedIn ppt:P13 ?referenceDoi. }
      OPTIONAL { ?statedIn ppt:P14 ?referenceCitation. }
      BIND (STR("support") AS ?argumentTypeName)
    }
    OPTIONAL {
      ?refnode ppsr:P43 ?statedIn.
      OPTIONAL { ?statedIn ppt:P13 ?referenceDoi. }
      OPTIONAL { ?statedIn ppt:P14 ?referenceCitation. }
      BIND (STR("refute") AS ?argumentTypeName)
      BIND (STR("https://en.wiktionary.org/wiki/refute") AS ?argumentTypeId) 
    }
  }
  OPTIONAL {
    ?sourceTaxon ppt:P11 ?sourceTaxon_ncbi. 
    BIND ( CONCAT("NCBI:txid", STR(?sourceTaxon_ncbi)) as ?sourceTaxonId )
  }
  OPTIONAL {
    ?targetTaxon ppt:P11 ?targetTaxon_ncbi. 
    BIND ( CONCAT("NCBI:txid", STR(?targetTaxon_ncbi)) as ?targetTaxonId )
  }
  OPTIONAL {
    ?sourceTaxon ppt:P2 ?sourceTaxonWd.
    BIND (STR(REPLACE(STR(?sourceTaxonWd), ".*Q", "WD:Q")) AS ?sourceTaxonWd_qid)
  }
  OPTIONAL {
    ?targetTaxon ppt:P2 ?targetTaxonWd.
    BIND (STR(REPLACE(STR(?targetTaxonWd), ".*Q", "WD:Q")) AS ?targetTaxonWd_qid)
  }
  BIND (STR(REPLACE(STR(?sourceTaxon), ".*Q", "PPSDB:Q")) AS ?sourceTaxonPpsdb_qid)
  BIND (STR(REPLACE(STR(?targetTaxon), ".*Q", "PPSDB:Q")) AS ?targetTaxonPpsdb_qid)
#   OPTIONAL {
#     ?sourceTaxon ppt:P40 ?habitat.
#     ?habitat rdfs:label ?habitatName.
#     ?habitat ppt:P37 ?habitatId.
#   }
  ?sourceTaxon rdfs:label ?sourceTaxonName .
  OPTIONAL { ?targetTaxon rdfs:label ?targetTaxonName. }
  OPTIONAL { ?sourceTaxon ppt:P2 ?sourceWdmap . }
  OPTIONAL { ?targetTaxon ppt:P2 ?targetWdmap . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?sourceTaxonName ?targetTaxonName
"""


wbi = WikibaseIntegrator(login=login)

print("Executing SPARQL query to retrieve records")

rec = wbi_helpers.execute_sparql_query(query=query, prefix=sparql_prefixes)

fields = [
    "argumentTypeId",
    "argumentTypeName",
    "sourceTaxonName",
    "sourceTaxonId",
    "sourceTaxonIds",
    "interactionTypeName",
    "interactionTypeId",
    "targetTaxonName",
    "targetTaxonId",
    "targetTaxonIds",
    "sourceBodyPartName",
    "sourceBodyPartId",
    "referenceDoi",
    "referenceCitation",
]

# Convert to TSV
if "bindings" in rec["results"] and len(rec["results"]["bindings"]) > 0:
    print("Converting to TSV format")
    print(f"{str(len(rec['results']['bindings']))} results found")
    with open("interactions.tsv", "w") as fh:
        fh.write("\t".join(fields) + "\n")
        for line in rec["results"]["bindings"]:
            out = []
            for field in fields:
                # concatenate primary and secondary identifiers if available
                if field == "sourceTaxonIds":
                    out.append(
                        "|".join(
                            [
                                line[i]["value"]
                                for i in [
                                    "sourceTaxonId",
                                    "sourceTaxonWd_qid",
                                    "sourceTaxonPpsdb_qid",
                                ]
                                if i in line and "value" in line[i]
                            ]
                        )
                    )
                elif field == "targetTaxonIds":
                    out.append(
                        "|".join(
                            [
                                line[i]["value"]
                                for i in [
                                    "targetTaxonId",
                                    "targetTaxonWd_qid",
                                    "targetTaxonPpsdb_qid",
                                ]
                                if i in line and "value" in line[i]
                            ]
                        )
                    )
                elif field in line and "value" in line[field]:
                    out.append(line[field]["value"])
                else:
                    out.append("")
            fh.write("\t".join(out))
            fh.write("\n")
