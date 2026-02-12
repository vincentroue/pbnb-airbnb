# &s &CITY_REF_DATA - Reference data for Airbnb pressure ratios

# Population (city proper) and housing units/dwellings for 35 European cities.
# Used for computing Airbnb pressure indicators:
#   - listings / 1000 inhabitants
#   - listings / 1000 housing units
#
# Sources & methodology:
#   - Population: Wikipedia "List of European cities by population within city limits",
#     national statistics offices (INSEE, ISTAT, INE, ONS, etc.), 2023-2025 estimates
#   - Housing: National statistics offices, census data (mostly 2021-2023)
#   - Where city-level housing data unavailable, estimated using national
#     dwellings-per-1000-inhabitants ratios from OECD/Eurostat applied to city population
#
# Key national ratios used for estimates (dwellings per 1000 inhabitants):
#   France: 590 | Italy: 587 | Spain: 540 | Greece: 680 | Turkey: 400
#   Hungary: 470 | Portugal: 590 | Belgium: 490 | UK: 440 | Sweden: 520
#   Norway: 500 | Denmark: 520 | Switzerland: 540 | Czech Republic: 490
#
# NOTE: City-level ratios often differ from national averages (cities tend to have
# more dwellings per capita due to smaller household sizes, second homes, vacancies).
# These are reasonable estimates for computing pressure indicators, not exact figures.
#
# Date: 2026-02-09

