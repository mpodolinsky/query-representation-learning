# Task labels: routerbench

- queries: 36478
- taxonomy: v0.1.0
- model: `/scratch/11034/atzanakak/tmlr/hf_home/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137` (config sha256 `97e295b63283`), vLLM 0.27.1, prompt hash `e03f6842dd09706d`
- inconsistent level1/level2 pairs: 686 (1.88%)
- parse errors (level3 = PARSE_ERROR): 0 (0.00%)
- truncated queries: 22 (0.06%)
- distinct level3 phrases: 15228

## Level 1

| level1 | n | % |
|---|---|---|
| reasoning_commonsense | 11654 | 31.95 |
| math | 8560 | 23.47 |
| social_science_humanities | 4280 | 11.73 |
| business_economics_law | 3147 | 8.63 |
| medicine_biology | 2991 | 8.2 |
| natural_science | 2674 | 7.33 |
| language_writing | 917 | 2.51 |
| general_knowledge_trivia | 787 | 2.16 |
| chinese_language | 769 | 2.11 |
| code | 697 | 1.91 |
| other | 2 | 0.01 |

## Level 2

| level1 | level2 | n | % |
|---|---|---|---|
| business_economics_law | law_legal_reasoning | 1725 | 4.73 |
| business_economics_law | economics | 644 | 1.77 |
| business_economics_law | management_marketing | 388 | 1.06 |
| business_economics_law | accounting_auditing | 272 | 0.75 |
| business_economics_law | business_ethics_professional_conduct | 93 | 0.25 |
| business_economics_law | finance_investment | 23 | 0.06 |
| business_economics_law | other_business_economics_law | 1 | 0.0 |
| business_economics_law | politics_international_relations | 1 | 0.0 |
| chinese_language | zodiac_calendar_culture | 395 | 1.08 |
| chinese_language | classical_poetry | 152 | 0.42 |
| chinese_language | character_riddles | 120 | 0.33 |
| chinese_language | classical_literature_novels | 46 | 0.13 |
| chinese_language | idioms_homonyms_vocabulary | 37 | 0.1 |
| chinese_language | translation_chinese | 16 | 0.04 |
| chinese_language | translation_multilingual | 3 | 0.01 |
| code | implementation_from_spec | 331 | 0.91 |
| code | algorithms_data_structures | 182 | 0.5 |
| code | computer_science_theory_security | 142 | 0.39 |
| code | machine_learning_ai | 14 | 0.04 |
| code | systems_scripting_devops | 13 | 0.04 |
| code | other_code | 8 | 0.02 |
| code | sql_databases | 2 | 0.01 |
| code | web_frontend | 2 | 0.01 |
| code | code_explanation_review | 1 | 0.0 |
| code | debugging_fixing | 1 | 0.0 |
| code | information_extraction_formatting | 1 | 0.0 |
| general_knowledge_trivia | science_technology_facts | 374 | 1.03 |
| general_knowledge_trivia | entertainment_media_arts | 182 | 0.5 |
| general_knowledge_trivia | geography_places | 58 | 0.16 |
| general_knowledge_trivia | history_events_dates | 50 | 0.14 |
| general_knowledge_trivia | people_biography | 33 | 0.09 |
| general_knowledge_trivia | sports | 29 | 0.08 |
| general_knowledge_trivia | politics_organizations_awards | 24 | 0.07 |
| general_knowledge_trivia | other_trivia | 23 | 0.06 |
| general_knowledge_trivia | religion_mythology | 6 | 0.02 |
| general_knowledge_trivia | economics | 5 | 0.01 |
| general_knowledge_trivia | business_ethics_professional_conduct | 3 | 0.01 |
| language_writing | summarization_title_generation | 582 | 1.6 |
| language_writing | text_classification_analysis | 300 | 0.82 |
| language_writing | information_extraction_formatting | 10 | 0.03 |
| language_writing | creative_writing | 9 | 0.02 |
| language_writing | roleplay_conversation | 9 | 0.02 |
| language_writing | professional_writing | 3 | 0.01 |
| language_writing | grammar_editing_rewriting | 2 | 0.01 |
| language_writing | code_explanation_review | 1 | 0.0 |
| language_writing | translation_multilingual | 1 | 0.0 |
| math | arithmetic_word_problem | 7926 | 21.73 |
| math | probability_statistics | 249 | 0.68 |
| math | abstract_algebra_topology_advanced | 136 | 0.37 |
| math | algebra_precalculus | 77 | 0.21 |
| math | calculus_analysis | 54 | 0.15 |
| math | geometry_trigonometry | 33 | 0.09 |
| math | number_theory | 30 | 0.08 |
| math | linear_algebra | 27 | 0.07 |
| math | combinatorics_discrete_graph_theory | 23 | 0.06 |
| math | other_math | 5 | 0.01 |
| medicine_biology | clinical_medicine_diagnosis | 821 | 2.25 |
| medicine_biology | anatomy_physiology | 539 | 1.48 |
| medicine_biology | genetics_molecular_cell_biology | 451 | 1.24 |
| medicine_biology | psychology | 397 | 1.09 |
| medicine_biology | nutrition_public_health | 352 | 0.96 |
| medicine_biology | pharmacology_treatment | 160 | 0.44 |
| medicine_biology | microbiology_immunology_virology | 153 | 0.42 |
| medicine_biology | ecology_evolution_organismal_biology | 107 | 0.29 |
| medicine_biology | other_medicine_biology | 5 | 0.01 |
| medicine_biology | general_school_science | 3 | 0.01 |
| medicine_biology | ethics_moral_reasoning | 1 | 0.0 |
| medicine_biology | everyday_activity_completion | 1 | 0.0 |
| medicine_biology | sociology_anthropology | 1 | 0.0 |
| natural_science | general_school_science | 908 | 2.49 |
| natural_science | classical_physics | 520 | 1.43 |
| natural_science | general_physical_chemistry | 329 | 0.9 |
| natural_science | earth_environmental_science | 299 | 0.82 |
| natural_science | engineering_technology | 218 | 0.6 |
| natural_science | astronomy_astrophysics | 188 | 0.52 |
| natural_science | probability_statistics | 60 | 0.16 |
| natural_science | computer_science_theory_security | 59 | 0.16 |
| natural_science | machine_learning_ai | 44 | 0.12 |
| natural_science | modern_physics | 22 | 0.06 |
| natural_science | economics | 16 | 0.04 |
| natural_science | ecology_evolution_organismal_biology | 7 | 0.02 |
| natural_science | organic_chemistry | 3 | 0.01 |
| natural_science | geography_demography | 1 | 0.0 |
| other | mixed_multi_domain | 2 | 0.01 |
| reasoning_commonsense | everyday_activity_completion | 10071 | 27.61 |
| reasoning_commonsense | pronoun_coreference_resolution | 1265 | 3.47 |
| reasoning_commonsense | formal_logic_deduction | 145 | 0.4 |
| reasoning_commonsense | logical_fallacies_argument_analysis | 122 | 0.33 |
| reasoning_commonsense | science_technology_facts | 14 | 0.04 |
| reasoning_commonsense | other_reasoning | 13 | 0.04 |
| reasoning_commonsense | physical_social_commonsense | 12 | 0.03 |
| reasoning_commonsense | games_strategy_planning | 10 | 0.03 |
| reasoning_commonsense | abstract_pattern_induction | 1 | 0.0 |
| reasoning_commonsense | riddles_brain_teasers | 1 | 0.0 |
| social_science_humanities | ethics_moral_reasoning | 1258 | 3.45 |
| social_science_humanities | history | 840 | 2.3 |
| social_science_humanities | politics_international_relations | 598 | 1.64 |
| social_science_humanities | psychology | 554 | 1.52 |
| social_science_humanities | philosophy | 398 | 1.09 |
| social_science_humanities | sociology_anthropology | 218 | 0.6 |
| social_science_humanities | religion_mythology | 193 | 0.53 |
| social_science_humanities | geography_demography | 112 | 0.31 |
| social_science_humanities | other_social_science_humanities | 47 | 0.13 |
| social_science_humanities | economics | 28 | 0.08 |
| social_science_humanities | law_legal_reasoning | 27 | 0.07 |
| social_science_humanities | management_marketing | 4 | 0.01 |
| social_science_humanities | business_ethics_professional_conduct | 2 | 0.01 |
| social_science_humanities | history_events_dates | 1 | 0.0 |

