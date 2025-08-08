# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from ebi_eva_common_pyutils.ncbi_utils import retrieve_species_scientific_name_from_tax_id_ncbi
from ebi_eva_common_pyutils.network_utils import json_request
from ebi_eva_common_pyutils.logger import logging_config as log_cfg


logger = log_cfg.get_logger(__name__)


def get_scientific_name_from_ensembl(taxonomy_id: int) -> str:
    ENSEMBL_REST_API_URL = "https://rest.ensembl.org/taxonomy/id/{0}?content-type=application/json".format(taxonomy_id)
    response = json_request(ENSEMBL_REST_API_URL)
    if "scientific_name" not in response:
        raise Exception("Scientific name could not be found for taxonomy {0} using the Ensembl API URL: {1}"
                        .format(taxonomy_id, ENSEMBL_REST_API_URL))
    return response["scientific_name"]


def normalise_taxon_scientific_name(taxon_name):
    """
    Match Ensembl representation
    See Clostridium sp. SS2/1 represented as clostridium_sp_ss2_1 in
    ftp://ftp.ensemblgenomes.org/pub/bacteria/release-48/fasta/bacteria_25_collection/clostridium_sp_ss2_1/
    """
    return re.sub('[^0-9a-zA-Z]+', '_', taxon_name.lower())


def get_normalized_scientific_name_from_ensembl(taxonomy_id: int) -> str:
    """Get the scientific name for that taxon"""
    return normalise_taxon_scientific_name(get_scientific_name_from_ensembl(taxonomy_id))


def get_scientific_name_from_taxonomy(taxonomy_id: int, api_key: str=None) -> str:
    """
    Search for a species scientific name based on the taxonomy id.
    Will first attempt to retrieve from Ensembl and then NCBI, if not found returns None.
    """
    try:
        species_name = get_scientific_name_from_ensembl(taxonomy_id)
    except Exception:
        logger.warning("Failed to retrieve scientific name in Ensembl for taxonomy id {0}".format(taxonomy_id))
        species_name = None
    if not species_name:
        species_name = retrieve_species_scientific_name_from_tax_id_ncbi(taxonomy_id, api_key=api_key)
    return species_name