CITY_DATA = {
    # -------------------------------------------------------------------------
    # CONFIRMED DATA (from official statistics)
    # -------------------------------------------------------------------------

    # UK - ONS / London Datastore / Census 2021
    "london": {
        "pop": 8_800_000,    # GLA estimate 2023
        "housing": 3_800_000, # London Datastore 2023: ~3.8M dwellings
        "pop_source": "GLA mid-year estimate 2023",
        "housing_source": "London Datastore / MHCLG dwelling stock 2023",
    },

    # France - INSEE RP2022
    "paris": {
        "pop": 2_133_000,    # INSEE 2022
        "housing": 1_399_000, # INSEE RP2022: 1,399,122 logements (dept 75)
        "pop_source": "INSEE RP2022",
        "housing_source": "INSEE RP2022 LOG T1 - dept 75",
    },

    # Germany - Statistik Berlin-Brandenburg
    "berlin": {
        "pop": 3_755_000,    # 2023 estimate
        "housing": 2_044_000, # Statistik Berlin-Brandenburg: 2,043,583 (end 2023)
        "pop_source": "Statistik Berlin-Brandenburg 2023",
        "housing_source": "Statistik Berlin-Brandenburg end 2023",
    },

    # Germany - Statistisches Amt München
    "munich": {
        "pop": 1_594_000,    # 2023 estimate
        "housing": 837_000,   # Statista/München Statistik end 2023: ~837,000
        "pop_source": "Statistisches Amt München 2023",
        "housing_source": "Statistisches Amt München 2023",
    },

    # Netherlands - CBS / Amsterdam municipality
    "amsterdam": {
        "pop": 921_000,      # CBS 2023
        "housing": 475_000,   # CBS/Amsterdam: 474,735 (Jan 2023)
        "pop_source": "CBS 2023",
        "housing_source": "Amsterdam Wonen in Amsterdam 2023: 474,735",
    },

    # Austria - Statistik Austria / Wien.gv.at
    "vienna": {
        "pop": 2_010_000,    # 2023 surpassed 2M
        "housing": 1_000_000, # Wien.gv.at: "about one million housing units"
        "pop_source": "Statistik Austria 2023",
        "housing_source": "Wien.gv.at Housing in Vienna: ~1M",
    },

    # Denmark - Statistics Denmark
    "copenhagen": {
        "pop": 660_000,      # Copenhagen Municipality 2023
        "housing": 347_000,   # Statistics Denmark 2023: 346,500
        "pop_source": "Statistics Denmark 2023",
        "housing_source": "Statistics Denmark 2023: 346,500",
    },

    # Czech Republic - CZSO Census 2021
    "prague": {
        "pop": 1_360_000,    # CZSO 2023
        "housing": 630_000,   # CZSO Census 2021: ~630K occupied dwellings
        "pop_source": "CZSO 2023",
        "housing_source": "CZSO Census 2021: ~630K occupied (total ~700K est.)",
    },

    # Ireland - CSO Census 2022
    "dublin": {
        "pop": 590_000,      # Dublin City (not county) Census 2022
        "housing": 251_000,   # CSO Census 2022: 250,632 (Dublin City)
        "pop_source": "CSO Census 2022 - Dublin City",
        "housing_source": "CSO Census 2022: 250,632 (Dublin City)",
    },

    # Norway - SSB / Oslo Kommune
    "oslo": {
        "pop": 709_000,      # SSB 2024
        "housing": 353_000,   # Oslo Kommune: 353,256 (Jan 2024)
        "pop_source": "SSB 2024",
        "housing_source": "Oslo Kommune Boligmengde Jan 2024: 353,256",
    },

    # Sweden - SCB / Stockholm Stad
    "stockholm": {
        "pop": 985_000,      # Stockholm Stad 2023
        "housing": 487_000,   # SCB/Stockholm 2023: 486,542
        "pop_source": "SCB 2023",
        "housing_source": "SCB/Stockholm Stad 2023: 486,542",
    },

    # Switzerland - Stadt Zürich
    "zurich": {
        "pop": 443_000,      # Stadt Zürich 2023
        "housing": 234_000,   # Stadt Zürich 2023: ~233,900
        "pop_source": "Stadt Zürich 2023",
        "housing_source": "Stadt Zürich 2023: ~233,900",
    },

    # UK - ONS Census 2021
    "manchester": {
        "pop": 552_000,      # ONS Census 2021
        "housing": 215_000,   # Manchester Council Census 2021: 214,700
        "pop_source": "ONS Census 2021",
        "housing_source": "Manchester City Council Census 2021: 214,700",
    },

    # UK - Scotland Census 2022
    "edinburgh": {
        "pop": 513_000,      # Scotland Census 2022
        "housing": 253_000,   # Scotland Census 2022: 252,731
        "pop_source": "Scotland Census 2022",
        "housing_source": "Scotland Census 2022: 252,731",
    },

    # Portugal - INE Census 2021
    "lisbon": {
        "pop": 545_000,      # INE Census 2021
        "housing": 320_000,   # INE Census 2021: 320,000
        "pop_source": "INE Portugal Census 2021",
        "housing_source": "INE Portugal Census 2021: 320,000",
    },

    # Portugal - INE Census 2021
    "porto": {
        "pop": 232_000,      # INE Census 2021
        "housing": 133_000,   # INE Census 2021: 133,000
        "pop_source": "INE Portugal Census 2021",
        "housing_source": "INE Portugal Census 2021: 133,000",
    },

    # France - INSEE RP2022
    "lyon": {
        "pop": 523_000,      # INSEE RP2022
        "housing": 319_000,   # INSEE RP2022: 318,612
        "pop_source": "INSEE RP2022",
        "housing_source": "INSEE RP2022 LOG T1: 318,612",
    },

    # France - INSEE RP2022
    "bordeaux": {
        "pop": 260_000,      # INSEE RP2022
        "housing": 168_000,   # INSEE RP2022: 168,458
        "pop_source": "INSEE RP2022",
        "housing_source": "INSEE RP2022 LOG T1: 168,458",
    },

    # -------------------------------------------------------------------------
    # ESTIMATED DATA (population confirmed, housing estimated from ratios/proxies)
    # -------------------------------------------------------------------------

    # Italy - ISTAT 2021. Metro City of Rome = 2.2M dwellings (6.4% of 35.3M national).
    # Commune of Rome ~65% of metro city dwellings. Italy ratio ~587/1000.
    # Rome commune has ~1.35-1.45M dwellings (consistent with 2.8M pop * ~500/1000 city ratio).
    "rome": {
        "pop": 2_750_000,    # ISTAT 2021
        "housing": 1_380_000, # Estimated: Metro City 2.2M, commune ~63%
        "pop_source": "ISTAT 2021",
        "housing_source": "ESTIMATE from ISTAT Metro City Rome 2.2M (commune ~63%)",
    },

    # Turkey - TUIK. Istanbul ~16M pop, Turkey ~400 dwellings/1000 nationally.
    # Istanbul as major city likely ~350/1000 (high household sizes, newer construction).
    "istanbul": {
        "pop": 15_840_000,   # TUIK 2023
        "housing": 5_540_000, # Estimated: ~350/1000 for Istanbul (lower than national avg)
        "pop_source": "TUIK 2023",
        "housing_source": "ESTIMATE from TUIK national ratio ~350/1000 for Istanbul",
    },

    # Spain - INE Census 2021. Madrid had ~1.38M in 2001 census.
    # 20 years of growth, Community of Madrid = 3M dwellings.
    # City of Madrid ~55% of community. ~1.65M dwellings.
    "madrid": {
        "pop": 3_400_000,    # INE 2024
        "housing": 1_650_000, # Estimated: ~55% of Community of Madrid 3M stock
        "pop_source": "INE Padron 2024",
        "housing_source": "ESTIMATE from INE: ~55% of Community of Madrid 3M",
    },

    # Greece - ELSTAT Census 2021. Greece total ~6.6M dwellings (9.7M pop = 680/1000).
    # Athens municipality pop 643K, Athens tends toward lower ratio (~550/1000 for dense urban).
    "athens": {
        "pop": 643_000,      # ELSTAT Census 2021
        "housing": 385_000,   # Estimated: ~600/1000 (dense urban, many vacancies/second homes)
        "pop_source": "ELSTAT Census 2021",
        "housing_source": "ESTIMATE from ELSTAT: Greece 680/1000 national, Athens ~600",
    },

    # Spain - INE/Idescat Census 2021. Barcelona city ~540/1000 Spanish avg.
    # Tight city boundaries suggest higher density ratio.
    "barcelona": {
        "pop": 1_660_000,    # INE 2024
        "housing": 810_000,   # Estimated: ~490/1000 (dense, tight boundaries)
        "pop_source": "INE Padron 2024",
        "housing_source": "ESTIMATE from INE/Idescat 2021 census (~490/1000)",
    },

    # Hungary - KSH Census 2022. Hungary total 4.6M dwellings (9.6M pop = 479/1000).
    # Budapest pop 1.75M, typically ~500/1000 for capital.
    "budapest": {
        "pop": 1_750_000,    # KSH 2023
        "housing": 880_000,   # Estimated: ~500/1000 (capital city, higher than national)
        "pop_source": "KSH 2023",
        "housing_source": "ESTIMATE from KSH: Hungary 479/1000 national, Budapest ~500",
    },

    # Italy - ISTAT 2021. Florence commune 372K pop. Italy ~587/1000 national.
    # Tourist city with many second homes, likely ~560/1000.
    "florence": {
        "pop": 372_000,      # ISTAT 2023
        "housing": 208_000,   # Estimated: ~560/1000
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: Italy 587/1000, Florence ~560",
    },

    # Belgium - Statbel. Brussels-Capital Region = 1.2M pop, ~570K dwellings.
    # Brussels commune proper = ~190K pop, but for Airbnb we use the 19-commune Region.
    # Using Region as "city proper" since that matches Inside Airbnb data.
    "brussels": {
        "pop": 1_220_000,    # Brussels-Capital Region 2023
        "housing": 570_000,   # Statbel: 11% of Belgium 4.9M = ~540K + growth
        "pop_source": "Statbel 2023 (Brussels-Capital Region)",
        "housing_source": "ESTIMATE from Statbel: 11% of Belgium occupied conventional dwellings",
    },

    # Italy - ISTAT 2021. Milan commune ~1.4M pop.
    # Dense city with high dwelling count. Italy ~587/1000.
    "milan": {
        "pop": 1_396_000,    # ISTAT 2023
        "housing": 790_000,   # Estimated: ~565/1000 (dense urban)
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: Italy 587/1000, Milan ~565",
    },

    # Italy - ISTAT 2021. Naples commune ~918K pop.
    # Southern Italy, larger household sizes → lower ratio ~480/1000.
    "naples": {
        "pop": 918_000,      # ISTAT 2023
        "housing": 440_000,   # Estimated: ~480/1000 (larger households in south)
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: ~480/1000 (southern Italy, larger households)",
    },

    # Spain - INE Census 2021. Malaga ~580K pop.
    # Resort/tourist city, higher vacancy/second homes ratio ~560/1000.
    "malaga": {
        "pop": 587_000,      # INE 2024
        "housing": 330_000,   # Estimated: ~560/1000 (tourist city, second homes)
        "pop_source": "INE Padron 2024",
        "housing_source": "ESTIMATE from INE: ~560/1000 (tourist city)",
    },

    # Spain - INE Census 2021. Valencia ~800K pop.
    # Spanish average ~540/1000.
    "valencia": {
        "pop": 800_000,      # INE 2024
        "housing": 430_000,   # Estimated: ~540/1000
        "pop_source": "INE Padron 2024",
        "housing_source": "ESTIMATE from INE: ~540/1000 (Spanish average)",
    },

    # Spain - INE Census 2021. Sevilla ~685K pop.
    "sevilla": {
        "pop": 685_000,      # INE 2024
        "housing": 370_000,   # Estimated: ~540/1000
        "pop_source": "INE Padron 2024",
        "housing_source": "ESTIMATE from INE: ~540/1000 (Spanish average)",
    },

    # Italy - ISTAT 2021. Venice commune ~258K pop.
    # Very high second home / tourist housing ratio, likely ~650/1000.
    "venice": {
        "pop": 258_000,      # ISTAT 2023
        "housing": 168_000,   # Estimated: ~650/1000 (extreme second homes/tourism)
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: ~650/1000 (high tourism/second homes)",
    },

    # Greece - ELSTAT Census 2021. Thessaloniki municipality ~319K pop.
    # Greece ~680/1000 nationally, urban ~550/1000.
    "thessaloniki": {
        "pop": 319_000,      # ELSTAT Census 2021
        "housing": 190_000,   # Estimated: ~600/1000 (28% vacancy in 2011 = high stock)
        "pop_source": "ELSTAT Census 2021",
        "housing_source": "ESTIMATE from ELSTAT: ~600/1000 (high vacancy rates)",
    },

    # Italy - ISTAT 2021. Bologna commune ~397K pop.
    "bologna": {
        "pop": 397_000,      # ISTAT 2023
        "housing": 225_000,   # Estimated: ~567/1000
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: ~567/1000",
    },

    # Italy - ISTAT 2021. Bergamo commune ~115K pop.
    "bergamo": {
        "pop": 122_000,      # ISTAT 2023
        "housing": 68_000,    # Estimated: ~557/1000
        "pop_source": "ISTAT 2023",
        "housing_source": "ESTIMATE from ISTAT: ~557/1000",
    },
}


# ---- Simplified version (just pop + housing) for quick use ----

CITY_POP_HOUSING = {k: {"pop": v["pop"], "housing": v["housing"]}
                     for k, v in CITY_DATA.items()}


# ---- Quick verification ----

if __name__ == "__main__":
    print(f"{'City':<16} {'Population':>12} {'Housing':>10} {'Ratio':>8}")
    print("-" * 50)
    for city, data in CITY_DATA.items():
        ratio = data["housing"] / data["pop"] * 1000
        marker = "" if "ESTIMATE" not in data["housing_source"] else " *"
        print(f"{city:<16} {data['pop']:>12,} {data['housing']:>10,} {ratio:>7.0f}{marker}")
    print()
    confirmed = sum(1 for v in CITY_DATA.values() if "ESTIMATE" not in v["housing_source"])
    estimated = len(CITY_DATA) - confirmed
    print(f"Total: {len(CITY_DATA)} cities ({confirmed} confirmed, {estimated} estimated)")

# &e