## Theme x level 1

| theme | business_economics_law | chinese_language | code | general_knowledge_trivia | language_writing | math | medicine_biology | natural_science | other | reasoning_commonsense | social_science_humanities |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abstract2title | 0 | 0 | 0 | 0 | 253 | 0 | 0 | 0 | 0 | 0 | 0 |
| accounting_audit | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| arc-challenge | 3 | 0 | 0 | 145 | 0 | 18 | 95 | 1102 | 0 | 105 | 2 |
| bias_detection | 0 | 0 | 0 | 0 | 284 | 0 | 0 | 0 | 0 | 0 | 0 |
| chinese | 0 | 768 | 0 | 0 | 0 | 14 | 0 | 0 | 0 | 0 | 0 |
| consensus_summary | 0 | 0 | 0 | 1 | 331 | 0 | 24 | 0 | 2 | 0 | 0 |
| grade-school-math | 0 | 0 | 0 | 0 | 0 | 7450 | 0 | 0 | 0 | 0 | 0 |
| hellaswag | 2 | 0 | 3 | 1 | 4 | 0 | 14 | 1 | 0 | 10016 | 1 |
| mbpp | 0 | 0 | 423 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| mmlu | 3111 | 1 | 261 | 640 | 10 | 1065 | 2857 | 1563 | 0 | 256 | 4273 |
| mtbench | 1 | 0 | 10 | 0 | 35 | 11 | 1 | 8 | 0 | 10 | 4 |
| winogrande | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1267 | 0 |

## Top-3 level 2 per theme

| theme | level2 | n | share |
|---|---|---|---|
| abstract2title | summarization_title_generation | 253 | 100% |
| accounting_audit | accounting_auditing | 27 | 90% |
| accounting_audit | law_legal_reasoning | 3 | 10% |
| arc-challenge | general_school_science | 745 | 51% |
| arc-challenge | earth_environmental_science | 208 | 14% |
| arc-challenge | science_technology_facts | 157 | 11% |
| bias_detection | text_classification_analysis | 284 | 100% |
| chinese | zodiac_calendar_culture | 394 | 50% |
| chinese | classical_poetry | 152 | 19% |
| chinese | character_riddles | 120 | 15% |
| consensus_summary | summarization_title_generation | 329 | 92% |
| consensus_summary | pharmacology_treatment | 15 | 4% |
| consensus_summary | clinical_medicine_diagnosis | 5 | 1% |
| grade-school-math | arithmetic_word_problem | 7442 | 100% |
| grade-school-math | probability_statistics | 6 | 0% |
| grade-school-math | combinatorics_discrete_graph_theory | 1 | 0% |
| hellaswag | everyday_activity_completion | 10007 | 100% |
| hellaswag | clinical_medicine_diagnosis | 13 | 0% |
| hellaswag | other_reasoning | 4 | 0% |
| mbpp | implementation_from_spec | 316 | 74% |
| mbpp | algorithms_data_structures | 106 | 25% |
| mbpp | geometry_trigonometry | 2 | 0% |
| mmlu | law_legal_reasoning | 1747 | 12% |
| mmlu | ethics_moral_reasoning | 1258 | 9% |
| mmlu | psychology | 951 | 7% |
| mtbench | roleplay_conversation | 9 | 11% |
| mtbench | creative_writing | 8 | 10% |
| mtbench | information_extraction_formatting | 8 | 10% |
| winogrande | pronoun_coreference_resolution | 1265 | 100% |
| winogrande | everyday_activity_completion | 2 | 0% |

## Inconsistent pairs (level2 not under level1), top 15

| level1 | level2 | n |
|---|---|---|
| medicine_biology | psychology | 397 |
| natural_science | probability_statistics | 60 |
| natural_science | computer_science_theory_security | 59 |
| natural_science | machine_learning_ai | 44 |
| social_science_humanities | economics | 28 |
| social_science_humanities | law_legal_reasoning | 27 |
| natural_science | economics | 16 |
| reasoning_commonsense | science_technology_facts | 14 |
| natural_science | ecology_evolution_organismal_biology | 7 |
| general_knowledge_trivia | religion_mythology | 6 |
| general_knowledge_trivia | economics | 5 |
| social_science_humanities | management_marketing | 4 |
| chinese_language | translation_multilingual | 3 |
| medicine_biology | general_school_science | 3 |
| general_knowledge_trivia | business_ethics_professional_conduct | 3 |

## 15 random examples per level 1

### math (n=8560)

