"""
Constants used throughout the WFM Checker package.

This module contains various data structures and mappings used for 
item name normalization and API interactions.
"""

from typing import Dict, Tuple, List

# Ayatan Sculpture maximum star data: {normalized_name: (max_amber_stars, max_cyan_stars)}
# Used to check for fully socketed sculptures vs empty ones when fetching prices
AYATAN_SCULPTURES: Dict[str, Tuple[int, int]] = {
    'ayatan_anasa_sculpture': (2, 2),
    'ayatan_hemakara_sculpture': (1, 2),
    'ayatan_kitha_sculpture': (1, 4),
    'ayatan_zambuka_sculpture': (1, 2),
    'ayatan_orta_sculpture': (1, 3),
    'ayatan_vaya_sculpture': (1, 2),
    'ayatan_piv_sculpture': (1, 2),
    'ayatan_valana_sculpture': (1, 2),
    'ayatan_sah_sculpture': (1, 2),
    'ayatan_ayr_sculpture': (0, 3),
}

# Weird URL special cases handler
SPECIAL_CASES: Dict[str, str] = {
    "semi-shotgun cannonade": "shotgun_cannonade",
    "summoner's wrath": "summoner%E2%80%99s_wrath",
    "fear sense": "sense_danger",
    "negation armor": "negation_swarm",
    "teleport rush": "fatal_teleport",
    "ghoulsaw blade": "ghoulsaw_blade_blueprint",
    "ghoulsaw engine": "ghoulsaw_engine_blueprint",
    "ghoulsaw grip": "ghoulsaw_grip_blueprint",
    "mutalist alad v assassinate (key)": "mutalist_alad_v_assassinate_key",
    "mutalist alad v nav coordinate": "mutalist_nav_coordinates",
    "scan aquatic lifeforms": "scan_lifeforms",
    "orokin tower extraction scene": "orokin_tower_extraction_scene",
    "orokin derelict simulacrum": "orokin_derelict_simulacrum",
    "orokin derelict plaza scene": "orokin_derelict_plaza_scene",
    "central mall backroom scene": "central_mall_backroom",
    "höllvanian historic quarter in spring scene": "höllvanian_historic_quarter_in_spring",
    "höllvanian intersection in winter scene": "höllvanian_intersection_in_winter",
    "höllvanian old town in fall scene": "höllvanian_old_town_in_fall",
    "höllvanian tenements in summer scene": "höllvanian_tenements_in_summer",
    "höllvanian terrace in summer scene": "höllvanian_terrace_in_summer",
    "orbit arcade scene": "orbit_arcade",
    "tech titan electronics store scene": "tech_titan_electronics_store",
    "riot-848 stock blueprint": "riot_848_stock",
    "riot-848 barrel blueprint": "riot_848_barrel",
    "riot-848 receiver blueprint": "riot_848_receiver",
}

EXCEPTIONS: List[str] = [
    'carrier_prime_systems',
    'dethcube_prime_systems',
    'helios_prime_systems',
    'nautilus_prime_systems',
    'nautilus_systems',
    'shade_prime_systems',
    'shedu_chassis',
    'spectra_vandal_chassis',
    'wyrm_prime_systems'
]

# List of Warframe prime names, this includes all primes of all warframes released
# even those who do not have a prime variant yet, this is done because the normal variant is undtradable and as such cannot be found in the market.
# this was done to avoid having to update the list every time a new prime is released
WARFRAMES: List[str] = [
    'ash_prime',
    'ember_prime',
    'excalibur_prime',
    'loki_prime',
    'mag_prime',
    'rhino_prime',
    'trinity_prime',
    'volt_prime',
    'frost_prime',
    'nyx_prime',
    'banshee_prime',
    'saryn_prime',
    'vauban_prime',
    'nova_prime',
    'nekros_prime',
    'valkyr_prime',
    'oberon_prime',
    'zephyr_prime',
    'hydroid_prime',
    'mirage_prime',
    'limbo_prime',
    'mesa_prime',
    'chroma_prime',
    'equinox_prime',
    'atlas_prime',
    'wukong_prime',
    'ivara_prime',
    'nezha_prime',
    'inaros_prime',
    'titania_prime',
    'nidus_prime',
    'octavia_prime',
    'harrow_prime',
    'gara_prime',
    'khora_prime',
    'revenant_prime',
    'garuda_prime',
    'baruuk_prime',
    'hildryn_prime',
    'wisp_prime',
    'gauss_prime',
    'grendel_prime',
    'protea_prime',
    'xaku_prime',
    'lavos_prime',
    'sevagoth_prime',
    'yareli_prime',
    'caliban_prime',
    'gyre_prime',
    'styanax_prime',
    'voruna_prime',
    'citrine_prime',
    'kullervo_prime',
    'dagath_prime',
    'qorvex_prime',
    'dante_prime',
    'jade_prime',
    'koumei_prime',
    'cyte_09_prime',
    'temple_prime',
    'oraxia_prime',
    'uriel_prime'
]
