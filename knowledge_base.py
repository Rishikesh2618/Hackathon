"""
FarmAI Knowledge Base
Contains structured knowledge about crops, pests, fertilizers, and government schemes.
"""

KNOWLEDGE_BASE = [
    # ─────────────────── CROPS ───────────────────
    {
        "id": "crop_001",
        "category": "crops",
        "title": "Rice Cultivation",
        "content": (
            "Rice is one of India's most important staple crops. It grows best in areas with "
            "high rainfall (100–200 cm) and temperatures of 20–35°C. Transplanting seedlings is "
            "the preferred method. Paddy varieties include Basmati (aromatic, long-grain), IR-36, "
            "and Swarna (high-yield). Spacing: 20×15 cm. Water management is critical – maintain "
            "5–7 cm standing water during vegetative stage. Harvest when 80% of grains turn golden. "
            "Yield: 4–6 tonnes/hectare."
        ),
        "keywords": ["rice", "paddy", "transplanting", "basmati", "ir36", "swarna", "harvest"]
    },
    {
        "id": "crop_002",
        "category": "crops",
        "title": "Wheat Cultivation",
        "content": (
            "Wheat is a major rabi (winter) crop grown from October to March. Optimal temperature "
            "is 10–25°C. Sow seeds at 100–125 kg/hectare with 22.5 cm row spacing. Top varieties: "
            "HD-2967, PBW-343, WH-542. Apply 120 kg N, 60 kg P2O5, 40 kg K2O per hectare. "
            "Irrigate at crown root initiation, tillering, and grain-filling stages. Harvest when "
            "moisture is below 14%. Yield: 3–5 tonnes/hectare. Watch for rust, powdery mildew."
        ),
        "keywords": ["wheat", "rabi", "winter crop", "hd2967", "pbw343", "irrigation", "rust"]
    },
    {
        "id": "crop_003",
        "category": "crops",
        "title": "Cotton Cultivation",
        "content": (
            "Cotton (Gossypium) is a major kharif cash crop. Preferred soil: black cotton (Regur) "
            "or sandy loam. Temperature: 21–30°C. Sow May–June with 90×60 cm spacing. Bt-cotton "
            "varieties (Bollgard II) offer boll-worm resistance. Apply NPK: 100:50:50 kg/ha. "
            "Critical water stages: square formation, flowering, boll development. Harvest bolls "
            "when fully open. Yield: 15–20 quintals/hectare (seed cotton)."
        ),
        "keywords": ["cotton", "kharif", "bt cotton", "bollgard", "boll weevil", "cash crop", "ginning"]
    },
    {
        "id": "crop_004",
        "category": "crops",
        "title": "Sugarcane Cultivation",
        "content": (
            "Sugarcane is a long-duration (12–18 months) crop requiring tropical climate. Propagated "
            "by setts (3-budded). Varieties: Co-86032, CoM-0265, CoS-767. Plant in February–March at "
            "90 cm row spacing. Apply 250:60:120 kg NPK/ha split over 3–4 months. Irrigation every "
            "7–10 days until maturity. Trash mulching conserves moisture. Harvest when Brix value "
            "reaches 18–20%. Ratoon crop gives 80% of plant yield."
        ),
        "keywords": ["sugarcane", "setts", "ratoon", "brix", "sucrose", "trash mulching", "jaggery"]
    },
    {
        "id": "crop_005",
        "category": "crops",
        "title": "Tomato Cultivation",
        "content": (
            "Tomato is a warm-season vegetable grown year-round in India. Varieties: Pusa Ruby, "
            "Arka Vikas, hybrid varieties. Transplant 25-day-old seedlings with 60×45 cm spacing. "
            "Apply 100:60:50 kg NPK/ha plus micronutrients. Use drip irrigation for best results. "
            "Stake plants to prevent lodging. Common problems: early blight, leaf curl virus, "
            "fruit borer. Harvest at mature green or red-ripe stage. Yield: 25–40 tonnes/hectare."
        ),
        "keywords": ["tomato", "pusa ruby", "arka vikas", "blight", "leaf curl", "fruit borer", "staking"]
    },
    {
        "id": "crop_006",
        "category": "crops",
        "title": "Maize (Corn) Cultivation",
        "content": (
            "Maize is a kharif crop used for food, fodder, and industry. Sow in June–July at "
            "60×25 cm spacing. Apply 120:60:40 kg NPK/ha; top-dress nitrogen at knee-high stage. "
            "Varieties: DHM-117, NK-6240, Pioneer hybrids. Irrigate at silking and grain-fill. "
            "Major pests: Fall Armyworm (FAW), stem borer. Control FAW with emamectin benzoate. "
            "Harvest when husk turns dry. Yield: 5–8 tonnes/hectare."
        ),
        "keywords": ["maize", "corn", "fall armyworm", "silking", "dhm117", "stem borer", "fodder"]
    },
    {
        "id": "crop_007",
        "category": "crops",
        "title": "Soybean Cultivation",
        "content": (
            "Soybean is a high-protein kharif oilseed crop. Sow June–July at 45×5 cm spacing, "
            "seed rate 70 kg/ha. Varieties: JS-9560, MACS-1407. Inoculate seeds with Rhizobium "
            "culture to fix nitrogen. Apply 30:60:40 kg NPK/ha at sowing. Requires well-drained "
            "soil (pH 6–7). Critical stages: flowering and pod formation. Control yellow mosaic "
            "virus with whitefly management. Yield: 2–3 tonnes/hectare."
        ),
        "keywords": ["soybean", "soya", "rhizobium", "oilseed", "js9560", "mosaic virus", "protein"]
    },
    {
        "id": "crop_008",
        "category": "crops",
        "title": "Groundnut (Peanut) Cultivation",
        "content": (
            "Groundnut is a kharif legume cash crop. Sow June–July at 30×10 cm spacing. Varieties: "
            "TAG-24, ICGS-44, Kadiri-6. Apply 25:50:50 kg NPK/ha; avoid excess nitrogen. Gypsum "
            "250 kg/ha at flowering helps pod development. Peg-zone moisture is critical. "
            "Major diseases: tikka leaf spot, stem rot. Harvest when leaves turn yellow. "
            "Yield: 2–4 tonnes pods/hectare."
        ),
        "keywords": ["groundnut", "peanut", "gypsum", "tikka", "stem rot", "legume", "oilseed"]
    },
    {
        "id": "crop_009",
        "category": "crops",
        "title": "Banana Cultivation",
        "content": (
            "Banana is a perennial tropical crop. Plant tissue-culture suckers at 1.8×1.5 m spacing. "
            "Varieties: Grand Naine, Robusta, Nendran. Apply 200:30:300 g NPK per plant. Drip "
            "fertigation is ideal. Propping needed to prevent storm lodging. Critical threat: "
            "Panama Wilt (Fusarium) and Sigatoka leaf spot. Bunch emerges 9–12 months after planting; "
            "harvest when fingers fill out. Yield: 30–70 tonnes/hectare."
        ),
        "keywords": ["banana", "grand naine", "tissue culture", "panama wilt", "sigatoka", "drip fertigation"]
    },
    {
        "id": "crop_010",
        "category": "crops",
        "title": "Onion Cultivation",
        "content": (
            "Onion (kharif, rabi, late kharif) suits sandy loam soils (pH 6–7). Varieties: "
            "Agrifound Light Red, Bhima Super. Transplant 45-day seedlings at 15×10 cm. Apply "
            "100:50:50 kg NPK/ha plus zinc. Irrigation: critical during bulb development. "
            "Main diseases: purple blotch, downy mildew. Pre-harvest withhold water for 2 weeks. "
            "Yield: 25–40 tonnes/hectare. Proper curing prevents storage losses."
        ),
        "keywords": ["onion", "bulb", "purple blotch", "bhima super", "curing", "rabi", "kharif"]
    },

    # ─────────────────── PESTS ───────────────────
    {
        "id": "pest_001",
        "category": "pests",
        "title": "Brown Plant Hopper (BPH) in Rice",
        "content": (
            "Brown Plant Hopper (Nilaparvata lugens) is the most destructive rice pest causing "
            "'hopperburn'. Both nymphs and adults suck phloem sap, causing yellowing and drying. "
            "Favoured by dense planting, excess nitrogen, and waterlogged conditions. "
            "Management: Drain water to break BPH cycle; spray imidacloprid 17.8 SL @ 125 ml/ha "
            "or buprofezin 25 SC @ 1 L/ha. Avoid synthetic pyrethroids (cause resurgence). "
            "Plant BPH-resistant varieties (IR-64, MTU-1010)."
        ),
        "keywords": ["bph", "brown planthopper", "hopperburn", "rice pest", "imidacloprid", "nilaparvata", "phloem"]
    },
    {
        "id": "pest_002",
        "category": "pests",
        "title": "Fall Armyworm in Maize",
        "content": (
            "Fall Armyworm (Spodoptera frugiperda) is an invasive pest from Americas devastating "
            "maize crops in India since 2018. Caterpillars bore into whorl, creating 'window-pane' "
            "damage; older caterpillars attack ears. Identification: caterpillar has inverted Y-mark "
            "on head. "
            "Management: Apply emamectin benzoate 5 SG @ 200 g/ha or chlorantraniliprole 18.5 SC @ 150 ml/ha. "
            "Coarse sand or fine soil in whorl for early control. Pheromone traps at 5/acre."
        ),
        "keywords": ["fall armyworm", "faw", "spodoptera", "maize pest", "whorl", "emamectin", "pheromone trap"]
    },
    {
        "id": "pest_003",
        "category": "pests",
        "title": "Aphids in Vegetables",
        "content": (
            "Aphids (Aphis gossypii, Myzus persicae) are soft-bodied insects that suck plant sap, "
            "causing leaf curl, yellowing, and sooty mould. They serve as vectors for 100+ plant "
            "viruses. Colonies form on undersides of young leaves. "
            "Management: Spray imidacloprid 70 WS @ 3 g/litre or thiamethoxam 25 WG @ 0.3 g/litre. "
            "Biological: Lady beetles, lacewings. Neem-based spray (3 ml/litre) for organic farming. "
            "Aluminium-foil mulch repels aphids."
        ),
        "keywords": ["aphid", "aphis gossypii", "myzus", "sap sucking", "virus vector", "thiamethoxam", "lady beetle"]
    },
    {
        "id": "pest_004",
        "category": "pests",
        "title": "Whitefly in Cotton & Vegetables",
        "content": (
            "Whiteflies (Bemisia tabaci) are tiny white-winged pests on leaf undersides. They "
            "secrete honeydew causing sooty mould; more importantly transmit Cotton Leaf Curl Virus "
            "and Tomato Yellow Leaf Curl Virus. Hot dry weather favours outbreaks. "
            "Management: Yellow sticky traps at 10/acre. Spray spiromesifen 22.9 SC @ 750 ml/ha or "
            "acetamiprid 20 SP @ 150 g/ha. Avoid broad-spectrum pesticides that kill natural enemies. "
            "Crop rotation breaks the cycle."
        ),
        "keywords": ["whitefly", "bemisia tabaci", "leaf curl virus", "cotton whitefly", "yellow sticky trap", "sooty mould"]
    },
    {
        "id": "pest_005",
        "category": "pests",
        "title": "Red Cotton Bollworm",
        "content": (
            "Pink Bollworm (Pectinophora gossypiella) is the most serious internal feeder of "
            "cotton. Larvae bore into squares and bolls, causing rosette flowers and stained lint. "
            "Management: Pheromone traps (Gossyplure) at 5/ha for monitoring. "
            "Spray thiodicarb 75 WP @ 1 kg/ha or profenofos 50 EC @ 1 L/ha when moths exceed 8/trap/week. "
            "Bt-cotton (Bollgard II) has built-in resistance. Early sowing before August reduces risk."
        ),
        "keywords": ["bollworm", "pink bollworm", "pectinophora", "cotton boll", "gossyplure", "bt cotton", "rosette flower"]
    },
    {
        "id": "pest_006",
        "category": "pests",
        "title": "Stem Borer in Rice",
        "content": (
            "Yellow Stem Borer (Scirpophaga incertulas) causes 'dead heart' in vegetative stage "
            "and 'white ear' in reproductive stage. Moths lay egg masses covered with hairs on leaf blades. "
            "Management: Clip and destroy egg masses. Apply carbofuran 3G @ 33 kg/ha or "
            "chlorpyrifos 20 EC @ 1.25 L/ha at tillering. Biological: Trichogramma card release "
            "@ 50,000 eggs/ha. Avoid excess nitrogen which promotes pest build-up."
        ),
        "keywords": ["stem borer", "scirpophaga", "dead heart", "white ear", "trichogramma", "carbofuran", "egg mass"]
    },
    {
        "id": "pest_007",
        "category": "pests",
        "title": "Locust Swarms",
        "content": (
            "Desert Locust (Schistocerca gregaria) poses catastrophic risk when gregarious swarms "
            "invade from Rajasthan/Gujarat. A small swarm eats same food as 35,000 people daily. "
            "Early warning: solitary locusts entering from Pakistan border. "
            "Management: Immediate aerial/ground spraying with malathion 96 ULV @ 1.08 L/ha or "
            "lambda-cyhalothrin 10 CS @ 0.25 L/ha. Report sightings to district agriculture office. "
            "Government runs National Locust Warning Organisation (NLWO) for real-time alerts."
        ),
        "keywords": ["locust", "desert locust", "schistocerca", "swarm", "malathion", "nlwo", "rajasthan"]
    },

    # ─────────────────── FERTILIZERS ───────────────────
    {
        "id": "fert_001",
        "category": "fertilizers",
        "title": "Urea - Nitrogen Fertilizer",
        "content": (
            "Urea (46% N) is the most widely used nitrogen fertilizer in India. Apply in split "
            "doses to minimise volatilization: 50% basal + 25% tillering + 25% panicle initiation "
            "(for rice). For wheat: 1/3 at sowing + 1/3 at first irrigation + 1/3 at second irrigation. "
            "Neem-coated urea (NCU) slows nitrogen release by 10–15% improving efficiency. "
            "Recommended dose: 120–150 kg N/ha for most cereals. Avoid applying before heavy rain."
        ),
        "keywords": ["urea", "nitrogen", "ncу", "neem coated urea", "split dose", "volatilization", "basal dose"]
    },
    {
        "id": "fert_002",
        "category": "fertilizers",
        "title": "DAP - Diammonium Phosphate",
        "content": (
            "DAP (18% N, 46% P2O5) is the most popular phosphatic fertilizer. Recommended as "
            "basal dose at sowing/transplanting for cereals, oilseeds, and pulses. Apply 100–125 "
            "kg DAP/ha for wheat; 50–75 kg/ha for legumes. Enhances root development and early "
            "crop establishment. In alkaline soil (pH > 7.5), single super phosphate (SSP) is "
            "preferred. Government-subsidised under NFSA. Price capped by Government of India."
        ),
        "keywords": ["dap", "diammonium phosphate", "phosphorus", "p2o5", "basal dose", "root development", "ssp"]
    },
    {
        "id": "fert_003",
        "category": "fertilizers",
        "title": "Potash (MOP) Fertilizer",
        "content": (
            "Muriate of Potash (MOP, 60% K2O) improves disease resistance, water-use efficiency, "
            "and quality of produce. Critical for potassium-hungry crops: potato, banana, tobacco. "
            "Recommended dose: 40–60 kg K2O/ha for cereals, 80–100 kg/ha for potato. Apply at "
            "sowing or split with top-dressing. Sandy soils require more frequent small doses. "
            "Soil test–based application is recommended to avoid luxury consumption."
        ),
        "keywords": ["mop", "potash", "k2o", "potassium", "muriate", "disease resistance", "soil test"]
    },
    {
        "id": "fert_004",
        "category": "fertilizers",
        "title": "Organic Manures: FYM, Compost & Vermicompost",
        "content": (
            "Farm Yard Manure (FYM) at 10–15 tonnes/ha improves soil structure, water-holding "
            "capacity, and microbial activity. Compost is decomposed organic matter; carbon:nitrogen "
            "ratio should be 20–30:1. Vermicompost is produced by earthworms, richer in nutrients "
            "than FYM (N 2–3%, P 1.5–2.2%, K 1.8–2.4%). Apply 2–4 tonnes/ha. "
            "Biofertilizers (Rhizobium, Azotobacter, PSB) can reduce chemical fertilizer requirement "
            "by 20–30%."
        ),
        "keywords": ["fym", "compost", "vermicompost", "organic manure", "biofertilizer", "rhizobium", "azotobacter", "psb"]
    },
    {
        "id": "fert_005",
        "category": "fertilizers",
        "title": "Micronutrients: Zinc, Boron, Iron",
        "content": (
            "Zinc deficiency (khaira disease in rice) shows inter-veinal chlorosis on young leaves. "
            "Apply zinc sulphate @ 25 kg/ha basal or spray 0.5% ZnSO4. Boron is essential for "
            "pollen germination; critical in sunflower, groundnut, oilseeds. Apply borax @ 10 kg/ha. "
            "Iron deficiency (lime-induced chlorosis) in alkaline soils – spray FeSO4 0.5% + citric "
            "acid 0.1%. Soil test is the best guide for micronutrient application."
        ),
        "keywords": ["zinc", "boron", "iron", "micronutrient", "khaira disease", "zn deficiency", "zinc sulphate", "borax"]
    },
    {
        "id": "fert_006",
        "category": "fertilizers",
        "title": "Biofertilizers",
        "content": (
            "Biofertilizers are living organisms that enrich soil nutrients. Key types: "
            "Rhizobium (fixes N in legume roots, saves 80–200 kg N/ha), Azotobacter (free-living "
            "N-fixer for non-legumes), PSB – Phosphate Solubilising Bacteria (makes fixed P avail.), "
            "Mycorrhiza (enhances P and water uptake). "
            "Application: seed treatment (200 g/15 kg seed) or soil application (2–4 kg/ha with FYM). "
            "Avoid mixing with chemical fertilisers/fungicides simultaneously. Shelf life: 6 months."
        ),
        "keywords": ["biofertilizer", "rhizobium", "azotobacter", "psb", "mycorrhiza", "nitrogen fixation", "seed treatment"]
    },
    {
        "id": "fert_007",
        "category": "fertilizers",
        "title": "Drip Fertigation",
        "content": (
            "Fertigation delivers water-soluble fertilizers through drip irrigation directly to the "
            "root zone, improving efficiency by 30–50%. Use fully water-soluble grades: 19:19:19 or "
            "13:40:13 NPK starter; 12:61:0 MAP for phosphorus; potassium nitrate 13:0:45 for K. "
            "Key rules: flush system before/after fertigation; maintain EC 1.5–3 dS/m; use fertigation "
            "injector. Best for high-value crops: tomato, pepper, grapes, cotton, banana."
        ),
        "keywords": ["fertigation", "drip irrigation", "water soluble fertilizer", "map", "potassium nitrate", "ec", "19 19 19"]
    },

    # ─────────────────── GOVERNMENT SCHEMES ───────────────────
    {
        "id": "scheme_001",
        "category": "schemes",
        "title": "PM-KISAN - PM Kisan Samman Nidhi",
        "content": (
            "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) provides income support of ₹6,000 per year "
            "to eligible farmer families in three equal installments of ₹2,000. The scheme covers all "
            "landholding farmer families subject to certain exclusion criteria. "
            "Eligibility: Small and marginal farmers with cultivable land. "
            "How to apply: Visit pmkisan.gov.in, nearest CSC, or agriculture office. "
            "Documents: Aadhaar, bank account linked to Aadhaar, land records. "
            "Over 11 crore farmers enrolled as of 2024."
        ),
        "keywords": ["pm kisan", "pmkisan", "samman nidhi", "kisan", "income support", "6000 rupees", "csc", "aadhaar"]
    },
    {
        "id": "scheme_002",
        "category": "schemes",
        "title": "PMFBY - Pradhan Mantri Fasal Bima Yojana",
        "content": (
            "PMFBY is India's flagship crop insurance scheme. Farmers pay premium of only 2% for kharif, "
            "1.5% for rabi, and 5% for commercial/horticultural crops. Balance premium paid by State "
            "and Central Government. Coverage: pre-sowing to post-harvest losses due to natural calamities, "
            "pests, diseases. Losses assessed through crop cutting experiments. "
            "Enrol through banks, CSC, or intermediaries before cut-off date. "
            "Claims settled within 2 months. Rs. 1.55 lakh crore paid in claims since 2016."
        ),
        "keywords": ["pmfby", "fasal bima", "crop insurance", "premium", "kharif", "rabi", "natural calamity", "claim"]
    },
    {
        "id": "scheme_003",
        "category": "schemes",
        "title": "KCC - Kisan Credit Card",
        "content": (
            "Kisan Credit Card provides farmers timely access to credit for cultivation expenses, "
            "post-harvest expenses, and allied activities. Limit up to ₹3 lakh at 7% interest rate; "
            "effective rate 4% after 3% interest subvention for timely repayment. "
            "Eligibility: All farmers, sharecroppers, tenant farmers. "
            "Apply at: Any commercial bank, regional rural bank, or Cooperative bank. "
            "Documents: Land records/lease agreement, ID proof, Aadhaar. "
            "Validity: 5 years (renewable). ATM-enabled – withdraw any time."
        ),
        "keywords": ["kcc", "kisan credit card", "credit", "interest subvention", "crop loan", "rrb", "atm", "sharecropper"]
    },
    {
        "id": "scheme_004",
        "category": "schemes",
        "title": "eNAM - National Agriculture Market",
        "content": (
            "eNAM (e-National Agriculture Market) is an online trading platform for agricultural "
            "commodities. Farmers can sell produce to buyers across India to get better prices. "
            "Over 1,361 mandis across 23 states integrated on eNAM platform. "
            "Benefits: transparent price discovery, reduced intermediaries, payment directly to "
            "farmer's bank via NEFT/RTGS. The mobile app allows farmers to check real-time prices. "
            "Supported commodities: 175+ including wheat, pulses, vegetables. "
            "Register with APMC membership/Aadhaar at enam.gov.in."
        ),
        "keywords": ["enam", "national agriculture market", "msp", "mandi", "price discovery", "apmc", "trading", "online market"]
    },
    {
        "id": "scheme_005",
        "category": "schemes",
        "title": "Soil Health Card Scheme",
        "content": (
            "Soil Health Card provides crop-wise nutrient content status of the soil and recommends "
            "appropriate dosage of nutrients for improving soil health and fertility. Over 22 crore "
            "cards issued to farmers. "
            "The card advises on 12 parameters including: N, P, K, pH, organic carbon, "
            "micronutrients (Zn, Fe, Cu, Mn, B, S). "
            "Soil sampling: 1 sample per 2.5 ha (rainfed) or 1 per 1 ha (irrigated). "
            "Check card and apply fertilizer as recommended to save 15–20% on fertilizer costs."
        ),
        "keywords": ["soil health card", "soil test", "nutrients", "ph", "npk", "organic carbon", "micronutrients", "22 crore"]
    },
    {
        "id": "scheme_006",
        "category": "schemes",
        "title": "PMKSY - PM Krishi Sinchai Yojana",
        "content": (
            "PMKSY aims to ensure 'Har Khet Ko Pani, More Crop Per Drop'. It integrates Accelerated "
            "Irrigation Benefits Programme (AIBP), Har Khet Ko Pani, and Per Drop More Crop (PDMC). "
            "Subsidy: 55% for small/marginal farmers, 45% for others on drip and sprinkler irrigation. "
            "Components: construction of water sources, distribution network, micro-irrigation. "
            "Apply at district agriculture/horticulture office. Drip systems save 40–50% water while "
            "improving yield by 40–50%."
        ),
        "keywords": ["pmksy", "krishi sinchai", "drip subsidy", "micro irrigation", "har khet ko pani", "sprinkler", "aibp"]
    },
    {
        "id": "scheme_007",
        "category": "schemes",
        "title": "PKVY - Paramparagat Krishi Vikas Yojana",
        "content": (
            "PKVY promotes organic farming through cluster-based approach. Groups of 50 farmers "
            "form clusters of 50 acres each. Financial support: ₹50,000/ha over 3 years (₹31,000 "
            "for inputs, ₹8,800 for value addition, ₹3,000 for packaging, ₹7,200 for organic "
            "certification). PGS (Participatory Guarantee System) certification provided. "
            "Covers: seeds, manure, organic pesticides, soil amendments. Also linked with Ecomark "
            "and India Organic labels for better market access."
        ),
        "keywords": ["pkvy", "organic farming", "paramparagat", "pgs certification", "india organic", "cluster", "50000 per hectare"]
    },
    {
        "id": "scheme_008",
        "category": "schemes",
        "title": "MSP - Minimum Support Price",
        "content": (
            "Minimum Support Price (MSP) is the government's guaranteed price for agricultural "
            "commodities. CACP (Commission for Agricultural Costs and Prices) recommends MSP for "
            "23 mandated crops including cereals (14), oilseeds (7), pulses (2), and copra. "
            "Example MSP 2023–24: Paddy ₹2,183/quintal, Wheat ₹2,275/quintal, Gram ₹5,440/quintal. "
            "Procurement agencies: FCI, NAFED, State agencies. Farmers must register for procurement. "
            "Price Deficiency Payment (PDPS) given when market price < MSP in some states."
        ),
        "keywords": ["msp", "minimum support price", "cacp", "procurement", "fci", "nafed", "paddy msp", "wheat msp", "mandated crops"]
    },
    {
        "id": "scheme_009",
        "category": "schemes",
        "title": "RKVY - Rashtriya Krishi Vikas Yojana",
        "content": (
            "RKVY-RAFTAAR (Remunerative Approaches for Agriculture and Allied sector Rejuvenation) "
            "promotes agriculture and allied sectors' holistic development. Provides grants for: "
            "infrastructure, value chain, agri-startups (up to ₹25 lakh seed funding). "
            "States can choose projects based on local needs. Key focus: doubling farmers' income, "
            "skilling youth in agriculture, agri-entrepreneurship. Apply through State Agriculture "
            "Department. Funds released directly to state government."
        ),
        "keywords": ["rkvy", "rashtriya krishi vikas", "raftaar", "agriculture startup", "seed funding", "agri entrepreneurship", "doubling income"]
    },
    {
        "id": "scheme_010",
        "category": "schemes",
        "title": "PM Kusum Yojana - Solar Pump Scheme",
        "content": (
            "PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Uttham Mahabhiyan) provides solar "
            "pumps to farmers for irrigation. Three components: A (ground-mounted solar plants), "
            "B (stand-alone solar pumps), C (solarization of grid-connected pumps). "
            "Subsidy: 30% Central, 30% State; farmer pays only 30–40%. "
            "Eligible pump sizes: 3 HP to 7.5 HP. Farmers can also sell surplus solar power to DISCOM "
            "at ₹3–4/unit. Target: 25.75 lakh solar pumps by 2026. Apply at state nodal agency."
        ),
        "keywords": ["pm kusum", "solar pump", "solar irrigation", "discom", "surplus power", "3hp pump", "7.5hp", "kusum"]
    },
    {
        "id": "scheme_011",
        "category": "schemes",
        "title": "FPO - Farmer Producer Organisations",
        "content": (
            "FPOs (Farmer Producer Organisations) are collectives of farmers to achieve economies "
            "of scale in input procurement and output marketing. Government targets 10,000 FPOs by 2027-28 "
            "with ₹6,865 crore support. Each new FPO gets financial support: ₹18 lakh for 3 years plus "
            "matching equity grant up to ₹15 lakh and credit guarantee up to ₹2 crore. "
            "Benefits: bulk buying, better prices, access to institutional finance, processing units. "
            "Register with Registrar of Companies or State Cooperative Registrar."
        ),
        "keywords": ["fpo", "farmer producer", "collective farming", "10000 fpo", "equity grant", "credit guarantee", "economies of scale"]
    },

    # ─────────────────── SOIL & GENERAL ───────────────────
    {
        "id": "soil_001",
        "category": "general",
        "title": "Soil pH and Soil Management",
        "content": (
            "Soil pH determines nutrient availability. Most crops prefer pH 6–7.5. "
            "Acid soils (pH < 5.5): apply agricultural lime @ 2–4 tonnes/ha; dolomite for Mg-deficient soils. "
            "Alkaline soils (pH > 8): apply gypsum @ 5 tonnes/ha, sulphur @ 300 kg/ha, or press mud. "
            "Saline soils (EC > 4 dS/m): improve drainage; leach with fresh water. "
            "Sodic soils (ESP > 15%): gypsum reclamation + bio-drainage. "
            "Regular soil testing every 2–3 years is recommended."
        ),
        "keywords": ["soil ph", "acid soil", "alkaline soil", "saline", "sodic", "lime", "gypsum", "dolomite", "soil test"]
    },
    {
        "id": "soil_002",
        "category": "general",
        "title": "Integrated Pest Management (IPM)",
        "content": (
            "IPM is an ecosystem-based strategy for sustainable pest control combining biological, "
            "cultural, physical and chemical methods. Steps: 1) Monitor and identify pests using ETL "
            "(Economic Threshold Level). 2) Cultural control: crop rotation, sanitation, resistant varieties. "
            "3) Biological control: Trichogramma, NPV, predators. 4) Mechanical: pheromone traps, yellow "
            "sticky traps, light traps. 5) Chemical: selective pesticides as last resort. "
            "IPM reduces pesticide use by 40–60%, lowers costs and promotes ecology."
        ),
        "keywords": ["ipm", "integrated pest management", "etl", "biological control", "trichogramma", "npv", "pheromone", "crop rotation"]
    },
    {
        "id": "water_001",
        "category": "general",
        "title": "Water Management and Irrigation",
        "content": (
            "Efficient irrigation methods save 30–60% water over flood irrigation. "
            "Drip irrigation: best for row crops, 90% efficiency. Sprinkler: 75–80% efficiency for field crops. "
            "Furrow irrigation: 60–70% efficiency. Critical irrigation stages for wheat: CRI, tillering, "
            "jointing, flowering, grain fill. For rice: alternate wetting and drying (AWD) saves 30% water. "
            "Check soil moisture: finger test – if moist at 5 cm, no need to irrigate. "
            "Rainwater harvesting and farm ponds reduce dependency on groundwater."
        ),
        "keywords": ["irrigation", "drip", "sprinkler", "furrow", "awd", "water management", "farm pond", "rainwater harvesting"]
    },
    {
        "id": "weather_001",
        "category": "general",
        "title": "Weather Advisory for Farmers",
        "content": (
            "Mausam (weather) plays a critical role in farming decisions. Key advisories: "
            "Pre-monsoon (April–May): prepare land, store seeds. Kharif (June–Sep): sow with monsoon arrival; "
            "delay sowing during extended dry spells. Rabi (Oct–March): ideal for wheat, mustard, gram. "
            "Sources: Meghdoot app (block-level 5-day forecast), Damini app (lightning alerts), IMD Agromet "
            "advisories. Satellite-based crop monitoring via Fasal Bima portal. "
            "Extreme weather response: provide shade netting, windbreaks, and drain waterlogged fields."
        ),
        "keywords": ["weather", "monsoon", "meghdoot", "imd agromet", "kharif season", "rabi season", "lightning", "dry spell"]
    },
]


def get_all_documents():
    """Return all documents as (id, text) pairs for indexing."""
    docs = []
    for item in KNOWLEDGE_BASE:
        text = f"{item['title']}. {item['content']} Keywords: {', '.join(item['keywords'])}"
        docs.append((item["id"], text, item))
    return docs


def get_categories():
    return list({item["category"] for item in KNOWLEDGE_BASE})


def get_by_category(category: str):
    return [item for item in KNOWLEDGE_BASE if item["category"] == category]