- `grade-school-math.dev.3053` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / money calculation: Carl wants to buy a new coat that is quite expensive. He saved $25 each week for 6 weeks. On the seventh week, he had to use a third of his saving to pay some bills. On the eighth week, [...] ive him?
- `grade-school-math.dev.5886` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / percent to total calculation: At a middle school, 20% of the students are in the band. If 168 students are in the band, how many students go to the middle school?
- `mmlu-elementary-mathematics.val.188` [mmlu/mmlu-elementary-mathematics] -> **arithmetic_word_problem** / solve linear equation: Please answer with the letter of the correct answer. Solve the equation −6x = −36. Check your answer. A) 6 B) 1 over 216 C) 1 over 6 D) 216 Print only a single choice from "A" or "B" or [...]  Answer:
- `grade-school-math.dev.5659` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / percentage and addition calculation: An online newspaper had listed 100 visitors in October. The number of visitors in November increased by 15%. There were 15 more visitors in December than in November. What is the total  [...]  months?
- `grade-school-math.dev.3346` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / money calculation: Susan had a sum of money. She spent 1/5 of it in September, 1/4 of it in October, and $120 in November. After spending these amounts of money, she still had $540 left. How much money di [...] t first?
- `grade-school-math.dev.725` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / toad count calculation: Tim has 30 toads. Jim has 20 more toads than Tim does. Sarah has twice as many toads as Jim does. How many toads does Sarah have?
- `grade-school-math.dev.807` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / age calculation: Yuan is 7 years older than his brother David and twice his age. How old is David?
- `grade-school-math.dev.1286` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / summing quantities: Olga has an aquarium with fish in 5 different colors. There are 12 yellow ones, half as many blue ones, and twice as many green ones as yellow ones. How many fish does Olga have in her aquarium?
- `grade-school-math.dev.4862` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / percentage and addition: In a 60-item exam, Liza got 90% of the items correctly. Her best friend, Rose, got 2 more correct answers than her. How many incorrect answers did Rose have?
- `grade-school-math.dev.4915` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / unit conversion per serving: Perry made a recipe that serves four people. He added a half cup of cream at the end. Cream has 88 grams of fat per cup. How many grams of fat were added to each serving of food?
- `mmlu-high-school-mathematics.val.53` [mmlu/mmlu-high-school-mathematics] -> **combinatorics_discrete_graph_theory** / pascal triangle element identification: Please answer with the letter of the correct answer. What is the second number in the row of Pascal's triangle that has 43 numbers? A) 43 B) 44 C) 42 D) 16 Print only a single choice fr [...]  Answer:
- `grade-school-math.dev.1550` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / percentage calculation: Hortense loves daisies and sunflowers. She planted 25 daisy seeds and 25 sunflower seeds in her flower bed. If 60% of the daisy seeds germinate, and 80% of the sunflower seeds germinate [...] flowers?
- `grade-school-math.dev.1097` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / percentage and subtraction calculation: Out of the 200 cookies that Javier baked from the recipe he learned online, his wife took 30%, and his daughter took 40 from the remaining cookies. If he ate half of the remaining cooki [...] not eat?
- `grade-school-math.dev.2325` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / solve for unknown price: George was selling some of his old toys on the internet. He managed to sell 3 little cars and a set of Legos. In total, he earned $45. How much did the Legos set cost, if one little car [...]  for $5?
- `grade-school-math.dev.5987` [grade-school-math/grade-school-math] -> **arithmetic_word_problem** / carbon emission comparison calculation: Marla is thinking about getting a canvas tote bag to avoid using plastic bags at the grocery store. If making the canvas bag released 600 pounds of carbon dioxide, each plastic bag rele [...]  pound.)

### code (n=697)

- `mbpp.dev.174` [mbpp/mbpp] -> **implementation_from_spec** / tuple element access: Write a function to get a colon of a tuple.
- `mbpp.dev.360` [mbpp/mbpp] -> **algorithms_data_structures** / recursive geometric sum calculation: Write a function to calculate the geometric sum of n-1. https://www.w3resource.com/python-exercises/data-structures-and-algorithms/python-recursion-exercise-9.php
- `mmlu-computer-security.val.92` [mmlu/mmlu-computer-security] -> **computer_science_theory_security** / ip spoofing detection: Please answer with the letter of the correct answer. How is IP address spoofing detected? A) Implementing a firewall to the network B) Identify all TCP sessions that are initiated but d [...]  Answer:
- `mbpp.dev.284` [mbpp/mbpp] -> **implementation_from_spec** / interleave lists: Write a function to interleave 3 lists of the same length into a single flat list.
- `mmlu-high-school-computer-science.val.2` [mmlu/mmlu-high-school-computer-science] -> **computer_science_theory_security** / network file transmission: Please answer with the letter of the correct answer. A user enters a Web address in a browser, and a request for a file is sent to a Web server. Which of the following best describes ho [...]  Answer:
- `mbpp.dev.109` [mbpp/mbpp] -> **algorithms_data_structures** / array element rearrangement: Write a function that takes in an array and an integer n, and re-arranges the first n elements of the given array so that all negative elements appear before positive ones, and where th [...] eserved.
- `mbpp.dev.349` [mbpp/mbpp] -> **information_extraction_formatting** / extract quoted values: Write a function to extract values between quotation marks " " of the given string.
- `mbpp.dev.150` [mbpp/mbpp] -> **implementation_from_spec** / tuple element counting: Write a function to find the number of elements that occurs before the tuple element in the given tuple.
- `mbpp.dev.0` [mbpp/mbpp] -> **implementation_from_spec** / shared elements in lists: Write a function to find the shared elements from the given two lists.
- `mbpp.dev.112` [mbpp/mbpp] -> **implementation_from_spec** / calculate lateral surface area: Write a function to find the lateral surface area of a cylinder.
- `mbpp.dev.204` [mbpp/mbpp] -> **implementation_from_spec** / check value in sequence: Write a python function to check whether any value in a sequence exists in a sequence or not.
- `mbpp.dev.145` [mbpp/mbpp] -> **implementation_from_spec** / extract tuple elements: Write a function that takes in a list of tuples and returns a list containing the rear element of each tuple.
- `mbpp.dev.5` [mbpp/mbpp] -> **implementation_from_spec** / square list elements: Write a function to find squares of individual elements in a list.
- `mbpp.dev.397` [mbpp/mbpp] -> **algorithms_data_structures** / list packing: Write a function to pack consecutive duplicates of a given list elements into sublists.
- `mmlu-college-computer-science.val.78` [mmlu/mmlu-college-computer-science] -> **computer_science_theory_security** / cache memory policy analysis: Please answer with the letter of the correct answer. The hit ratio of a cache memory is the percentage of accesses (reads and writes) for which data are found in the cache. Write-throug [...]  Answer:

### natural_science (n=2674)

