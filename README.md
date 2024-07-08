[![GloBI Review by Elton](../../actions/workflows/review.yml/badge.svg)](../../actions/workflows/review.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12687627.svg)](https://doi.org/10.5281/zenodo.12687627)
[![GloBI](https://api.globalbioticinteractions.org/interaction.svg?accordingTo=globi:kbseah/ppsdb-globi-export)](https://globalbioticinteractions.org/?accordingTo=globi:kbseah/ppsdb-globi-export) 

This repository contains an export of interaction data from the
[Protist-Prokaryote Symbiosis
Database](https://ppsdb.wikibase.cloud/wiki/Main_Page) for integration with
Global Biotic Interactions (GloBI, http://globalbioticinteractions.org).

PPSDB documents symbiotic interactions between protists (microbial eukaryotes)
and prokaryotes (bacteria and archaea), with a focus on mutualisms and
symbioses with a few specific partners that are in close physical association
(endosymbioses, ectosymbioses). Fungi and macroalgae are generally not
included, nor are microbiome studies that look at associated microbial
communities collectively.

Interaction statements have been manually compiled from the literature. Taxa
are linked to the NCBI Taxonomy identifiers where possible.

The original database is structured as linked open data on a Wikibase instance
hosted by Wikibase.cloud. For integration to GloBI, a subset of the statements
are exported in a tabular format (TSV) and version-controlled in this
repository. The export is performed through a SPARQL query, via a Python script
`execute_query.py`. The dependencies for the Python script are listed in
`requirements.txt`.

If you have comments or questions please [open an
issue](https://github.com/kbseah/ppsdb-globi-export/issues/new). Suggestions
for new examples to add to the database are particularly welcome.

You are also welcome to browse the [original
database](https://ppsdb.wikibase.cloud/wiki/Main_Page), which can be searched
with SPARQL queries. Please refer to the main site for complete documentation.

The table `interactions.tsv` contains the list of symbiotic interactions.
Fields follow the guidelines in the GloBI [template
repository](https://github.com/globalbioticinteractions/template-dataset/).