- `arc-challenge.val.25` [arc-challenge/arc-challenge] -> **earth_environmental_science** / ecological succession prediction: A volcano erupts and covers the surrounding area with lava and volcanic ash. As the ecosystem begins to recover, which type of plant will most likely be the first to colonize land in th [...]  Answer:
- `mmlu-conceptual-physics.val.134` [mmlu/mmlu-conceptual-physics] -> **classical_physics** / time dilation effect: Please answer with the letter of the correct answer. If you travel at high speed, then compared with your friends who “stay at home,” you are A) neither younger nor older. B) older. C)  [...]  Answer:
- `mmlu-high-school-physics.val.42` [mmlu/mmlu-high-school-physics] -> **classical_physics** / gravitational oscillation analysis: Please answer with the letter of the correct answer. Pretend someone actually managed to dig a hole straight through the center of the Earth all the way to the other side. If an object  [...]  Answer:
- `mmlu-high-school-microeconomics.val.165` [mmlu/mmlu-high-school-microeconomics] -> **general_school_science** / economics demand curve: Please answer with the letter of the correct answer. The demand curve for a perfectly competitive firm's product is A) perfectly elastic. B) kinked at the going market price. C) downwar [...]  Answer:
- `mmlu-astronomy.val.122` [mmlu/mmlu-astronomy] -> **astronomy_astrophysics** / planet tectonics identification: Please answer with the letter of the correct answer. Which planet(s) in the solar system has/have active plate tectonics? A) Mars B) Earth C) Mars and Earth D) Venus Print only a single [...]  Answer:
- `mmlu-conceptual-physics.val.91` [mmlu/mmlu-conceptual-physics] -> **classical_physics** / conceptual physics question: Please answer with the letter of the correct answer. When you buy a pipe in a hardware store, the water isn’t included. When you buy copper wire, electrons A) None of these B) must be s [...]  Answer:
- `mmlu-electrical-engineering.val.87` [mmlu/mmlu-electrical-engineering] -> **engineering_technology** / microprocessor component identification: Please answer with the letter of the correct answer. A microprocessor is ALU A) and control unit on a single chip. B) register unit and control unit on a single chip. C) and memory on a [...]  Answer:
- `mmlu-high-school-chemistry.val.121` [mmlu/mmlu-high-school-chemistry] -> **general_physical_chemistry** / acid-base reaction ph calculation: Please answer with the letter of the correct answer. A 50.0 mL sample of 0.0025 M HBr is mixed with 50.0 mL of 0.0023 M KOH. What is the pH of the resulting mixture? A) 4 B) 1 C) 5 D) 1 [...]  Answer:
- `mmlu-electrical-engineering.val.49` [mmlu/mmlu-electrical-engineering] -> **engineering_technology** / electrical engineering calculation: Please answer with the letter of the correct answer. An SCR has half cycle surge current rating of 3000 A for 50 Hz supply. One cycle surge current will be A) 6000 A. B) 1500 A. C) 4242 [...]  Answer:
- `arc-challenge.val.294` [arc-challenge/arc-challenge] -> **general_school_science** / mass conservation in reactions: The equation below shows the products formed when a solution of silver nitrate (AgNO3) reacts with a solution of sodium chloride (NaCl). AgNO3 + NaCl (Reactants) -> NaNO3 + AgCl (Prod [...]  Answer:
- `arc-challenge.test.953` [arc-challenge/arc-challenge] -> **general_school_science** / science experiment explanation: Greta passed a comb through her hair several times. She then placed the comb next to a stream of water flowing from a faucet. Greta observed the stream of water bend toward the comb. Ho [...]  Answer:
- `mmlu-machine-learning.val.7` [mmlu/mmlu-machine-learning] -> **computer_science_theory_security** / probability_distribution_validation: Please answer with the letter of the correct answer. Statement 1\| For a continuous random variable x and its probability distribution function p(x), it holds that 0 ≤ p(x) ≤ 1 for all  [...]  Answer:
- `mmlu-college-physics.val.40` [mmlu/mmlu-college-physics] -> **classical_physics** / power dissipation calculation: Please answer with the letter of the correct answer. A resistor in a circuit dissipates energy at a rate of 1 W. If the voltage across the resistor is doubled, what will be the new rate [...]  Answer:
- `mmlu-high-school-physics.val.109` [mmlu/mmlu-high-school-physics] -> **classical_physics** / electric magnetic field analysis: Please answer with the letter of the correct answer. Which of the following statements about electric and magnetic fields is FALSE: A) All charges experience a force in an electric fiel [...]  Answer:
- `arc-challenge.test.38` [arc-challenge/arc-challenge] -> **general_school_science** / biology function identification: What is the main function of photosynthetic cells within a plant? A) to convert energy from sunlight into food energy B) to break down sugar into usable chemicals C) to allow the passag [...]  Answer:

### medicine_biology (n=2991)

- `mmlu-college-medicine.val.63` [mmlu/mmlu-college-medicine] -> **anatomy_physiology** / cell cycle phase comparison: Please answer with the letter of the correct answer. Which of the following phases are common to cells undergoing meiosis and mitosis? I. G0 II. phase G2 III. phase S phase A) II and II [...]  Answer:
- `mmlu-high-school-psychology.val.230` [mmlu/mmlu-high-school-psychology] -> **psychology** / theoretical reasoning: Please answer with the letter of the correct answer. According to Kohlberg, in order to reason at the postconventional level, people must A) believe in God. B) have had a successful res [...]  Answer:
- `mmlu-nutrition.val.67` [mmlu/mmlu-nutrition] -> **nutrition_public_health** / foodborne illness causes: Please answer with the letter of the correct answer. The two most common causes of foodborne illness in the United States and Europe are: A) Listeria and Salmonella B) Shigella and Stap [...]  Answer:
- `mmlu-professional-medicine.val.172` [mmlu/mmlu-professional-medicine] -> **genetics_molecular_cell_biology** / genetic inheritance calculation: Please answer with the letter of the correct answer. A couple comes for preconceptional genetic counseling because they both have a family history of α-thalassemia. The woman has a mini [...]  Answer:
- `mmlu-moral-disputes.val.5` [mmlu/mmlu-moral-disputes] -> **other_medicine_biology** / cloning terminology recall: Please answer with the letter of the correct answer. What does SCNT stand for, as used in the discussion on cloning? A) stem cell nuclear transmission B) somatic cell nuclear transfer C [...]  Answer:
- `mmlu-anatomy.val.108` [mmlu/mmlu-anatomy] -> **anatomy_physiology** / anatomy function identification: Please answer with the letter of the correct answer. The thoracic cage is a structural unit important for which of the following functions? A) Menstruation B) Respiration C) Alimentatio [...]  Answer:
- `mmlu-professional-medicine.val.252` [mmlu/mmlu-professional-medicine] -> **clinical_medicine_diagnosis** / renal failure treatment consideration: Please answer with the letter of the correct answer. A 78-year-old woman is admitted to the hospital for replacement of her left knee joint due to degenerative joint disease. She has ty [...]  Answer:
- `mmlu-high-school-psychology.val.177` [mmlu/mmlu-high-school-psychology] -> **genetics_molecular_cell_biology** / chromosome abnormality identification: Please answer with the letter of the correct answer. The most common form of Down syndrome results during sex cell formation and fertilization from A) failure of the separation of XX B) [...]  Answer:
- `mmlu-college-medicine.val.104` [mmlu/mmlu-college-medicine] -> **anatomy_physiology** / cellular process location: Please answer with the letter of the correct answer. The enzymes of glycolysis are located in the: A) cytoplasm. B) nucleus. C) mitochondrion. D) lysosomes. Print only a single choice f [...]  Answer:
- `mmlu-high-school-government-and-politics.val.84` [mmlu/mmlu-high-school-government-and-politics] -> **pharmacology_treatment** / legal basis for medical rights: Please answer with the letter of the correct answer. Which of the following was the legal basis for the 1973 Roe v. Wade majority opinion, in which the Supreme Court struck down a state [...]  Answer:
- `mmlu-high-school-biology.val.264` [mmlu/mmlu-high-school-biology] -> **genetics_molecular_cell_biology** / glycolysis purpose identification: Please answer with the letter of the correct answer. Many different fermentation pathways occur in different organisms in nature. For example, skeletal muscle cells convert pyruvate int [...]  Answer:
- `mmlu-professional-psychology.val.146` [mmlu/mmlu-professional-psychology] -> **psychology** / concept identification: Please answer with the letter of the correct answer. The match between a child’s temperament and the demands and responses of the environment in which she develops is known as _________ [...]  Answer:
- `mmlu-anatomy.val.83` [mmlu/mmlu-anatomy] -> **anatomy_physiology** / anatomy identification: Please answer with the letter of the correct answer. Which of the following closes and seals off the lower airway during swallowing? A) Larynx B) Uvula C) Epiglottis D) Alveoli Print on [...]  Answer:
- `mmlu-high-school-biology.val.239` [mmlu/mmlu-high-school-biology] -> **anatomy_physiology** / tissue characteristic comparison: Please answer with the letter of the correct answer. The major difference between cartilage and bone is that cartilage A) lacks blood vessels and nerves B) is a part of the skeletal sys [...]  Answer:
- `mmlu-professional-psychology.val.384` [mmlu/mmlu-professional-psychology] -> **psychology** / language development factors: Please answer with the letter of the correct answer. Which is NOT a contributor to individual differences in the development of vocal language skills? A) The quality of nonparental earl [...]  Answer:

### social_science_humanities (n=4280)

- `mmlu-high-school-us-history.val.79` [mmlu/mmlu-high-school-us-history] -> **history** / us constitution formation: Please answer with the letter of the correct answer. This question refers to the following information. "Some men look at constitutions with sanctimonious reverence, and deem them like  [...]  Answer:
- `mmlu-world-religions.val.82` [mmlu/mmlu-world-religions] -> **religion_mythology** / caste group identification: Please answer with the letter of the correct answer. The kshatriyas is the caste name assigned to which group? A) Priests B) Servants C) Rulers, warriors D) Merchants Print only a singl [...]  Answer:
- `mmlu-jurisprudence.val.4` [mmlu/mmlu-jurisprudence] -> **philosophy** / political philosophy analysis: Please answer with the letter of the correct answer. Which proposition below is the most consistent with what Rawls claims the POP would opt for in respect of 'social primary goods'? A) [...]  Answer:
- `mmlu-moral-scenarios.val.672` [mmlu/mmlu-moral-scenarios] -> **ethics_moral_reasoning** / moral scenario evaluation: Please answer with the letter of the correct answer. For which of these two scenarios does the main character (who uses I/me/my) do something clearly morally wrong, according to ordinar [...]  Answer:
- `mmlu-high-school-us-history.val.136` [mmlu/mmlu-high-school-us-history] -> **history** / us history event identification: Please answer with the letter of the correct answer. This question refers to the following information. "Is there no danger to our liberty and independence in a bank that in its nature  [...]  Answer:
- `mmlu-us-foreign-policy.val.42` [mmlu/mmlu-us-foreign-policy] -> **politics_international_relations** / american exceptionalism analysis: Please answer with the letter of the correct answer. Why might the 'Philadelphian System' be linked to the idea of American exceptionalism? A) It was designed as the antithesis of Europ [...]  Answer:
- `mmlu-moral-scenarios.val.715` [mmlu/mmlu-moral-scenarios] -> **ethics_moral_reasoning** / moral scenario evaluation: Please answer with the letter of the correct answer. For which of these two scenarios does the main character (who uses I/me/my) do something clearly morally wrong, according to ordinar [...]  Answer:
- `mmlu-moral-disputes.val.35` [mmlu/mmlu-moral-disputes] -> **ethics_moral_reasoning** / moral dispute fact recall: Please answer with the letter of the correct answer. The annual death-toll from poverty related causes is, according to Pogge, A) around one quarter of all human deaths. B) none of the  [...]  Answer:
- `mmlu-high-school-geography.val.140` [mmlu/mmlu-high-school-geography] -> **geography_demography** / caste system knowledge: Please answer with the letter of the correct answer. Which one of the following groups is excluded from the caste system of Hinduism? A) Scholar-priests B) Businessmen and farmers C) Un [...]  Answer:
- `mmlu-prehistory.val.105` [mmlu/mmlu-prehistory] -> **history** / prehistoric human intellect indicators: Please answer with the letter of the correct answer. Which of the following most strongly indicates advances in the human intellect during the Upper Paleolithic? A) acquisition of non-l [...]  Answer:
- `mmlu-sociology.val.145` [mmlu/mmlu-sociology] -> **sociology_anthropology** / community type identification: Please answer with the letter of the correct answer. Which of the following is not identified as a new form of community? A) gay villages, which are formed in certain parts of large cit [...]  Answer:
- `mmlu-high-school-government-and-politics.val.160` [mmlu/mmlu-high-school-government-and-politics] -> **politics_international_relations** / federalism concept identification: Please answer with the letter of the correct answer. Which of the following statements best characterizes cooperative federalism? A) The federal government granting power over a policy  [...]  Answer:
- `mmlu-prehistory.val.93` [mmlu/mmlu-prehistory] -> **history** / archaeology terminology: Please answer with the letter of the correct answer. Artifacts _________; ecofacts __________ A) are made by humans; exhibit traces of human activity. B) decay rapidly; last for a long  [...]  Answer:
- `mmlu-sociology.val.131` [mmlu/mmlu-sociology] -> **sociology_anthropology** / concept definition recall: Please answer with the letter of the correct answer. With industrial capitalism, leisure emerged as a concept that meant: A) regulated and organized activities to reduce social disorder [...]  Answer:
- `mmlu-moral-scenarios.val.88` [mmlu/mmlu-moral-scenarios] -> **ethics_moral_reasoning** / moral scenario evaluation: Please answer with the letter of the correct answer. For which of these two scenarios does the main character (who uses I/me/my) do something clearly morally wrong, according to ordinar [...]  Answer:

### business_economics_law (n=3147)

- `mmlu-professional-law.val.891` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / contract mistake enforcement: Please answer with the letter of the correct answer. An avid stamp collector had amassed a large and valuable collection. Many of his stamps were extremely rare and highly coveted. On n [...]  Answer:
- `mmlu-business-ethics.val.24` [mmlu/mmlu-business-ethics] -> **business_ethics_professional_conduct** / multiple choice question: Please answer with the letter of the correct answer. Better access to certain markets, differentiation of products, and the sale of pollution-control technology are ways in which better [...]  Answer:
- `mmlu-high-school-microeconomics.val.174` [mmlu/mmlu-high-school-microeconomics] -> **economics** / microeconomics concept identification: Please answer with the letter of the correct answer. Deadweight loss occurs in A) monopoly markets because P > MC. B) All of the above. C) monopolistic competition as P > MC. D) oligopo [...]  Answer:
- `mmlu-marketing.val.19` [mmlu/mmlu-marketing] -> **management_marketing** / marketing theory identification: Please answer with the letter of the correct answer. Advertising is employed as a defence, to retain customers, and to increase brand usage. Advertising is used to reinforce existing at [...]  Answer:
- `mmlu-professional-accounting.val.34` [mmlu/mmlu-professional-accounting] -> **law_legal_reasoning** / agency law question: Please answer with the letter of the correct answer. Long was a purchasing agent for Frost, a sole proprietor. Long had express authority to place purchase orders with Frost's suppliers [...]  Answer:
- `mmlu-professional-law.val.1350` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / contract formation analysis: Please answer with the letter of the correct answer. Berg offered to sell a parcel of land to Jones for $75,000 cash. The offer was in writing on March 1 and made by sending an e-mail t [...]  Answer:
- `mmlu-professional-accounting.val.190` [mmlu/mmlu-professional-accounting] -> **accounting_auditing** / unrealized gain loss recognition: Please answer with the letter of the correct answer. Dodd Co.'s debt securities at December 31 included available-for-sale securities with a cost basis of $24000 and a fair value of $30 [...]  Answer:
- `mmlu-professional-accounting.val.147` [mmlu/mmlu-professional-accounting] -> **accounting_auditing** / tax amortization rules: Please answer with the letter of the correct answer. Which of the following cannot be amortized for tax purposes? A) Temporary directors’ fees. B) Incorporation costs. C) Organizational [...]  Answer:
- `mmlu-professional-law.val.913` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / attorney privilege determination: Please answer with the letter of the correct answer. A husband and his wife are involved in a contested divorce and child custody battle. Ignorant of the adversarial system, they both v [...]  Answer:
- `mmlu-professional-law.val.1304` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / property rights determination: Please answer with the letter of the correct answer. On February 1, a woman conveys her farm to a man, and the man duly records the conveyance. The following day, the man conveys the pr [...]  Answer:
- `mmlu-professional-law.val.1006` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / criminal law analysis: Please answer with the letter of the correct answer. Howard did not know it, but his wife was having an affair with another man. One day Howard came home early from work and caught his  [...]  Answer:
- `mmlu-professional-accounting.val.252` [mmlu/mmlu-professional-accounting] -> **accounting_auditing** / accounts receivable calculation: Please answer with the letter of the correct answer. Kanji Company had sales last year of $265 million, including cash sales of $25 million. If its average collection period was 36 days [...]  Answer:
- `mmlu-econometrics.val.29` [mmlu/mmlu-econometrics] -> **economics** / regression function identification: Please answer with the letter of the correct answer. Which of the following statements is true concerning the population regression function (PRF) and sample regression function (SRF)?  [...]  Answer:
- `mmlu-public-relations.val.74` [mmlu/mmlu-public-relations] -> **management_marketing** / marketing campaign evaluation: Please answer with the letter of the correct answer. Which type of measurement is the most effective choice for evaluating a campaign's impact on audience attitudes? A) studying the con [...]  Answer:
- `mmlu-professional-law.val.906` [mmlu/mmlu-professional-law] -> **law_legal_reasoning** / criminal law analysis: Please answer with the letter of the correct answer. A man was at a party where he observed a female guest who had passed out and was unconscious and alone in a bedroom of the house. Th [...]  Answer:

### language_writing (n=917)

- `mtbench.dev.40` [mtbench/mtbench] -> **creative_writing** / film recommendation with descriptions: Suggest five award-winning documentary films with brief background descriptions for aspiring filmmakers to study.
- `abstract2title.test.192` [abstract2title/abstract2title] -> **summarization_title_generation** / scientific abstract to title: Carbon-based perovskite solar cells aroused huge attention for their simple, low-cost device fabrication processing and excellent stability. However, the fully low-temperature preparati [...] devices.
- `consensus_summary.dev.35` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: The findings of the present review suggest that exercise therapy may improve HRV in myocardial infarction, chronic heart failure and revascularization patients by increasing vaga [...] ase HRV?
- `consensus_summary.dev.68` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: Because more states are likely to pass legislation legalizing medical and recreational use of marijuana, increased efforts to establish child-focused safety requirements regardin [...] hildren?
- `consensus_summary.dev.346` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: We observed consistent beneficial effects of grounding in domains highly relevant to massage therapists, namely pain, physical function, and mood. claim: Grounding could become i [...] ractice?
- `consensus_summary.dev.76` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: Furthermore, we find consistent evidence that the support of the crowd tends to bias referee’s decisions (in terms of penalties, red cards, and yellow cards) in favor of the home [...] ee bias?
- `mtbench-reference.dev.0` [mtbench/mtbench-reference] -> **translation_multilingual** / translation and refinement: Please assume the role of an English translator, tasked with correcting and enhancing spelling and language. Regardless of the language I use, you should identify it, translate it, and  [...] 伊消得人憔悴".
- `abstract2title.test.25` [abstract2title/abstract2title] -> **summarization_title_generation** / abstract to title: For perovskite solar cells, thermal treatment of perovskite/PCBM layer is typically required for facilitated charge extraction, thereby eliminating the notorious photocurrent hysteresis [...] r cells.
- `consensus_summary.dev.169` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: These data suggest that applying a ketogenic diet or exploiting cellular mechanisms associated with ketone-based metabolism offers new therapeutic opportunities for controlling p [...] to diet?
- `consensus_summary.dev.221` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary: claim: Evidence exists indicating that increased brain creatine may be effective at reducing the severity of, or enhancing recovery from mild traumatic brain injury, however, only limit [...] ecovery?
- `consensus_summary.dev.75` [consensus_summary/consensus_summary] -> **summarization_title_generation** / consensus summary generation: claim: Overall, these results demonstrated that a single administration of creatine improves working memory efficiency, and, when co-administrated with l-arginine, improves reference me [...] gnition?
- `abstract2title.test.206` [abstract2title/abstract2title] -> **summarization_title_generation** / abstract to title: Organic-inorganic inverted perovskite solar cells have been analyzed. This structure uses organic semiconductors as electron and hole selective electrodes and the perovskite as light ha [...] ut ∼10%.
- `abstract2title.test.197` [abstract2title/abstract2title] -> **summarization_title_generation** / abstract to title: The effect of transparent conductive oxide (TCO) on the performance of compact-layer free perovskite solar cells has been investigated. The results show that the perovskite film formati [...] ormance.
- `abstract2title.test.11` [abstract2title/abstract2title] -> **summarization_title_generation** / abstract to title: Organic-inorganic hybrid perovskites have recently attracted substantial attention as a top candidate for use as light-absorbing materials in high-efficiency, low-cost and solution-proc [...] ormance.
- `abstract2title.test.166` [abstract2title/abstract2title] -> **summarization_title_generation** / abstract to title: Due to its super thermal stability, inorganic CsPbI2Br perovskite has attracted more and more attention in the field of photovoltaic application. However, its device performance, as rep [...] r cells.

### general_knowledge_trivia (n=787)

- `mmlu-global-facts.val.61` [mmlu/mmlu-global-facts] -> **geography_places** / country fact recall: Please answer with the letter of the correct answer. Different less developed countries have different levels of secondary school enrollment. Some countries with high secondary-school e [...]  Answer:
- `mmlu-miscellaneous.val.698` [mmlu/mmlu-miscellaneous] -> **entertainment_media_arts** / horse racing terminology: Please answer with the letter of the correct answer. In horse racing what is the term for a wager on the 1st 2nd and 3rd place finishers in a specific race? A) triple crown B) trifecta  [...]  Answer:
- `mmlu-miscellaneous.val.744` [mmlu/mmlu-miscellaneous] -> **politics_organizations_awards** / un official language identification: Please answer with the letter of the correct answer. Which of these is not one of the official languages of the United Nations? A) Japanese B) English C) Spanish D) Russian Print only a [...]  Answer:
- `arc-challenge.test.840` [arc-challenge/arc-challenge] -> **science_technology_facts** / unit identification: The weight of an object changes at different locations on Earth. Which is a measurement of weight? A) 16 N B) 20 mL C) 45 m D) 90°C Print only a single choice from "A" or "B" or "C" or  [...]  Answer:
- `arc-challenge.test.945` [arc-challenge/arc-challenge] -> **science_technology_facts** / fuel type identification: In 1995, a private bus company in Washington, D.C., introduced a program to run all its tour buses with fuel obtained from soybeans. The buses are powered by A) biogas. B) nuclear fuel. [...]  Answer:
- `mmlu-miscellaneous.val.440` [mmlu/mmlu-miscellaneous] -> **entertainment_media_arts** / film author identification: Please answer with the letter of the correct answer. The film 'Stand By Me' is based on a novel by what author? A) Dean Koontz B) Anne Proulx C) Frank McCourt D) Stephen King Print only [...]  Answer:
- `arc-challenge.test.239` [arc-challenge/arc-challenge] -> **science_technology_facts** / experiment repetition step: Which step should a student do in order to be able to repeat an experiment? A) do the experiment many times B) keep a record of all procedures C) make a model of the set-up of the exper [...]  Answer:
- `mmlu-miscellaneous.val.477` [mmlu/mmlu-miscellaneous] -> **entertainment_media_arts** / magazine focus identification: Please answer with the letter of the correct answer. Which of these magazines does not focus on natural science? A) Outside B) Smithsonian C) National Geographic D) Tiger Beat Print onl [...]  Answer:
- `mmlu-miscellaneous.val.304` [mmlu/mmlu-miscellaneous] -> **geography_places** / statue of liberty fact recall: Please answer with the letter of the correct answer. How many spikes are on the Statue of Liberty's crown? A) thirteen B) seven C) five D) nine Print only a single choice from "A" or "B [...]  Answer:
- `mmlu-global-facts.val.34` [mmlu/mmlu-global-facts] -> **politics_organizations_awards** / historical election fact recall: Please answer with the letter of the correct answer. Ross Perot makes polling history by leading the presidential race briefly in June as a third-party candidate with 39%. He winds up w [...]  Answer:
- `mmlu-miscellaneous.val.89` [mmlu/mmlu-miscellaneous] -> **sports** / baseball figure identification: Please answer with the letter of the correct answer. Which of these famous baseball figures was once acquitted at court-martial for insubordination? A) Ty Cobb B) Abner Doubleday C) Jac [...]  Answer:
- `mmlu-miscellaneous.val.187` [mmlu/mmlu-miscellaneous] -> **religion_mythology** / patron saint identification: Please answer with the letter of the correct answer. Who is the patron saint of animals? A) St Francis of Assisi B) St Joan of Arc C) St Isidore of Seville D) St Anthony of Padua Print  [...]  Answer:
- `mmlu-miscellaneous.val.599` [mmlu/mmlu-miscellaneous] -> **entertainment_media_arts** / nursery rhyme recall: Please answer with the letter of the correct answer. According to the Mother Goose nursery rhyme which child is full of woe? A) Saturday's child B) Thursday's child C) Monday's child D) [...]  Answer:
- `mmlu-miscellaneous.val.206` [mmlu/mmlu-miscellaneous] -> **entertainment_media_arts** / horse measurement unit recall: Please answer with the letter of the correct answer. When it comes to measuring horses how long is a 'hand'? A) two feet B) four inches C) ten inches D) seven inches Print only a single [...]  Answer:
- `mmlu-miscellaneous.val.76` [mmlu/mmlu-miscellaneous] -> **science_technology_facts** / greek alphabet knowledge: Please answer with the letter of the correct answer. What's the third letter of the Greek alphabet? A) delta B) gamma C) theta D) phi Print only a single choice from "A" or "B" or "C" o [...]  Answer:

### reasoning_commonsense (n=11654)

- `hellaswag.val.4477` [hellaswag/hellaswag] -> **everyday_activity_completion** / hair coloring decision: [header] How to lowlight blonde hair [title] Decide how dark you want to go. [step] Highlights are a few shades lighter than your hair, while lowlights are a few shades darker. If you w [...]  Answer:
- `hellaswag.val.7422` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete diy instructions: [header] How to make an adult blanket sleeper [title] Create your blanket sleeper's pattern. [step] Lay several feet worth of untouched christmas wrapping paper down on a large flat sur [...]  Answer:
- `hellaswag.val.6058` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete instruction with example: [header] How to remember long numbers [title] Look for shapes within your number. [step] Part of what makes numbers difficult to remember is that they are symbols that don't actually co [...]  Answer:
- `hellaswag.val.5381` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete hair care step: [header] How to enhance your hair color using tea [title] Brew chamomile tea to gently lighten. [step] Steep 2-3 tea bags of pure chamomile tea in a cup of boiling water for 10 minutes. [...]  Answer:
- `hellaswag.val.9705` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete computer task steps: [header] How to unblock flash player [title] Launch google chrome. [step] Just click on the desktop icon on your computer to launch google chrome. Once the browser is open, click on the [...]  Answer:
- `winogrande.dev.1063` [winogrande/winogrande] -> **pronoun_coreference_resolution** / pronoun resolution: Learning a new form of karate was difficult for Logan but not William because _ was not athletic. A) William B) Logan Print only a single choice from "A" or "B" without explanation. Answer:
- `hellaswag.val.2344` [hellaswag/hellaswag] -> **everyday_activity_completion** / scene continuation: The baby is looking at the camera and then the hand wiped his face. the hand A) talked and raised its hand. B) lays on the table with the baby on it and then the little girl hits the ca [...]  Answer:
- `winogrande.dev.243` [winogrande/winogrande] -> **pronoun_coreference_resolution** / pronoun resolution: The man paid cash for the phone but purchased the tablet with credit because the _ was pricy. A) Phone B) Tablet Print only a single choice from "A" or "B" without explanation. Answer:
- `hellaswag.val.1564` [hellaswag/hellaswag] -> **everyday_activity_completion** / scene continuation: Michele obama and another woman are hula hooping outside on a sunny day. as the camera A) pans around and focuses on taken, she puts the hula hoop down and starts to hula hoop with othe [...]  Answer:
- `winogrande.dev.641` [winogrande/winogrande] -> **pronoun_coreference_resolution** / pronoun resolution: The man thought lifting the rock, not the log, would give him a hernia because the _ was lighter. A) log B) rock Print only a single choice from "A" or "B" without explanation. Answer:
- `hellaswag.val.3675` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete hair styling steps: [header] How to do a laced ponytail [title] Pull your hair up into a high ponytail. [step] Wrap a hair tie around your wrist and pull your hair up into a high ponytail. Hold your hair w [...]  Answer:
- `mmlu-formal-logic.val.36` [mmlu/mmlu-formal-logic] -> **formal_logic_deduction** / truth table construction: Please answer with the letter of the correct answer. Construct a complete truth table for the following argument. Then, using the truth table, determine whether the argument is valid or [...]  Answer:
- `hellaswag.val.1558` [hellaswag/hellaswag] -> **everyday_activity_completion** / scene continuation: A woman in a parking lot is bouncing up and down with some kind of pogo stick attachments on her legs. The woman walks around the parking lot. The woman starts bouncing up and down whil [...]  Answer:
- `hellaswag.val.3237` [hellaswag/hellaswag] -> **everyday_activity_completion** / scene continuation: Two men are sitting on chairs in front of snow mobiles. there A) are a lot of people in cube shapes watching the men. B) is a hole in the ice in front of them. C) man is holding the sid [...]  Answer:
- `hellaswag.val.7695` [hellaswag/hellaswag] -> **everyday_activity_completion** / complete activity steps: [header] How to ride a bus [title] Figure out how to get where you are going. [step] Contact your local bus or transit system and get help from a " route planner " or buy a map book. Ma [...]  Answer:

### chinese_language (n=769)

- `chinese_zodiac.dev.345` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac identification: 2024, ox, 50s
- `chinese_zodiac.dev.283` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac identification: 2023, rat, 10s
- `chinese_zodiac.dev.326` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac year identification: 2024, horse, 70s
- `chinese_zodiac.dev.145` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac identification: 2022, monkey, 50s
- `chinese_tang_poetries.dev.17` [chinese/chinese_tang_poetries] -> **classical_poetry** / poem line identification: 天门中断楚江开，碧水东流至此回。
- `chinese_tang_poetries.dev.16` [chinese/chinese_tang_poetries] -> **classical_poetry** / poem line identification: 巴山楚水凄凉地，二十三年弃置身。
- `chinese_zodiac.dev.195` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac identification: 2022, dog, under 10s
- `chinese_zodiac.dev.10` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac identification: 2021, monkey, 80s
- `chinese_zodiac.dev.139` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac year identification: 2022, tiger, 60s
- `Chinese_character_riddles.dev.50` [chinese/Chinese_character_riddles] -> **character_riddles** / solve character riddle: 见到二人
- `chinese_zodiac.dev.16` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac year identification: 2021, tiger, 80s
- `chinese_zodiac.dev.314` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac year identification: 2024, horse, 80s
- `chinese_homonym.dev.13` [chinese/chinese_homonym] -> **idioms_homonyms_vocabulary** / homonym identification: 老宋忘了晚上有约会，当他赶到的时候女孩已经先走了，他感到很自责。
- `chinese_zodiac.dev.331` [chinese/chinese_zodiac] -> **zodiac_calendar_culture** / zodiac year identification: 2024, pig, 60s
- `chinese_shi_jing.test.4` [chinese/chinese_shi_jing] -> **classical_poetry** / identify poetry title: 下面这段内容出自诗经的哪一篇？请只回复包含完整分类结构的篇目名称，不要包含其他内容。例如：《周南·关雎》 --- 摽有梅，其实七兮。求我庶士，迨其吉兮。

### other (n=2)

- `consensus_summary.dev.218` [consensus_summary/consensus_summary] -> **mixed_multi_domain** / answer unrelated question: claim: Exclusive breastfeeding in the initial weeks after childbirth and continuing to breastfeed (either exclusively or partially) for at least 3 months, preferably 6 months, may reduc [...] ces for?
- `consensus_summary.dev.359` [consensus_summary/consensus_summary] -> **mixed_multi_domain** / answer synthesis: claim: reducing calorie intake and increasing physical activity are the most effective ways to combat obesity. claim: genetic and metabolic factors play a larger role in obesity and tha [...] muscles?
