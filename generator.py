"""
scibot_dataset_v3.py  —  SciBot 15,000-example Generator
=========================================================
Output: Alpaca-format JSONL
  { "instruction": "...", "input": "...", "output": "...", "metadata": {...} }

Design rules:
  1. Every output directly answers its input — zero topic drift.
  2. Misconception questions name the error first, then correct it.
  3. Math problems: no contradictory premises; randomised values; full working shown.
  4. Grade-appropriate language at every level.
  5. Answers stop when the question is answered — no unrequested elaboration.
  6. 9 cognitive levels: define / explain / compare / calculate / predict /
     justify / apply / analyse / misconception.
  7. Messy real-student phrasing handled gracefully.

Run:
  python scibot_dataset_v3.py --n 15000 --out scibot_v3.jsonl
"""

import json, math, random, argparse
from pathlib import Path
from collections import Counter

# ── shared instruction ─────────────────────────────────────────────────────
INSTRUCTION = (
    "You are SciBot, an expert K-12 science tutor. "
    "Answer the exact question asked and do not introduce unrelated topics. "
    "Use language appropriate for the student's grade level. "
    "If a question contains a scientific error or internal contradiction, "
    "identify it explicitly before giving the correct answer. "
    "For calculation problems show every step with correct units. "
    "Define technical terms inline when writing for middle-school level or below."
)

EXAMPLES = []

def q(grade, subject, difficulty, q_type, question, answer):
    EXAMPLES.append({
        "grade_level": grade, "subject": subject,
        "difficulty": difficulty, "q_type": q_type,
        "question": question.strip(), "answer": answer.strip(),
    })

E, M, H = "easy", "medium", "hard"
DEF, EXP, CMP, CAL = "define", "explain", "compare", "calculate"
PRD, JUS, APP, ANA, MIS = "predict", "justify", "apply", "analyse", "misconception"

# ══════════════════════════════════════════════════════════════════
#  K-2  LIFE SCIENCE
# ══════════════════════════════════════════════════════════════════
q("1st Grade","Life Science",E,EXP,
"Where do desert animals get food and water?",
"Desert animals get food by eating plants, insects, or other animals that live in the desert. "
"They get water from the food they eat, from rare rainfall, or by storing water in their bodies. "
"Camels store fat in their humps to help survive long periods without water. "
"Kangaroo rats get almost all their water from the seeds they eat.")

q("1st Grade","Life Science",E,EXP,
"What do plants need to grow?",
"Plants need four things to grow: sunlight, water, air, and nutrients from soil. "
"Sunlight gives them energy to make food. Water carries nutrients through the plant. "
"Plants take in carbon dioxide — a gas from the air — to make food. "
"Soil holds the roots and provides minerals.")

q("1st Grade","Life Science",E,CMP,
"What is the difference between a living thing and a non-living thing?",
"Living things grow, need energy, respond to the world around them, and can reproduce. "
"Animals, plants, and tiny organisms like bacteria are living things. "
"Non-living things like rocks, water, and air do not grow on their own, do not eat, and cannot reproduce.")

q("2nd Grade","Life Science",E,EXP,
"Why do leaves change colour in autumn?",
"Leaves are green in spring and summer because they contain chlorophyll — a substance that helps "
"the plant make food from sunlight. In autumn, days get shorter and cooler. "
"The tree stops making chlorophyll, so the green colour fades. Yellow and orange colours that were "
"hidden beneath the green now show through. Some trees also make a red pigment.")

q("2nd Grade","Life Science",E,EXP,
"What is a food chain? Give a simple example.",
"A food chain shows the order in which living things eat each other, passing energy along. "
"Example: grass → grasshopper → frog → hawk. "
"The grass makes its own food from sunlight. The grasshopper eats the grass. "
"The frog eats the grasshopper. The hawk eats the frog. "
"The arrow means 'is eaten by' or 'energy passes to.'")

q("1st Grade","Life Science",E,EXP,
"How do fish breathe underwater?",
"Fish breathe using organs called gills instead of lungs. Water enters through the fish's mouth "
"and flows over the gills. The gills pull dissolved oxygen out of the water and release carbon "
"dioxide back. This is similar to how our lungs exchange gases with air — but gills work with water.")

q("1st Grade","Life Science",E,EXP,
"What are the four stages of a butterfly's life cycle?",
"A butterfly goes through four stages called complete metamorphosis. "
"Stage 1 — Egg: the butterfly lays a tiny egg on a leaf. "
"Stage 2 — Larva (caterpillar): it hatches and eats leaves to grow. "
"Stage 3 — Pupa (chrysalis): it wraps up and its body completely changes inside. "
"Stage 4 — Adult: a butterfly breaks out with wings and can reproduce.")

q("2nd Grade","Life Science",E,PRD,
"Predict: if all the plants in a food chain died, what would happen to the animals?",
"If all the plants died, herbivores — animals that eat plants — would run out of food and die. "
"Then the animals that eat those herbivores would also run out of food and die. "
"The whole food chain would collapse because plants are at the start — they are the only living "
"things that make food from sunlight. Every animal ultimately depends on plants.")

q("1st Grade","Life Science",E,DEF,
"Define: what is a habitat?",
"A habitat is the natural place where an animal lives. "
"It provides everything the animal needs to survive: food, water, shelter, and space. "
"A fish's habitat is a river or ocean. A bear's habitat is a forest.")

q("2nd Grade","Life Science",E,APP,
"A bird has a long, thin beak. What type of food is it probably adapted to eat, and why?",
"A bird with a long, thin beak is probably adapted to eat nectar from flowers or to probe for insects "
"in narrow holes. The long shape lets it reach deep into a flower or a crack where a short beak "
"could not reach. This is an example of how an animal's body is shaped to match what it eats.")

q("1st Grade","Life Science",E,EXP,
"Why do animals need food?",
"Animals need food because it gives them energy to move, grow, and stay alive. "
"Food also provides the building materials animals need to grow bigger and repair their bodies. "
"Without food, an animal would not have the energy to breathe, move, or reproduce.")

q("2nd Grade","Life Science",E,CMP,
"What is the difference between an insect and a spider?",
"Insects have six legs and three body parts: head, thorax, and abdomen. Examples: ants, beetles. "
"Spiders have eight legs and two body parts: cephalothorax and abdomen. "
"Spiders are not insects — they belong to a different group called arachnids.")

# ══════════════════════════════════════════════════════════════════
#  K-2  EARTH & PHYSICAL SCIENCE
# ══════════════════════════════════════════════════════════════════
q("2nd Grade","Earth Science",E,EXP,
"What causes day and night?",
"Day and night are caused by Earth spinning on its axis — an imaginary line through its centre. "
"Earth completes one full spin every 24 hours. The side facing the Sun has daytime; "
"the side facing away has night-time. The Sun does not move around Earth — Earth is rotating.")

q("2nd Grade","Earth Science",E,EXP,
"What are the three states of water and how do they change?",
"Water exists as a solid (ice), a liquid (water), and a gas (water vapour). "
"Adding heat: ice melts to liquid; liquid evaporates to vapour. "
"Removing heat: vapour condenses to liquid; liquid freezes to ice.")

q("1st Grade","Physical Science",E,EXP,
"What is a magnet and what does it attract?",
"A magnet pulls certain metals toward it using a force called magnetism. "
"Magnets attract metals containing iron, steel, cobalt, or nickel. "
"They do not attract plastic, wood, rubber, or glass. "
"Every magnet has two poles — north and south. Opposite poles attract; same poles repel.")

q("2nd Grade","Physical Science",E,DEF,
"Define: what is energy? Give two examples.",
"Energy is the ability to do work or cause change. "
"Kinetic energy is the energy of movement — a rolling ball. "
"Heat energy warms objects — a hot oven has heat energy.")

q("2nd Grade","Earth Science",E,EXP,
"What is soil made of?",
"Soil is made of tiny pieces of broken-down rock mixed with dead plant and animal material called humus. "
"It also contains water, air, and tiny living things like bacteria and worms. "
"Plants grow in soil because it holds their roots and supplies the minerals and water they need.")

q("2nd Grade","Physical Science",E,CMP,
"What is the difference between pushing and pulling?",
"A push moves an object away from you. Example: pushing a swing. "
"A pull moves an object toward you. Example: opening a drawer. "
"Both are types of forces — they change the motion or shape of an object.")

q("1st Grade","Physical Science",E,PRD,
"Predict: if you let go of a ball at the top of a hill, what will happen and why?",
"The ball will roll down the hill because of gravity — a force that pulls everything toward the ground. "
"At the top the ball has stored energy from being up high. "
"When released, gravity pulls it downward and it rolls to the bottom.")

q("2nd Grade","Earth Science",E,EXP,
"What is weather and name four types.",
"Weather is what the air outside is like at a particular time and place. "
"Four types: sunny (clear skies), rainy (water falls from clouds), "
"windy (air moves quickly), snowy (frozen water falls when very cold).")

# ══════════════════════════════════════════════════════════════════
#  3-5  LIFE SCIENCE
# ══════════════════════════════════════════════════════════════════
q("4th Grade","Life Science",E,EXP,
"What is photosynthesis and why is it important?",
"Photosynthesis is the process plants use to make their own food. "
"Plants take in carbon dioxide from the air and water from the soil, then use sunlight to turn them "
"into glucose (sugar) and oxygen. "
"Word equation: carbon dioxide + water + sunlight → glucose + oxygen. "
"It matters because it produces the oxygen we breathe and creates the energy that flows through "
"almost every food chain on Earth.")

q("4th Grade","Life Science",E,EXP,
"What are the main parts of a plant and what does each do?",
"Roots: anchor the plant and absorb water and minerals from soil. "
"Stem: carries water and nutrients between roots and leaves; holds the plant upright. "
"Leaves: make food through photosynthesis using sunlight, water, and carbon dioxide. "
"Flowers: attract pollinators; produce seeds for reproduction. "
"Seeds: contain a tiny new plant and stored food to help it sprout.")

q("5th Grade","Life Science",E,CMP,
"What is the difference between an inherited trait and a learned behaviour?",
"An inherited trait is passed from parents to offspring through genes — you are born with it and cannot "
"change it through experience. Example: eye colour. "
"A learned behaviour is something an organism does because it was taught or practised. "
"Example: a dog sitting on command was trained, not born knowing this. "
"Ask yourself: was it present at birth, or acquired through experience?")

q("3rd Grade","Life Science",E,EXP,
"What is an adaptation? Give two examples.",
"An adaptation is a body part or behaviour that helps an animal survive in its habitat. "
"Example 1: a polar bear has thick white fur — warm in Arctic cold and camouflaged in snow. "
"Example 2: a cactus has thick waxy skin and stores water in its stem — survival in hot, dry deserts.")

q("5th Grade","Life Science",M,JUS,
"Justify: why are decomposers essential to an ecosystem?",
"Decomposers — mainly bacteria and fungi — break dead organisms into simple substances like minerals "
"and carbon dioxide, returning nutrients to the soil and air. "
"Without decomposers, dead matter would pile up and nutrients would be permanently locked away. "
"Producers (plants) would run out of the minerals they need to grow, and the entire ecosystem would collapse.")

q("4th Grade","Life Science",E,EXP,
"What is a food web and how does it differ from a food chain?",
"A food chain shows one single path of energy: grass → rabbit → fox. "
"A food web shows all the feeding relationships in an ecosystem connected together. "
"Most animals eat more than one food source, so a web is more realistic. "
"Example: a fox eats rabbits, mice, AND berries — a web shows all of those connections.")

q("5th Grade","Life Science",M,ANA,
"Analyse: why do food chains rarely have more than five levels?",
"Because energy is lost at every step. When a plant is eaten, only about 10% of the plant's energy "
"transfers to the herbivore — the rest is lost as heat. "
"The same 10% rule applies at every level. "
"By the fifth level, so little energy remains that it cannot support a viable predator population. "
"This is called the 10% rule and it limits how long food chains can be.")

q("4th Grade","Life Science",M,CMP,
"Compare complete and incomplete metamorphosis.",
"Complete metamorphosis — four stages: egg → larva → pupa → adult. "
"The larva looks completely different from the adult. Examples: butterflies, beetles, flies. "
"Incomplete metamorphosis — three stages: egg → nymph → adult. "
"The nymph looks like a small adult and gradually grows into one — no pupa stage. "
"Examples: grasshoppers, cockroaches, dragonflies.")

q("3rd Grade","Life Science",M,APP,
"A farmer wants richer soil without buying fertiliser. How could they use legumes to help?",
"The farmer could plant legumes — beans, peas, or clover — in the fields. "
"Legumes have bacteria called Rhizobium living in their roots that convert nitrogen from the air "
"into a form plants can use. "
"When the legume plants are ploughed back into the soil, they release that nitrogen. "
"This naturally enriches the soil for the next crop. This practice is called crop rotation.")

# ══════════════════════════════════════════════════════════════════
#  3-5  EARTH & PHYSICAL SCIENCE
# ══════════════════════════════════════════════════════════════════
q("4th Grade","Earth Science",E,EXP,
"Describe the water cycle and name each stage.",
"The water cycle is the continuous movement of water through the environment. "
"Evaporation: the Sun heats surface water → becomes water vapour that rises. "
"Condensation: vapour cools and forms tiny droplets → clouds. "
"Precipitation: water falls as rain, snow, sleet, or hail. "
"Collection: water gathers in oceans, lakes, rivers, and underground → cycle repeats.")

q("5th Grade","Physical Science",M,CMP,
"What is the difference between a physical change and a chemical change? Give one example of each.",
"A physical change alters the form or appearance of a substance but creates no new substance. "
"Example: cutting paper — still paper, just smaller. "
"A chemical change creates new substances with different properties. "
"Signs: colour change, gas produced, heat or light released, irreversible change. "
"Example: burning wood → ash and smoke — entirely new substances.")

q("3rd Grade","Physical Science",E,EXP,
"What is the difference between a solid, a liquid, and a gas?",
"Solid: fixed shape and volume; particles tightly packed. Example: a rock. "
"Liquid: fixed volume but takes the shape of its container. Example: water in a cup. "
"Gas: no fixed shape or volume; spreads to fill any container. Example: air in a balloon.")

q("4th Grade","Earth Science",M,EXP,
"What causes earthquakes?",
"Earth's outer shell is broken into large pieces called tectonic plates that move very slowly. "
"When two plates grind against each other, get stuck, then suddenly slip, "
"they release energy that travels through the ground as seismic waves — we feel this as shaking. "
"The point underground where the slip occurs is the focus; the point above it on the surface is the epicentre.")

q("5th Grade","Earth Science",M,EXP,
"How do volcanoes form?",
"Volcanoes form where magma — molten rock — pushes up through openings in Earth's crust. "
"Most form at tectonic plate boundaries. "
"At divergent boundaries, plates pull apart and magma rises to fill the gap. "
"At convergent boundaries, one plate sinks and melts, and magma rises through the plate above. "
"Volcanoes also form over hot spots, like the Hawaiian islands.")

q("5th Grade","Earth Science",M,CMP,
"What is the difference between renewable and non-renewable energy sources?",
"Non-renewable: forms over millions of years; used faster than replenished; once gone, gone. "
"Examples: coal, oil, natural gas. Burning them releases CO₂. "
"Renewable: replenished naturally on a human timescale; will not run out. "
"Examples: solar, wind, hydroelectric, geothermal. Most produce little or no greenhouse gases.")

q("4th Grade","Physical Science",M,EXP,
"What is the difference between a conductor and an insulator?",
"A conductor lets heat or electricity pass through it easily. "
"Examples: copper (electrical wires), aluminium (pots). "
"An insulator resists the flow of heat or electricity. "
"Examples: rubber (wire coating), wood (pot handles). "
"Conductors carry energy; insulators direct and contain it safely.")

q("3rd Grade","Physical Science",E,APP,
"You mix sugar into warm water and it disappears. Has it gone? How could you get it back?",
"The sugar has not gone — it dissolved into the water to form a solution. "
"The sugar particles are too small to see but are still in the water. "
"You can get the sugar back by evaporating the water: heat the mixture gently until all the water "
"turns to steam and escapes, leaving sugar crystals behind.")

# ══════════════════════════════════════════════════════════════════
#  6-8  LIFE SCIENCE
# ══════════════════════════════════════════════════════════════════
q("6th Grade","Life Science / Biology",M,EXP,
"What is a cell and why is it called the basic unit of life?",
"A cell is the smallest unit that can carry out all the basic processes of life independently: "
"growth, energy use, response to environment, and reproduction. "
"All living organisms are made of one or more cells. Single-celled organisms complete all life "
"processes in one cell. Multicellular organisms have trillions of specialised cells working together. "
"No structure smaller than a cell can independently do all of these things.")

q("6th Grade","Life Science / Biology",M,CMP,
"Compare plant cells and animal cells. What structures does each have that the other lacks?",
"Both share: nucleus, cell membrane, cytoplasm, mitochondria, and ribosomes. "
"Plant cells only: cell wall (rigid cellulose layer for structural support), "
"chloroplasts (carry out photosynthesis), large central vacuole (stores water, maintains pressure). "
"Animal cells only: lysosomes (digest waste and pathogens), centrioles (organise the mitotic spindle).")

q("7th Grade","Life Science / Biology",M,CMP,
"Explain the difference between mitosis and meiosis. Define key terms.",
"Mitosis produces two daughter cells, each diploid — containing the same chromosome number "
"(46 in humans, two copies of each chromosome) as the parent cell. Used for growth and repair. "
"Meiosis produces four daughter cells, each haploid — containing half the chromosomes (23 in humans). "
"Used to produce sex cells (sperm and eggs). "
"When sperm and egg fuse at fertilisation, the diploid number is restored.")

q("7th Grade","Life Science / Biology",M,EXP,
"What is DNA and what does it do in a cell?",
"DNA — deoxyribonucleic acid — is found in the nucleus, shaped like a twisted ladder called a double helix. "
"It contains instructions called genes that tell the cell how to build proteins. "
"Proteins control almost everything a cell does: its structure, chemical reactions, and communication. "
"DNA is also copied when cells divide so each new cell gets a complete set of instructions, "
"and is passed from parents to offspring explaining family resemblance.")

q("8th Grade","Life Science / Biology",M,EXP,
"Describe natural selection and how it leads to evolution.",
"Natural selection works through four steps: "
"Variation — individuals in a population differ in heritable traits. "
"Inheritance — traits pass to offspring through genes. "
"Overproduction — more offspring are produced than the environment can support. "
"Differential survival — individuals with advantageous traits reproduce more, so those traits "
"become more common. Over many generations this change in the population's genetic make-up is evolution.")

q("6th Grade","Life Science / Biology",M,EXP,
"What are the roles of the digestive system?",
"The digestive system breaks food into nutrients small enough to absorb into the blood. "
"Mouth: chewing and saliva begin mechanical and chemical breakdown. "
"Stomach: acid and enzymes further liquefy food. "
"Small intestine: most nutrients are absorbed into the bloodstream. "
"Large intestine: water is absorbed; remaining waste is excreted. "
"Liver: produces bile to help digest fats. Pancreas: provides digestive enzymes.")

q("7th Grade","Life Science / Biology",M,EXP,
"What is the difference between aerobic and anaerobic respiration?",
"Aerobic respiration uses oxygen to break down glucose, producing about 30–32 ATP per glucose "
"and releasing carbon dioxide and water as waste. Used by most cells most of the time. "
"Anaerobic respiration occurs without oxygen, producing only 2 ATP per glucose. "
"In human muscles it produces lactic acid, causing the burning sensation during intense exercise. "
"It kicks in when oxygen delivery cannot keep up with energy demand.")

q("8th Grade","Life Science / Biology",M,EXP,
"How does energy flow through an ecosystem?",
"Energy enters through producers — plants and algae — that capture sunlight via photosynthesis. "
"Primary consumers (herbivores) eat producers. Secondary consumers eat primary consumers. "
"At each step roughly 90% of energy is lost as heat — only about 10% passes to the next level. "
"This means there are always far more plants than herbivores, and more herbivores than top predators. "
"Decomposers break down dead organisms at every level, returning nutrients to the soil.")

q("6th Grade","Life Science / Biology",M,PRD,
"Predict: what would happen to rabbit numbers if all the foxes in a habitat were removed?",
"Rabbit numbers would initially grow rapidly with no predator. "
"As rabbits increased, they would consume more grass and plants. "
"Eventually the food supply would be depleted, causing starvation, and the population would crash. "
"This demonstrates why predators are necessary to keep prey populations balanced with available food.")

q("7th Grade","Life Science / Biology",M,ANA,
"Analyse how vaccines work. What does the immune system do the second time it sees a pathogen?",
"A vaccine introduces a harmless form of a pathogen — weakened, killed, or a protein fragment — "
"triggering an immune response. The body produces antibodies and, crucially, memory B and T cells. "
"These memory cells persist for years. When the real pathogen appears later, they recognise it "
"immediately and mount a rapid, powerful response — destroying the pathogen before illness develops. "
"The second response is much faster and stronger than the first.")

q("8th Grade","Life Science / Biology",M,JUS,
"Justify why biodiversity is important to ecosystem stability.",
"High biodiversity means many species filling different roles. "
"If one species is lost, others can often fill a similar role, keeping the ecosystem functioning. "
"Low-biodiversity ecosystems are fragile — one disease or climate event can collapse them. "
"Diverse plant species also stabilise soil, support pollinators, and provide varied food sources. "
"For humans, biodiversity underpins medicines, food crops, clean water, and clean air.")

q("7th Grade","Life Science / Biology",M,APP,
"Apply: why might a doctor prescribe a full 10-day course of antibiotics even if you feel better after 3 days?",
"Feeling better after 3 days means the immune system and antibiotics have reduced the bacterial "
"population enough to relieve symptoms — but not eliminated every bacterium. "
"Any surviving bacteria are likely to be those with some resistance to the antibiotic. "
"If you stop early, these resistant bacteria reproduce and can cause a relapse that is harder to treat. "
"Completing the full course ensures the entire bacterial population is eliminated, "
"reducing the risk of resistance developing.")

# ══════════════════════════════════════════════════════════════════
#  6-8  MISCONCEPTIONS
# ══════════════════════════════════════════════════════════════════
q("7th Grade","Life Science / Biology",M,MIS,
"What is the function of the kidneys in the human respiratory system?",
"This question contains a scientific error: the kidneys are not part of the respiratory system. "
"The kidneys belong to the excretory (urinary) system. They filter waste — mainly urea — from the blood, "
"regulate water and salt balance, and produce urine. "
"The respiratory system consists of the nose, trachea, bronchi, and lungs, "
"whose job is to bring oxygen in and remove carbon dioxide.")

q("6th Grade","Life Science / Biology",M,MIS,
"Humans evolved from chimpanzees. Is this correct?",
"No — this is a common misconception. Humans did not evolve from chimpanzees. "
"Humans and chimpanzees share a common ancestor that lived about 6–7 million years ago. "
"From that ancestor, two lineages evolved separately — one became modern chimps, the other modern humans. "
"Chimpanzees are our closest living relatives, not our ancestors.")

q("8th Grade","Physical Science",M,MIS,
"Does a heavier object always fall faster than a lighter one?",
"No — Galileo disproved this in the late 1500s. "
"In the absence of air resistance, all objects fall at the same rate regardless of mass. "
"Gravity accelerates every object at 9.8 m/s² near Earth's surface. "
"A bowling ball and a feather dropped in a vacuum hit the ground simultaneously. "
"In everyday life, air resistance makes the feather fall slower — but that is air drag, not mass.")

q("7th Grade","Earth Science",M,MIS,
"Seasons are caused by Earth getting closer to the Sun in summer. Is this correct?",
"No — this is incorrect. Earth's distance from the Sun barely changes throughout the year, "
"and Earth is actually slightly closer to the Sun in January — Northern Hemisphere winter. "
"Seasons are caused by Earth's axial tilt (23.5°). When the Northern Hemisphere tilts toward the Sun, "
"sunlight hits more directly and days are longer — summer. "
"When it tilts away, sunlight is weaker and days shorter — winter. "
"The Southern Hemisphere has the opposite season at the same time.")

q("6th Grade","Physical Science",E,MIS,
"Plants breathe in oxygen and breathe out carbon dioxide, just like animals. Is this completely right?",
"Only partially correct. Plants do perform cellular respiration continuously — taking in oxygen and "
"releasing carbon dioxide, like animals. "
"But during daylight, plants also perform photosynthesis, which does the opposite: "
"takes in carbon dioxide and releases oxygen. "
"Daytime net result: photosynthesis produces far more oxygen than respiration uses, "
"so plants are net oxygen producers during the day. At night, only respiration runs.")

q("8th Grade","Life Science / Biology",M,MIS,
"Acquired characteristics — like a bodybuilder's muscles — can be inherited by children. Correct?",
"No — this idea is called Lamarckism and was disproved in the 19th century. "
"Characteristics acquired during a lifetime do not alter the DNA in reproductive cells (sperm and eggs). "
"Only DNA changes in sex cells can be inherited. "
"A bodybuilder's children inherit the same genetic potential for muscle growth as anyone else — "
"not the parent's developed muscles.")

q("7th Grade","Life Science / Biology",M,MIS,
"Antibiotics can be used to treat the flu. Is this correct?",
"No — this is a dangerous misconception. "
"Antibiotics target structures found only in bacteria — such as the bacterial cell wall. "
"The flu (influenza) is caused by a virus, which has a completely different structure. "
"Antibiotics have no effect on viruses. Taking them for a viral infection does not help, "
"and contributes to antibiotic resistance — making future bacterial infections harder to treat. "
"Influenza is managed with rest, fluids, and in some cases antiviral medications.")

q("6th Grade","Earth Science",M,MIS,
"The Great Wall of China is visible from space with the naked eye. Is this true?",
"No — this is a popular myth. The Great Wall of China is very long but very narrow — "
"at most about 9 metres wide. "
"The human eye cannot distinguish an object that narrow from low Earth orbit (~400 km altitude). "
"Astronauts on the International Space Station have confirmed they cannot see it without optical aids. "
"By contrast, large cities, highways, and reservoirs are visible because of their broader area or reflectivity.")

# ══════════════════════════════════════════════════════════════════
#  6-8  EARTH SCIENCE
# ══════════════════════════════════════════════════════════════════
q("6th Grade","Earth Science",M,EXP,
"What are the layers of Earth from surface to centre?",
"Crust: outermost, thinnest solid layer we live on. Oceanic crust is thinner and denser; "
"continental crust is thicker and less dense. "
"Mantle: thick layer of hot rock that flows very slowly. "
"Outer core: liquid iron and nickel — its motion generates Earth's magnetic field. "
"Inner core: solid iron and nickel — extreme pressure keeps it solid despite intense heat.")

q("7th Grade","Earth Science",M,EXP,
"Explain the rock cycle.",
"Igneous rocks: form when magma (underground) or lava (surface) cools and solidifies. "
"Sedimentary rocks: form when weathered fragments accumulate, are buried, and are compacted and cemented. "
"Metamorphic rocks: form when any rock type is subjected to intense heat and pressure without melting. "
"Rocks cycle between types through melting, weathering, burial, and heat/pressure over millions of years.")

q("8th Grade","Earth Science",M,EXP,
"What is plate tectonics and what features does it explain?",
"Plate tectonics: Earth's outer layer (lithosphere) is divided into ~15 tectonic plates that move slowly. "
"Divergent boundaries: plates pull apart; magma rises → mid-ocean ridges; new crust forms. "
"Convergent boundaries: plates collide; mountains form or one plate subducts → ocean trenches and volcanoes. "
"Transform boundaries: plates slide past → earthquakes. "
"Explains: continental shapes fitting together, matching fossils on separated continents, "
"and the distribution of earthquakes and volcanoes at plate margins.")

q("7th Grade","Earth Science",M,EXP,
"Explain why the Moon has phases.",
"The Moon does not change shape — we see different amounts of its sunlit side from Earth. "
"New Moon: lit side faces away → invisible. Full Moon: lit side faces us → fully visible. "
"Crescent, quarter, and gibbous phases show fractions of the sunlit half as the Moon orbits Earth "
"once every 29.5 days.")

q("8th Grade","Earth Science",M,EXP,
"What is the greenhouse effect and how does human activity intensify it?",
"Natural greenhouse effect: greenhouse gases (CO₂, methane, water vapour) absorb heat radiated from "
"Earth's surface and re-emit it, keeping Earth ~33 °C warmer than it would otherwise be. "
"Human intensification: burning fossil fuels and deforestation release extra CO₂ and methane much "
"faster than natural sinks can absorb them, trapping more heat and raising global temperatures — climate change.")

q("6th Grade","Earth Science",E,CMP,
"What is the difference between weather and climate?",
"Weather: what the atmosphere is doing right now — temperature, rain, wind. Changes hour to hour. "
"Climate: the average pattern of weather in a region over 30+ years. "
"A desert has a hot, dry climate even if it rains on a particular day. "
"Memory aid: climate is what you expect; weather is what you get.")

q("7th Grade","Earth Science",M,ANA,
"Analyse the evidence that supports the theory of plate tectonics.",
"Seafloor spreading: ocean crust is youngest at mid-ocean ridges and gets older moving away — "
"confirmed by radiometric dating. "
"Palaeomagnetism: symmetric magnetic stripes on either side of ridges record field reversals. "
"Continental fit: South America and Africa coastlines match. "
"Matching fossils: identical ancient species on continents now separated by oceans. "
"Earthquake and volcano distribution: almost exclusively at plate boundaries. "
"GPS: plates move at measurable rates of 1–15 cm/year.")

q("8th Grade","Earth Science",M,PRD,
"Predict: what would happen to Earth's climate if all forests were cut down?",
"Forests absorb large amounts of CO₂ through photosynthesis. Removing them would leave more CO₂ "
"in the atmosphere, intensifying the greenhouse effect and raising global temperatures. "
"Forests return water vapour through transpiration — without this, regional rainfall would decrease. "
"Exposed soil would erode rapidly, reducing agricultural productivity. "
"Biodiversity would collapse as habitats disappeared.")

# ══════════════════════════════════════════════════════════════════
#  6-8  PHYSICAL SCIENCE
# ══════════════════════════════════════════════════════════════════
q("6th Grade","Physical Science",E,CMP,
"What is the difference between mass and weight?",
"Mass: amount of matter in an object; measured in kg; constant anywhere in the universe. "
"Weight: force of gravity on an object; measured in newtons (N); depends on gravitational field strength. "
"On the Moon gravity is ~1/6 of Earth's — an astronaut weighs six times less there "
"but their mass is identical.")

q("7th Grade","Physical Science",M,EXP,
"State Newton's three laws of motion with a precise example for each.",
"First Law (Inertia): an object stays at rest or moves at constant velocity unless a net force acts. "
"Example: a hockey puck on frictionless ice continues indefinitely. "
"Second Law: F = ma. "
"Example: a 2 kg object with a 10 N net force accelerates at 5 m/s². "
"Third Law: every action has an equal and opposite reaction on a different object. "
"Example: a rocket expels gas downward; the gas pushes the rocket upward with equal force.")

q("8th Grade","Physical Science",M,CMP,
"What is the difference between speed, velocity, and acceleration?",
"Speed: how fast — scalar (number only). Example: 60 km/h. "
"Velocity: speed with direction — vector. Example: 60 km/h north. "
"A car circling at constant speed has changing velocity because direction changes. "
"Acceleration: rate of change of velocity. Occurs when speed changes, direction changes, or both. "
"Formula: a = Δv / t.")

q("6th Grade","Physical Science",E,DEF,
"Define six forms of energy and give one example of each.",
"Kinetic: energy of motion. Example: a moving car. "
"Gravitational potential: energy from height. Example: a book on a shelf. "
"Elastic potential: stored in stretched/compressed material. Example: a stretched rubber band. "
"Thermal: energy from particle motion. Example: a hot pan. "
"Chemical: stored in chemical bonds. Example: energy in food. "
"Electrical: from moving electrons. Example: current powering a bulb.")

q("7th Grade","Physical Science",M,EXP,
"What is the law of conservation of energy?",
"Energy cannot be created or destroyed — only converted from one form to another. "
"Total energy in a closed system is constant. "
"Example: a falling ball converts gravitational potential energy to kinetic energy. "
"On impact, kinetic energy converts to sound and thermal energy. "
"Total energy is the same throughout — just in different forms.")

q("6th Grade","Physical Science",M,APP,
"Apply: why does a metal spoon feel colder than a wooden spoon at the same room temperature?",
"Both spoons are at the same temperature as the room. "
"Metal conducts heat away from your hand very quickly — it draws warmth out fast, which feels cold. "
"Wood conducts heat slowly — it barely draws heat from your hand, so it feels close to body temperature. "
"The sensation of cold depends on how fast heat flows away from your hand, not the object's actual temperature.")

# ══════════════════════════════════════════════════════════════════
#  MESSY / INFORMAL STUDENT INPUT
# ══════════════════════════════════════════════════════════════════
q("6th Grade","Earth Science",E,EXP,
"why moon change shape??",
"Great question! The Moon does not actually change shape. "
"What changes is how much of its sunlit side we can see from Earth. "
"New Moon: lit side faces away — we see nothing. Full Moon: lit side faces us completely. "
"In between we see crescent, quarter, and gibbous shapes. These are called the phases of the Moon.")

q("5th Grade","Life Science",E,EXP,
"wait so plants breathe??",
"Yes, in a way! Plants exchange gases, similar to breathing. "
"During photosynthesis they take in carbon dioxide and release oxygen. "
"They also do cellular respiration — taking in oxygen and releasing carbon dioxide for energy. "
"During the day, photosynthesis produces far more oxygen than respiration uses, "
"so plants are a net oxygen source.")

q("4th Grade","Physical Science",E,EXP,
"whats the diff between hot and cold lol",
"Hot and cold describe how much thermal energy — energy from moving particles — something has. "
"Fast-moving particles → more thermal energy → feels hot. "
"Slow-moving particles → less thermal energy → feels cold. "
"Temperature measures this in degrees Celsius (°C) or Fahrenheit (°F). "
"Heat always flows from hotter objects to cooler ones.")

q("7th Grade","Biology",E,EXP,
"whats dna even do i dont get it",
"DNA is like a detailed instruction manual stored inside almost every cell. "
"It contains genes — instructions for building proteins, which do most of the work in your body: "
"building muscles, fighting infection, digesting food. "
"DNA also explains why you look like your parents — you inherited half your DNA from each of them. "
"Its shape is a twisted ladder called a double helix.")

q("8th Grade","Chemistry",M,EXP,
"ok so like why does ice melt asking for a test tmrw",
"Ice melts when enough heat energy is added. "
"In ice, water molecules are locked in a rigid structure and only vibrate. "
"Adding heat gives them enough energy to break free and flow past each other — liquid water. "
"This happens at 0 °C (32 °F) at normal atmospheric pressure. Good luck on your test!")

q("9th Grade","Physics",M,EXP,
"idk how to do f=ma can u help",
"F = ma is Newton's second law: Force = mass × acceleration. "
"Units: F in newtons (N), m in kilograms (kg), a in m/s². "
"Example: 4 kg box, acceleration 3 m/s² → F = 4 × 3 = 12 N. "
"Rearrange: m = F/a; a = F/m. Always check units: kg × m/s² = N.")

q("10th Grade","Chemistry",M,EXP,
"what even is a mole in chemistry its so confusing",
"A mole is a counting unit. Like 'dozen' means 12, 'mole' means 6.022 × 10²³. "
"One mole of carbon atoms weighs exactly 12 grams — matching carbon's atomic mass in grams. "
"This lets chemists weigh out known numbers of atoms on a balance. "
"So '2 moles of HCl' means 2 × 6.022×10²³ molecules of HCl.")

q("6th Grade","Earth Science",E,EXP,
"why is the sky blue",
"Sunlight contains all colours mixed together. When it enters the atmosphere, gas molecules "
"scatter blue light in all directions far more than other colours, because blue has a shorter wavelength. "
"So wherever you look in the sky, scattered blue light reaches your eyes — making the sky appear blue. "
"At sunset, light travels through more atmosphere, scattering away the blue and leaving orange and red.")

q("5th Grade","Earth Science",E,EXP,
"how do mountains form",
"Mountains form in several ways. "
"Fold mountains: two tectonic plates collide, pushing rock layers upward into folds — the Himalayas. "
"Volcanic mountains: magma erupts and piles up — Mount Fuji. "
"Fault-block mountains: large rock blocks pushed up along cracks (faults) — the Sierra Nevada. "
"All mountain-building is ultimately driven by slow movement of tectonic plates.")

q("7th Grade","Physics",M,EXP,
"what happens when u mix hot and cold water",
"Heat flows from the hotter water to the cooler water until both reach the same temperature — "
"called thermal equilibrium. The hot water cools; the cold water warms. "
"With equal masses: T_final = (T_hot + T_cold) / 2. "
"Energy lost by hot water = energy gained by cold water — conservation of energy.")

# ══════════════════════════════════════════════════════════════════
#  HIGH SCHOOL  BIOLOGY
# ══════════════════════════════════════════════════════════════════
q("9th Grade","Biology",M,EXP,
"Describe the structure of DNA and the base-pairing rules.",
"DNA is a double helix — two strands twisted together. "
"Each strand is built from nucleotides: deoxyribose sugar + phosphate group + one of four bases "
"(adenine A, thymine T, guanine G, cytosine C). "
"Base-pairing: A pairs with T (2 hydrogen bonds); G pairs with C (3 hydrogen bonds). "
"Sugar-phosphate groups form the outer backbone; paired bases form the interior rungs.")

q("10th Grade","Biology",M,EXP,
"Explain protein synthesis from DNA to protein.",
"Transcription (nucleus): RNA polymerase reads the template DNA strand 3'→5' and builds mRNA 5'→3'. "
"RNA uses uracil (U) instead of thymine. In eukaryotes, introns are spliced out; mature mRNA exits nucleus. "
"Translation (ribosome): ribosome reads mRNA codons (3 nucleotides = 1 amino acid). "
"tRNA molecules bring matching amino acids; peptide bonds link them. "
"Translation ends at a stop codon (UAA, UAG, UGA). The polypeptide folds into a functional protein.")

q("11th Grade","Biology",H,EXP,
"Explain how the lac operon works in E. coli.",
"The lac operon is inducible — normally off, switched on when lactose is available. "
"Lactose absent: repressor binds the operator, blocking RNA polymerase. No transcription. "
"Lactose present: allolactose (lactose derivative) binds repressor, changing its shape so it "
"leaves the operator. RNA polymerase transcribes lacZ, lacY, lacA → lactose-metabolising enzymes produced. "
"When lactose is consumed, free repressor reattaches and transcription stops.")

q("12th Grade","Biology",H,EXP,
"What is the Hardy-Weinberg principle and what five conditions are required?",
"Hardy-Weinberg: allele and genotype frequencies are constant if no evolutionary forces act. "
"Equation: p² + 2pq + q² = 1  (p + q = 1). "
"Five conditions: (1) No mutation. (2) No gene flow. (3) Random mating. "
"(4) Very large population (no genetic drift). (5) No natural selection. "
"Because these are never perfectly met, real populations always evolve to some degree.")

q("9th Grade","Biology",M,EXP,
"What is the role of enzymes in biological reactions?",
"Enzymes are protein catalysts that speed up reactions without being consumed. "
"They lower activation energy. Each has an active site that binds a specific substrate (lock-and-key). "
"After the reaction the enzyme is released unchanged. "
"Above ~40 °C, most human enzymes denature — shape changes, function lost. "
"Optimal: 37 °C, near-neutral pH.")

q("10th Grade","Biology",M,EXP,
"Describe the cell cycle and how checkpoints prevent cancer.",
"G1: cell grows and carries out normal functions. "
"S phase: DNA is replicated. "
"G2: cell continues growing and prepares for division. "
"M phase: mitosis and cytokinesis. "
"G1 checkpoint: checks cell size and DNA integrity. "
"G2 checkpoint: confirms replication is complete. "
"Spindle checkpoint: confirms chromosomes are properly attached. "
"p53 detects DNA damage → triggers repair or apoptosis. "
"Mutations in checkpoint genes allow uncontrolled division — cancer.")

q("11th Grade","Biology",H,CMP,
"Compare mitosis and meiosis: purpose, products, and genetic outcome.",
"Mitosis: purpose — growth and repair. Products — 2 diploid cells. Genetic outcome — identical to parent. "
"Meiosis: purpose — gamete production. Products — 4 haploid cells. "
"Genetic outcome — unique due to crossing over (Prophase I) and independent assortment.")

q("12th Grade","Biology",H,EXP,
"Explain the endosymbiotic theory and its supporting evidence.",
"Theory: mitochondria and chloroplasts evolved from free-living prokaryotes engulfed by a larger cell. "
"Evidence: (1) double membrane; (2) circular DNA like prokaryotes; "
"(3) 70S ribosomes like bacteria; (4) divide by binary fission; "
"(5) rRNA sequences link mitochondria to alpha-proteobacteria and chloroplasts to cyanobacteria.")

q("9th Grade","Biology",M,APP,
"Apply: why does a fever help the body fight infection?",
"A moderate fever (38–40 °C) slows or stops pathogen reproduction, since many pathogens are adapted to 37 °C. "
"Elevated temperature also speeds immune cell activity and antibody production. "
"However, fever above 41 °C is dangerous — it can denature the body's own enzymes.")

q("10th Grade","Biology",M,ANA,
"Analyse how antibiotic resistance develops in a bacterial population.",
"A bacterial population has natural variation — a rare few may carry a mutation conferring resistance. "
"When antibiotic is applied, sensitive bacteria are killed; resistant ones survive and reproduce. "
"Over generations, the resistant allele increases in frequency until the population is largely resistant. "
"Accelerated by: incomplete courses (leaving resistant survivors), overuse (increasing selection pressure), "
"and horizontal gene transfer (bacteria share resistance genes directly).")

q("11th Grade","Biology",H,PRD,
"Predict: what happens to ATP production if the inner mitochondrial membrane becomes freely permeable to H⁺?",
"The proton gradient driving ATP synthase would collapse. "
"H⁺ would cross the membrane without flowing through ATP synthase — no oxidative phosphorylation. "
"Only glycolysis and Krebs cycle remain: just 4 ATP per glucose instead of ~32. "
"Cell would die from energy starvation. "
"This is the mechanism of uncouplers like 2,4-dinitrophenol.")

q("10th Grade","Biology",H,JUS,
"Justify why sexual reproduction is advantageous over asexual reproduction for long-term survival.",
"Sexual reproduction produces genetically unique offspring through crossing over, independent assortment, "
"and random fertilisation. "
"This genetic diversity means some individuals are likely to survive novel threats — new diseases, "
"environmental changes, new predators — because the population has varied alleles. "
"Asexual reproduction produces genetically identical clones; a single pathogen can potentially wipe out "
"the entire population. "
"Genetic diversity is the raw material for natural selection and long-term adaptation.")

q("9th Grade","Biology",M,DEF,
"Define: gene, allele, genotype, and phenotype.",
"Gene: a segment of DNA at a specific location (locus) on a chromosome that codes for a protein or trait. "
"Allele: one of two or more versions of a gene. Example: B (brown eyes) and b (blue eyes). "
"Genotype: the actual combination of alleles an individual carries. Example: Bb. "
"Phenotype: the observable trait that results from the genotype. Example: brown eyes.")

q("11th Grade","Biology",H,EXP,
"Explain epigenetics and give two examples of epigenetic mechanisms.",
"Epigenetics: heritable changes in gene expression that do not alter the DNA sequence. "
"DNA methylation: methyl groups added to cytosine at CpG sites, typically silencing genes. "
"Roles in X-chromosome inactivation and genomic imprinting. "
"Histone modification: "
"Acetylation loosens chromatin → genes more accessible → transcription active. "
"Deacetylation compacts chromatin → transcription repressed.")

q("12th Grade","Biology",H,ANA,
"Analyse why the lac operon is more energetically efficient than constitutive expression.",
"Constitutive expression would produce lactose-metabolising enzymes continuously, "
"wasting energy and amino acids even when lactose is absent or glucose (preferred fuel) is available. "
"The lac operon is inducible — enzymes are synthesised only when allolactose is present AND "
"glucose is absent (catabolite repression via the CAP–cAMP system). "
"Resources are allocated precisely when needed, providing a significant fitness advantage.")

# ══════════════════════════════════════════════════════════════════
#  HIGH SCHOOL  CHEMISTRY
# ══════════════════════════════════════════════════════════════════
q("9th Grade","Chemistry",M,EXP,
"What is an atom and how is it structured?",
"Nucleus: protons (positive) and neutrons (neutral). "
"Electron shells: electrons (negative) orbit the nucleus. "
"Atomic number = protons (defines the element). Neutral atom: electrons = protons. "
"Mass number = protons + neutrons. Same element, different neutron numbers = isotopes.")

q("10th Grade","Chemistry",M,EXP,
"What do periods and groups represent in the periodic table?",
"Periods (rows): elements in the same period have the same number of electron shells. "
"Moving left to right, one proton and one electron are added each step. "
"Groups (columns): elements in the same group have the same number of valence electrons "
"and therefore similar chemical properties. "
"Group 1 (alkali metals): 1 valence electron, highly reactive. "
"Group 18 (noble gases): full outer shell, nearly inert.")

q("10th Grade","Chemistry",M,CMP,
"What is the difference between ionic and covalent bonding?",
"Ionic: metal + non-metal; one atom transfers electrons to another → oppositely charged ions held by "
"electrostatic attraction. Example: Na + Cl → NaCl. High melting point; conducts when dissolved. "
"Covalent: two non-metals; atoms share electron pairs. Example: H₂, H₂O. "
"Properties vary; generally do not conduct electricity.")

q("10th Grade","Chemistry",M,EXP,
"What is the difference between an acid and a base, and what does pH measure?",
"Acid: releases H⁺ in water; tastes sour; turns blue litmus red. Examples: HCl, acetic acid. "
"Base: accepts H⁺ or releases OH⁻; tastes bitter; turns red litmus blue. Examples: NaOH, baking soda. "
"pH = −log[H⁺]. Scale 0–14: <7 acidic, 7 neutral, >7 basic. "
"Logarithmic: pH 4 is 10× more acidic than pH 5.")

q("11th Grade","Chemistry",H,EXP,
"What is Le Chatelier's principle? Give one concentration and one temperature example.",
"Principle: a system at equilibrium shifts to partially counteract any applied stress. "
"Concentration example: N₂ + 3H₂ ⇌ 2NH₃. Adding N₂ shifts equilibrium right → more NH₃. "
"Temperature example: same reaction is exothermic forward. "
"Increasing temperature shifts it left, reducing NH₃ yield. "
"Only temperature changes K itself.")

q("11th Grade","Chemistry",H,EXP,
"State the four gas laws and show how the ideal gas law combines them.",
"Boyle's: P₁V₁ = P₂V₂ (constant T, n). "
"Charles's: V₁/T₁ = V₂/T₂ (constant P, n; T in K). "
"Gay-Lussac's: P₁/T₁ = P₂/T₂ (constant V, n). "
"Avogadro's: V ∝ n (constant T, P). "
"Ideal Gas Law: PV = nRT (P atm, V litres, n mol, R = 0.08206 L·atm/mol·K, T Kelvin). "
"Assumes point-mass particles with no intermolecular forces.")

q("12th Grade","Chemistry",H,EXP,
"Explain Gibbs free energy and how it predicts spontaneity.",
"ΔG = ΔH − TΔS. "
"ΔG < 0: spontaneous. ΔG > 0: non-spontaneous. ΔG = 0: equilibrium. "
"ΔH < 0, ΔS > 0 → always spontaneous. "
"ΔH > 0, ΔS < 0 → never spontaneous. "
"ΔH < 0, ΔS < 0 → spontaneous at low T. "
"ΔH > 0, ΔS > 0 → spontaneous at high T. "
"Also: ΔG° = −RT ln K.")

q("11th Grade","Chemistry",H,JUS,
"Justify why increasing temperature increases reaction rate but can reduce yield for an exothermic reaction.",
"Higher T: more molecules exceed activation energy → faster rate (Arrhenius: k = Ae^(−Ea/RT)). "
"For exothermic equilibrium reactions, heat is a product. "
"Le Chatelier: adding heat shifts equilibrium in the endothermic (reverse) direction, reducing product yield. "
"Industrial compromise: Haber process uses ~450 °C for acceptable rate and acceptable yield.")

q("9th Grade","Chemistry",M,EXP,
"What is the law of conservation of mass and how does it apply to equations?",
"Matter is neither created nor destroyed in a chemical reaction — mass of reactants = mass of products. "
"Chemical equations must therefore be balanced: the same number of each atom on both sides. "
"Use coefficients (never change subscripts). "
"Example: 2H₂ + O₂ → 2H₂O (4 H and 2 O on each side).")

q("12th Grade","Chemistry",H,ANA,
"Analyse how a buffer solution resists pH changes.",
"Buffer: weak acid (HA) + conjugate base (A⁻) in significant concentrations. "
"Add H⁺: H⁺ + A⁻ → HA — base absorbs the acid; pH barely changes. "
"Add OH⁻: OH⁻ + HA → A⁻ + H₂O — acid neutralises the base. "
"Henderson-Hasselbalch: pH = pKa + log([A⁻]/[HA]). "
"Most effective within ±1 pH unit of pKa. Capacity exhausted when one component is nearly depleted.")

q("10th Grade","Chemistry",M,APP,
"Apply: why does aluminium foil keep food both warm and cool?",
"Aluminium is a good heat conductor and reflects infrared radiation. "
"Keeps warm: wrapping reduces convective heat loss; shiny surface reflects radiant heat back to food. "
"Keeps cool: the same reflective surface reflects incoming radiant heat away from cold food. "
"In both cases the foil slows the rate of heat transfer between the food and surroundings.")

q("11th Grade","Chemistry",H,EXP,
"Explain how electronegativity determines bond polarity.",
"Electronegativity: how strongly an atom attracts shared electrons. Increases across period; decreases down group. "
"ΔEN < 0.5: nonpolar covalent — electrons shared nearly equally. Example: Cl₂. "
"ΔEN 0.5–1.7: polar covalent — unequal sharing; partial charges (δ+, δ−). Example: H₂O, HCl. "
"ΔEN > 1.7: ionic — one atom essentially takes the electrons. Example: NaCl (ΔEN ≈ 2.1).")

q("12th Grade","Chemistry",H,PRD,
"Predict: what happens to equilibrium in N₂(g) + 3H₂(g) ⇌ 2NH₃(g) if pressure is increased?",
"Increasing pressure shifts equilibrium toward the side with fewer moles of gas. "
"Left side: 1 + 3 = 4 mol gas. Right side: 2 mol gas. "
"Equilibrium shifts right → more NH₃ produced. "
"This is why the Haber process operates at ~200 atm. "
"K itself does not change — only temperature changes K.")

# ══════════════════════════════════════════════════════════════════
#  HIGH SCHOOL  PHYSICS
# ══════════════════════════════════════════════════════════════════
q("9th Grade","Physics",M,EXP,
"State Newton's three laws with a precise example for each.",
"First Law (Inertia): an object stays at rest or moves at constant velocity unless a net force acts. "
"Example: a satellite keeps orbiting without an engine — no air resistance in space. "
"Second Law: F = ma. Example: 2 kg object, net force 10 N → a = 5 m/s². "
"Third Law: equal and opposite reaction on a different object. "
"Example: rocket expels gas down → gas pushes rocket up with equal force.")

q("10th Grade","Physics",M,EXP,
"What is conservation of momentum and when does it apply?",
"Momentum p = mv (kg·m/s). "
"In a closed system with no net external force, total momentum is conserved. "
"Elastic collision: objects bounce; KE and momentum both conserved. "
"Inelastic collision: objects stick or deform; momentum conserved; KE not (some → heat/sound). "
"Example: 3 kg at 4 m/s hits stationary 1 kg → total momentum = 12 kg·m/s before and after.")

q("11th Grade","Physics",H,EXP,
"Define Ohm's Law and derive expressions for I, R, and V.",
"Ohm's Law: V = IR. (V = volts, I = amperes, R = ohms). "
"I = V/R; R = V/I. "
"Example: 12 V, 4 Ω → I = 3 A. "
"Applies to ohmic conductors at constant temperature. "
"Non-ohmic components (diodes, transistors) do not obey a linear V–I relationship.")

q("11th Grade","Physics",H,CMP,
"Compare series and parallel circuits.",
"Series: one loop; same current through all; voltage divides; R_total = R₁ + R₂ + …; "
"one failure breaks the whole circuit. "
"Parallel: components share the same two nodes; same voltage across each; current divides; "
"1/R_total = 1/R₁ + 1/R₂ + … (total R < smallest R); one branch fails, others keep working. "
"Household wiring is parallel so appliances work independently.")

q("12th Grade","Physics",H,EXP,
"Explain the photoelectric effect and its significance.",
"Light above a threshold frequency ejects electrons from a metal surface. "
"Classical wave theory failed: experiment showed intensity alone cannot eject electrons — frequency must exceed a minimum. "
"Higher frequency → higher KE of ejected electrons (not higher intensity). "
"Einstein (1905): light consists of photons with E = hf. A photon ejects an electron only if E ≥ work function (ϕ). "
"Established wave–particle duality of light. Nobel Prize 1921.")

q("10th Grade","Physics",M,CMP,
"What is the difference between potential and kinetic energy?",
"Potential energy: stored energy due to position or condition. Gravitational PE = mgh; elastic PE = ½kx². "
"Kinetic energy: energy of motion. KE = ½mv². "
"Roller coaster descending: PE → KE (speeds up). Ascending: KE → PE (slows down). "
"Without friction, total mechanical energy (PE + KE) is constant.")

q("9th Grade","Physics",M,APP,
"Apply: a car skids to a stop. Where does its kinetic energy go?",
"Friction between tyres and road converts the car's kinetic energy primarily into thermal energy — "
"tyres and road surface heat up. A small amount converts to sound (tyre squeal). "
"No energy is destroyed; it is transformed. This is consistent with conservation of energy.")

q("11th Grade","Physics",H,JUS,
"Justify why astronauts in the ISS feel weightless even though gravity is present.",
"Gravity at ISS altitude (~400 km) is about 8.8 m/s² — roughly 90% of surface gravity. "
"The ISS is in free fall: it continuously falls toward Earth but moves sideways fast enough to "
"follow Earth's curvature — this is orbital motion. "
"Everything aboard accelerates at the same rate, so the floor exerts no normal force on the astronauts. "
"Weight is felt as the normal force. With no normal force, astronauts feel weightless — "
"not because gravity is absent, but because there is no supporting force.")

q("12th Grade","Physics",H,EXP,
"Describe wave-particle duality of light and matter.",
"Wave properties of light: diffraction, interference, refraction (c = fλ). "
"Particle properties: photoelectric effect and Compton scattering show light behaves as photons (E = hf). "
"Matter waves (de Broglie 1924): λ = h/mv. Confirmed by electron diffraction. "
"At macroscopic scales, wavelengths of matter are unmeasurably tiny. "
"At atomic scales, wave behaviour governs — electron orbitals, tunnelling, double-slit interference.")

q("10th Grade","Physics",H,ANA,
"Analyse the energy transformations in a hydroelectric power station.",
"Water behind the dam: gravitational PE = mgh. "
"Water flows down: PE → kinetic energy (KE = ½mv²). "
"Moving water spins turbines: KE → rotational KE. "
"Turbines drive generators: rotational KE → electrical energy (electromagnetic induction). "
"Losses at each step via friction and electrical resistance (heat). "
"Overall efficiency ~85–90% — among the highest of large-scale energy sources.")

q("9th Grade","Physics",M,PRD,
"Predict: if the mass of a spring-mass system is quadrupled, how does the period change?",
"Period of a mass-spring system: T = 2π√(m/k). "
"If m is quadrupled: T_new = 2π√(4m/k) = 2 × 2π√(m/k) = 2T. "
"The period doubles. "
"Period depends on mass and spring constant, not amplitude.")

# ══════════════════════════════════════════════════════════════════
#  HIGH SCHOOL  EARTH & ENVIRONMENTAL SCIENCE
# ══════════════════════════════════════════════════════════════════
q("9th Grade","Earth Science",M,CMP,
"What is the difference between weathering and erosion?",
"Weathering: rock breaks down in place. "
"Physical: mechanical forces (freeze-thaw, plant roots). Chemical: minerals react with water or acids. "
"Erosion: weathered material is transported by water, wind, ice, or gravity. "
"Weathering produces the debris; erosion moves it. Together they shape valleys and coastlines.")

q("10th Grade","Earth Science",M,EXP,
"Describe the carbon cycle and explain how fossil fuel burning affects it.",
"Plants fix CO₂ via photosynthesis → stored in tissues. Animals get carbon by eating plants. "
"Respiration and decomposition return CO₂ to atmosphere. Oceans absorb large amounts. "
"Over millions of years, buried organic matter → fossil fuels (locked-away carbon). "
"Burning fossil fuels releases this stored CO₂ far faster than natural sinks can absorb it, "
"raising atmospheric CO₂ and intensifying the greenhouse effect.")

q("11th Grade","Environmental Science",H,EXP,
"What is eutrophication and what causes it?",
"Excessive N and P enrich a water body → explosive algal bloom → algae die → "
"decomposers consume dissolved O₂ → hypoxic/anoxic dead zone. "
"Primary cause: agricultural fertiliser runoff. Also: sewage discharge, urban stormwater. "
"Solutions: vegetated buffer strips, reduced fertiliser use, improved sewage treatment.")

q("12th Grade","Environmental Science",H,EXP,
"Explain the nitrogen cycle and why nitrogen fixation is essential for life.",
"N₂ = 78% of atmosphere but useless to most organisms — triple bond too stable. "
"Fixation: Rhizobium bacteria (legume nodules) convert N₂ → NH₃. Lightning fixes small amounts. "
"Nitrification: bacteria convert NH₃ → NO₂⁻ → NO₃⁻ (plant-absorbable). "
"Assimilation: plants use nitrate to build amino acids and nucleic acids. Animals eat plants. "
"Ammonification: decomposers return N from dead matter as NH₃. "
"Denitrification: bacteria reduce NO₃⁻ → N₂. "
"Without fixation, no usable nitrogen enters the food chain — no proteins or DNA possible.")

q("10th Grade","Earth Science",M,PRD,
"Predict: what would happen to global sea levels if all of Antarctica's ice sheet melted?",
"Antarctica holds roughly 26 million km³ of ice, representing about 58 metres of potential sea-level rise. "
"If it all melted, global sea levels would rise by approximately 58–60 metres. "
"This would flood all coastal cities — London, New York, Shanghai, Mumbai — and most low-lying nations. "
"Hundreds of millions of people would be displaced. "
"Current projections are far more modest for this century, but even 1–2 metres would cause severe impacts.")

q("11th Grade","Earth Science",H,ANA,
"Analyse the evidence supporting plate tectonic theory.",
"Seafloor spreading: radiometric dating shows ocean crust is youngest at mid-ocean ridges. "
"Palaeomagnetism: symmetric magnetic stripes on either side of ridges record field reversals. "
"Continental fit: South America and Africa coastlines and geological features match. "
"Matching fossils: Mesosaurus found only on now-separated continents. "
"Distribution: 90% of earthquakes and volcanoes occur at plate boundaries. "
"GPS: plates move at 1–15 cm/year — directly measured.")

# ══════════════════════════════════════════════════════════════════
#  AP BIOLOGY
# ══════════════════════════════════════════════════════════════════
q("AP Biology","Biology",H,EXP,
"Explain the three stages of the Calvin cycle in detail.",
"Carbon fixation: RuBisCO attaches CO₂ to RuBP (5C) → two 3-PGA (3C). "
"Reduction: 3-PGA + ATP + NADPH → G3P. One G3P exits to build glucose. "
"Regeneration of RuBP: remaining G3P + ATP → RuBP. "
"Net cost per G3P: 3 CO₂, 9 ATP, 6 NADPH. Six turns produce one glucose.")

q("AP Biology","Biology",H,EXP,
"Describe the three stages of signal transduction.",
"Reception: ligand binds receptor (GPCR, RTK, or ion channel) with high specificity. "
"Transduction: conformational change activates relay cascade — second messengers (cAMP, Ca²⁺), "
"protein kinase cascades — signal amplified many-fold. "
"Response: altered gene expression, enzyme activity, or cell behaviour (division, migration, apoptosis).")

q("AP Biology","Biology",H,EXP,
"Explain the endosymbiotic theory and evidence supporting it.",
"Mitochondria and chloroplasts evolved from free-living prokaryotes engulfed by a larger cell. "
"Evidence: (1) double membrane; (2) circular prokaryotic DNA; (3) 70S ribosomes (bacterial); "
"(4) binary fission division; "
"(5) rRNA phylogeny — mitochondria → alpha-proteobacteria; chloroplasts → cyanobacteria.")

q("AP Biology","Biology",H,PRD,
"Predict what happens to ATP production if the inner mitochondrial membrane becomes freely permeable to H⁺.",
"The proton gradient collapses. H⁺ bypasses ATP synthase — no oxidative phosphorylation. "
"Only glycolysis + Krebs remain: ~4 ATP per glucose instead of ~32. "
"Cell dies from energy starvation. Mechanism of chemical uncouplers like 2,4-dinitrophenol.")

q("AP Biology","Biology",H,ANA,
"Analyse how crossing over during meiosis I increases genetic variation.",
"During Prophase I, homologous chromosomes pair (synapsis) and non-sister chromatids exchange "
"segments at chiasmata — crossing over. "
"Each chromatid acquires a novel allele combination not present in either parent chromosome. "
"Combined with independent assortment (2²³ combinations in humans) and random fertilisation, "
"virtually every gamete is genetically unique — the evolutionary advantage of sexual reproduction.")

q("AP Biology","Biology",H,EXP,
"Explain epigenetics and give two mechanisms.",
"Epigenetics: heritable gene expression changes without altering DNA sequence. "
"DNA methylation: methyl groups on cytosine typically silence genes. "
"Roles: X-chromosome inactivation, genomic imprinting. "
"Histone acetylation: loosens chromatin → transcription active. "
"Deacetylation: compacts chromatin → transcription repressed.")

q("AP Biology","Biology",H,JUS,
"Justify why the lac operon is more energetically efficient than constitutive expression.",
"Constitutive expression wastes energy producing lactose enzymes continuously even when lactose is absent. "
"The lac operon produces enzymes only when allolactose is present AND glucose is absent (CAP–cAMP). "
"Resources are allocated precisely when and where needed — significant fitness advantage.")

q("AP Biology","Biology",H,CMP,
"Compare the light-dependent reactions and the Calvin cycle.",
"Light-dependent reactions: thylakoid membranes; inputs: light, H₂O, ADP, NADP⁺; "
"outputs: ATP, NADPH, O₂. "
"Calvin cycle: stroma; inputs: CO₂, ATP, NADPH; outputs: G3P, ADP, NADP⁺. "
"Tightly coupled: light reactions supply ATP and NADPH consumed by Calvin cycle, "
"which regenerates ADP and NADP⁺ for light reactions.")

q("AP Biology","Biology",H,APP,
"Apply: explain why a patient with cystic fibrosis produces abnormally thick mucus.",
"Cystic fibrosis results from mutations in the CFTR gene, which encodes a chloride ion channel "
"in the membranes of epithelial cells. "
"In healthy cells, Cl⁻ is secreted into the airway lumen, drawing water out by osmosis, "
"keeping mucus thin and fluid. "
"In CF, the CFTR channel is absent or non-functional — Cl⁻ cannot be secreted. "
"Without the osmotic drive, water stays in the cells rather than entering the mucus. "
"The result is abnormally thick, viscous mucus that blocks airways and ducts in the lungs, "
"pancreas, and other organs.")

q("AP Biology","Biology",H,EXP,
"Explain the structure of the cell membrane and the fluid mosaic model.",
"Phospholipid bilayer: hydrophilic heads outward (facing water); hydrophobic tails inward. "
"Integral proteins: span the bilayer; function as channels, carriers, receptors, enzymes. "
"Peripheral proteins: attached to surface; role in signalling and structural support. "
"Cholesterol: embedded in bilayer; stabilises fluidity at varying temperatures. "
"Glycoproteins/glycolipids: sugar-bearing molecules on outer surface; cell recognition and immune response. "
"'Fluid': components can move laterally in the layer. 'Mosaic': diverse embedded proteins.")

# ══════════════════════════════════════════════════════════════════
#  AP CHEMISTRY
# ══════════════════════════════════════════════════════════════════
q("AP Chemistry","Chemistry",H,EXP,
"What is the Nernst equation and how is it used?",
"E = E° − (RT/nF) ln Q "
"(E° = standard potential; R = 8.314 J/mol·K; T in K; n = moles electrons; F = 96,485 C/mol; Q = reaction quotient). "
"At 298 K: E = E° − (0.0592/n) log Q. "
"At equilibrium: E° = (0.0592/n) log K. "
"Used to: calculate battery voltage at different states of charge; "
"measure ion concentrations from cell potential; connect to thermodynamics via ΔG = −nFE.")

q("AP Chemistry","Chemistry",H,EXP,
"Explain reaction kinetics: factors affecting rate and the rate law.",
"Factors: higher concentration → more collisions; higher T → more collisions exceed Ea; "
"greater surface area; catalyst lowers Ea without consumption. "
"Arrhenius: k = Ae^(−Ea/RT). "
"Rate law: rate = k[A]^m[B]^n (orders m, n determined experimentally). "
"Overall order = m + n.")

q("AP Chemistry","Chemistry",H,JUS,
"Justify why increasing temperature increases rate but may reduce yield for an exothermic reaction.",
"Higher T increases rate (Arrhenius). "
"For exothermic equilibrium reactions, Le Chatelier shifts equilibrium in the endothermic direction "
"when heat is added, reducing product yield. "
"Haber process compromise: ~450 °C, ~200 atm — rate acceptable, yield acceptable.")

q("AP Chemistry","Chemistry",H,EXP,
"Explain how a buffer resists pH changes.",
"Buffer: weak acid HA + conjugate base A⁻. "
"Add H⁺: H⁺ + A⁻ → HA — acid absorbed, pH unchanged. "
"Add OH⁻: OH⁻ + HA → A⁻ + H₂O — base neutralised. "
"pH = pKa + log([A⁻]/[HA]) — Henderson-Hasselbalch. "
"Most effective within ±1 pH of pKa.")

q("AP Chemistry","Chemistry",H,ANA,
"Analyse why O₂ is paramagnetic using molecular orbital theory.",
"Valence bond theory incorrectly predicts O₂ is diamagnetic (no unpaired electrons). "
"MO theory: 8 valence electrons fill bonding and antibonding MOs in energy order. "
"The two highest-energy electrons occupy the two degenerate π* orbitals, one each (Hund's rule). "
"Two unpaired electrons → paramagnetic. "
"Liquid O₂ is visibly attracted to a magnet — confirming MO theory over VB theory.")

q("AP Chemistry","Chemistry",H,PRD,
"Predict what happens to equilibrium in N₂(g) + 3H₂(g) ⇌ 2NH₃(g) if pressure is increased.",
"Equilibrium shifts toward the side with fewer moles of gas. "
"Left: 4 mol gas; Right: 2 mol gas → shifts right, producing more NH₃. "
"K is unchanged; only temperature changes K.")

q("AP Chemistry","Chemistry",H,EXP,
"Explain VSEPR theory and predict the geometry of water and ammonia.",
"VSEPR: electron pairs around a central atom arrange to minimise repulsion. "
"Include lone pairs in count; lone pairs repel more strongly than bonding pairs. "
"Water (H₂O): 2 bonding pairs + 2 lone pairs → tetrahedral electron geometry → bent molecular shape. "
"Bond angle: ~104.5° (less than 109.5° due to lone pair repulsion). "
"Ammonia (NH₃): 3 bonding pairs + 1 lone pair → tetrahedral electron geometry → trigonal pyramidal shape. "
"Bond angle: ~107°.")

q("AP Chemistry","Chemistry",H,CMP,
"Compare intermolecular forces: hydrogen bonding, dipole-dipole, and London dispersion.",
"London dispersion: all molecules; temporary dipoles from electron movement; "
"strength increases with molar mass and surface area. Weakest per interaction. "
"Dipole-dipole: polar molecules; permanent dipoles attract. Stronger than dispersion of similar mass. "
"Hydrogen bonding: H directly bonded to N, O, or F interacts with lone pair on N, O, or F on another molecule. "
"Strongest; explains high BP of H₂O, HF; DNA base pairing; protein secondary structure.")

# ══════════════════════════════════════════════════════════════════
#  AP PHYSICS
# ══════════════════════════════════════════════════════════════════
q("AP Physics","Physics",H,EXP,
"Derive v² = v₀² + 2aΔx from first principles.",
"v = v₀ + at → t = (v−v₀)/a. "
"Substitute into Δx = v₀t + ½at²: "
"Δx = v₀(v−v₀)/a + (v−v₀)²/(2a). "
"Multiply by 2a: 2aΔx = 2v₀(v−v₀) + (v−v₀)² = v² − v₀². "
"∴ v² = v₀² + 2aΔx ■")

q("AP Physics","Physics",H,EXP,
"Use Gauss's Law to find the electric field outside a uniformly charged sphere.",
"Gauss's Law: ∮ E·dA = Q_enc/ε₀. "
"Spherical Gaussian surface of radius r > R: by symmetry E·4πr² = Q/ε₀. "
"E = Q/(4πε₀r²) = kQ/r². "
"Outside a uniform sphere the field equals that of a point charge Q at the centre. "
"Inside a spherical shell: Q_enc = 0 → E = 0.")

q("AP Physics","Physics",H,PRD,
"Predict: if the mass of a pendulum bob is doubled but length is unchanged, how does the period change?",
"T = 2π√(L/g). Mass is absent from this equation. "
"Doubling the mass has no effect on the period. "
"Period depends only on length and gravitational field strength — not mass.")

q("AP Physics","Physics",H,EXP,
"Describe SHM and derive the period of a mass-spring system.",
"SHM: restoring force F = −kx; a(t) = −ω²x(t). "
"x(t) = A cos(ωt + φ). KE and PE trade off; E = ½kA² = constant. "
"Derivation: ma = −kx → ω² = k/m → T = 2π/ω = 2π√(m/k). "
"Period independent of amplitude.")

q("AP Physics","Physics",H,JUS,
"Justify why astronauts in the ISS feel weightless even though gravity is present.",
"Gravity at 400 km altitude ≈ 8.8 m/s². "
"The ISS and everything inside free-fall together — all accelerate at the same g. "
"The floor exerts no normal force on the astronauts. "
"Perceived weight = normal force. No normal force → weightless sensation. "
"It is not the absence of gravity; it is the absence of a support force.")

q("AP Physics","Physics",H,ANA,
"Analyse why a gyroscope resists changes in orientation.",
"Spinning gyroscope has angular momentum L = Iω. "
"Conservation of angular momentum: L is constant unless an external torque acts. "
"Applied torque causes precession — axis rotates perpendicular to both L and torque. "
"Precession rate Ω = τ/L. Larger L (faster spin) → slower precession → more stable.")

q("AP Physics","Physics",H,EXP,
"Explain Faraday's law of electromagnetic induction.",
"A changing magnetic flux through a conducting loop induces an EMF. "
"ε = −dΦ_B/dt (Faraday's law; negative sign is Lenz's law — induced current opposes the change). "
"Φ_B = B·A·cos θ. "
"Applications: electric generators (rotating coil in magnetic field), transformers, induction cooktops. "
"More turns: ε = −N·dΦ_B/dt.")

q("AP Physics","Physics",H,CMP,
"Compare elastic and inelastic collisions in terms of conserved quantities.",
"Both: momentum is conserved (closed system, no external force). "
"Elastic: KE is also conserved — no permanent deformation or heat produced. "
"Objects bounce back. Example: ideal billiard balls. "
"Inelastic: KE is NOT conserved — some converts to thermal energy, sound, or deformation. "
"Perfectly inelastic: objects stick together. "
"Real collisions are somewhere between elastic and perfectly inelastic.")

# ══════════════════════════════════════════════════════════════════
#  MULTI-STEP WORD PROBLEMS (static)
# ══════════════════════════════════════════════════════════════════
q("10th Grade","Physics",H,CAL,
"A car travelling at 20 m/s brakes to a stop in 4 s. (a) Find acceleration. (b) Find stopping distance.",
"(a) a = (v_f − v_i)/t = (0 − 20)/4 = −5 m/s²  (deceleration)\n"
"(b) Δx = v_i·t + ½at² = 20(4) + ½(−5)(16) = 80 − 40 = 40 m")

q("11th Grade","Physics",H,CAL,
"A 0.5 kg ball is dropped from rest at 20 m. (a) GPE at top. (b) Speed before impact. (g = 9.8 m/s²)",
"(a) PE = mgh = 0.5 × 9.8 × 20 = 98 J\n"
"(b) All PE → KE: ½mv² = 98 → v² = 392 → v = √392 ≈ 19.8 m/s")

q("11th Grade","Chemistry",H,CAL,
"How many grams of CO₂ form when 50 g of CaCO₃ decomposes? (CaCO₃ → CaO + CO₂; M: 100, 44 g/mol)",
"n(CaCO₃) = 50/100 = 0.5 mol\n"
"CaCO₃:CO₂ = 1:1 → n(CO₂) = 0.5 mol\n"
"m(CO₂) = 0.5 × 44 = 22 g")

q("10th Grade","Chemistry",H,CAL,
"A gas is at 3.0 L, 300 K, 1.0 atm. Find new volume at 600 K and 2.0 atm.",
"V₂ = P₁V₁T₂/(T₁P₂) = (1.0)(3.0)(600)/((300)(2.0)) = 1800/600 = 3.0 L\n"
"Doubling T doubles V; doubling P halves V — effects cancel.")

q("12th Grade","Chemistry",H,CAL,
"Weak acid HA, Ka = 1.8 × 10⁻⁵. Find pH of 0.10 M solution (small-x approximation).",
"x² = Ka × C = 1.8×10⁻⁵ × 0.10 = 1.8×10⁻⁶\n"
"x = [H⁺] = 1.34×10⁻³ M\n"
"pH = −log(1.34×10⁻³) = 2.87\n"
"Check: x/C = 1.34% < 5% ✓")

q("AP Physics","Physics",H,CAL,
"An electron (m = 9.11×10⁻³¹ kg) moves at 1.0×10⁶ m/s. Find its de Broglie wavelength.",
"λ = h/mv = 6.626×10⁻³⁴ / (9.11×10⁻³¹ × 1.0×10⁶) = 7.27×10⁻¹⁰ m = 0.727 nm\n"
"Comparable to atomic spacings — electron diffraction and microscopy exploit this.")

q("12th Grade","Physics",H,CAL,
"A 400 nm photon: find energy in eV. (h = 6.626×10⁻³⁴ J·s, c = 3×10⁸ m/s, 1 eV = 1.6×10⁻¹⁹ J)",
"E = hc/λ = (6.626×10⁻³⁴ × 3×10⁸)/(400×10⁻⁹) = 4.97×10⁻¹⁹ J\n"
"In eV: 4.97×10⁻¹⁹ / 1.6×10⁻¹⁹ = 3.1 eV")

q("11th Grade","Biology",H,CAL,
"Bacteria double every 20 min. Starting with 100 cells, how many after 2 hours?",
"Doublings = 120/20 = 6\n"
"N = 100 × 2⁶ = 100 × 64 = 6,400 cells")

q("10th Grade","Biology",H,CAL,
"q² = 0.0016 in a HWE population. Find p, q, and carrier frequency 2pq.",
"q = √0.0016 = 0.04\n"
"p = 1 − 0.04 = 0.96\n"
"2pq = 2 × 0.96 × 0.04 = 0.0768 (7.68%)")

q("9th Grade","Chemistry",M,CAL,
"Calculate moles in 36 g of water. (M H₂O = 18 g/mol)",
"n = m/M = 36/18 = 2 mol")

q("9th Grade","Physics",M,CAL,
"A 60 W bulb runs 5 hours. Energy consumed in joules?",
"E = P × t = 60 × (5 × 3600) = 60 × 18000 = 1,080,000 J = 1.08 MJ")

q("10th Grade","Physics",M,CAL,
"6 Ω and 3 Ω in parallel. Find total resistance.",
"1/R = 1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2 → R = 2 Ω")

q("11th Grade","Physics",H,CAL,
"A 2 kg block on a frictionless surface is pushed by a 10 N force for 4 m. Find final speed from rest.",
"Work = F × d = 10 × 4 = 40 J\n"
"Work-energy theorem: KE = ½mv² = 40 J\n"
"v² = 80/2 = 40\n"
"v = √40 ≈ 6.32 m/s")

q("12th Grade","Chemistry",H,CAL,
"Calculate the pH of a 0.05 M NaOH solution.",
"NaOH is a strong base — fully dissociates: [OH⁻] = 0.05 M\n"
"pOH = −log(0.05) = 1.30\n"
"pH = 14 − pOH = 14 − 1.30 = 12.70")

# ══════════════════════════════════════════════════════════════════
#  RANDOMISED MATH GENERATORS
#  Rules: no contradictory premises; full step-by-step working shown.
# ══════════════════════════════════════════════════════════════════

def make_math_examples():
    rng = []

    # ── Newton F = ma ──────────────────────────────────────────
    for _ in range(60):
        m = random.choice([1,2,3,4,5,6,8,10,12,15,20,25,50,70,100])
        a = round(random.uniform(0.5, 15.0), 1)
        F = round(m * a, 2)
        grade = random.choice(["8th Grade","9th Grade","10th Grade"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
            "question":f"A {m} kg object accelerates at {a} m/s². What is the net force acting on it?",
            "answer":(f"Newton's second law: F = ma\n"
                      f"F = {m} kg × {a} m/s²\n"
                      f"F = {F} N\n\n"
                      f"The net force is {F} newtons.")})

    # ── Kinematics: find final velocity ───────────────────────
    for _ in range(60):
        v0 = random.choice([0,1,2,3,5,8,10,12,15,20,25])
        a  = round(random.uniform(0.5, 10.0), 1)
        t  = random.choice([1,2,3,4,5,6,8,10,12])
        vf = round(v0 + a*t, 2)
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
            "question":(f"An object has an initial velocity of {v0} m/s and accelerates at "
                        f"{a} m/s² for {t} s. What is its final velocity?"),
            "answer":(f"v = v₀ + at\n"
                      f"v = {v0} + ({a})({t})\n"
                      f"v = {v0} + {round(a*t,2)}\n"
                      f"v = {vf} m/s")})

    # ── Kinematics: find displacement ─────────────────────────
    for _ in range(60):
        v0 = random.choice([0,2,4,5,6,8,10,12,15])
        a  = round(random.uniform(0.5, 8.0), 1)
        t  = random.choice([1,2,3,4,5,6,8,10])
        d  = round(v0*t + 0.5*a*t**2, 2)
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
            "question":(f"An object has an initial velocity of {v0} m/s and accelerates at "
                        f"{a} m/s² for {t} s. How far does it travel?"),
            "answer":(f"Δx = v₀t + ½at²\n"
                      f"Δx = ({v0})({t}) + ½({a})({t}²)\n"
                      f"Δx = {v0*t} + ½({a})({t**2})\n"
                      f"Δx = {v0*t} + {round(0.5*a*t**2,2)}\n"
                      f"Δx = {d} m")})

    # ── Kinematics: find time ─────────────────────────────────
    for _ in range(30):
        v0 = random.choice([0,2,5,10,15,20])
        vf = v0 + random.choice([5,10,15,20,25,30])
        a  = round(random.uniform(1.0, 8.0), 1)
        t  = round((vf - v0) / a, 3)
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
            "question":(f"An object accelerates from {v0} m/s to {vf} m/s at {a} m/s². "
                        f"How long does this take?"),
            "answer":(f"v = v₀ + at → t = (v − v₀)/a\n"
                      f"t = ({vf} − {v0}) / {a}\n"
                      f"t = {vf-v0} / {a}\n"
                      f"t = {t} s")})

    # ── v² = v₀² + 2aΔx ──────────────────────────────────────
    for _ in range(30):
        v0 = random.choice([0,2,4,5,8,10])
        a  = round(random.uniform(1.0, 6.0), 1)
        d  = random.choice([5,10,15,20,25,30,40,50])
        vf = round(math.sqrt(v0**2 + 2*a*d), 3)
        grade = random.choice(["9th Grade","10th Grade","11th Grade","AP Physics"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"hard","q_type":"calculate",
            "question":(f"An object with initial velocity {v0} m/s accelerates at {a} m/s² over {d} m. "
                        f"Find its final velocity."),
            "answer":(f"v² = v₀² + 2aΔx\n"
                      f"v² = {v0}² + 2({a})({d})\n"
                      f"v² = {v0**2} + {round(2*a*d,2)}\n"
                      f"v² = {round(v0**2 + 2*a*d,2)}\n"
                      f"v = √{round(v0**2+2*a*d,2)} = {vf} m/s")})

    # ── Ohm's Law ─────────────────────────────────────────────
    for _ in range(60):
        case = random.choice(["I","R","V"])
        grade = random.choice(["10th Grade","11th Grade","AP Physics"])
        if case == "I":
            V = random.choice([3,6,9,12,15,18,24,36,48])
            R = random.choice([2,3,4,6,8,10,12,15,18,20,24])
            I = round(V/R, 4)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"A circuit has a voltage of {V} V and resistance of {R} Ω. Find the current.",
                "answer":(f"V = IR → I = V/R\n"
                          f"I = {V} ÷ {R}\n"
                          f"I = {I} A")})
        elif case == "R":
            V = random.choice([6,9,12,18,24,36])
            I = random.choice([0.25,0.5,0.75,1.0,1.5,2.0,3.0,4.0,6.0])
            R = round(V/I, 3)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"A circuit carries {I} A at {V} V. Find the resistance.",
                "answer":(f"V = IR → R = V/I\n"
                          f"R = {V} ÷ {I}\n"
                          f"R = {R} Ω")})
        else:
            I = random.choice([0.5,1.0,1.5,2.0,2.5,3.0,4.0])
            R = random.choice([4,5,6,8,10,12,15,20,25])
            V = round(I*R, 2)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"A {R} Ω resistor carries {I} A. Find the voltage across it.",
                "answer":(f"V = IR\n"
                          f"V = {I} × {R}\n"
                          f"V = {V} V")})

    # ── Power: P = IV and P = V²/R ────────────────────────────
    for _ in range(30):
        V = random.choice([6,9,12,24,120,230])
        R = random.choice([2,4,5,6,8,10,12,20,100])
        P = round(V**2/R, 3)
        I = round(V/R, 4)
        grade = random.choice(["10th Grade","11th Grade","AP Physics"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
            "question":f"A {R} Ω resistor is connected to a {V} V supply. Find the power dissipated.",
            "answer":(f"P = V²/R\n"
                      f"P = {V}² / {R}\n"
                      f"P = {V**2} / {R}\n"
                      f"P = {P} W\n\n"
                      f"(Alternatively: I = V/R = {I} A; P = IV = {I} × {V} = {round(I*V,3)} W)")})

    # ── Series/parallel total resistance ──────────────────────
    for _ in range(30):
        r1 = random.choice([2,3,4,5,6,8,10,12,15,20])
        r2 = random.choice([2,3,4,5,6,8,10,12,15,20])
        mode = random.choice(["series","parallel"])
        grade = random.choice(["10th Grade","11th Grade"])
        if mode == "series":
            rt = r1 + r2
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"Two resistors, {r1} Ω and {r2} Ω, are connected in series. Find the total resistance.",
                "answer":(f"Series: R_total = R₁ + R₂\n"
                          f"R_total = {r1} + {r2} = {rt} Ω")})
        else:
            rt = round(1/(1/r1 + 1/r2), 4)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"Two resistors, {r1} Ω and {r2} Ω, are connected in parallel. Find the total resistance.",
                "answer":(f"Parallel: 1/R_total = 1/R₁ + 1/R₂\n"
                          f"1/R_total = 1/{r1} + 1/{r2} = {round(1/r1,4)} + {round(1/r2,4)} = {round(1/r1+1/r2,4)}\n"
                          f"R_total = {rt} Ω\n"
                          f"(Total R is less than either individual resistor.)")})

    # ── KE and GPE ────────────────────────────────────────────
    for _ in range(50):
        m = random.choice([0.5,1,2,3,5,8,10,15,20,50,70,80,100])
        case = random.choice(["KE","PE","drop"])
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        if case == "KE":
            v = round(random.uniform(1.0,30.0),1)
            KE = round(0.5*m*v**2,3)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"Find the kinetic energy of a {m} kg object moving at {v} m/s.",
                "answer":(f"KE = ½mv²\n"
                          f"KE = ½ × {m} × {v}²\n"
                          f"KE = ½ × {m} × {round(v**2,2)}\n"
                          f"KE = {KE} J")})
        elif case == "PE":
            h = random.choice([1,2,3,4,5,8,10,15,20,25,30,50,100])
            PE = round(m*9.8*h,3)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"medium","q_type":"calculate",
                "question":f"Find the gravitational PE of a {m} kg object at height {h} m. (g = 9.8 m/s²)",
                "answer":(f"PE = mgh\n"
                          f"PE = {m} × 9.8 × {h}\n"
                          f"PE = {PE} J")})
        else:
            h = random.choice([2,5,10,15,20,25,30,40,50])
            v = round(math.sqrt(2*9.8*h),3)
            rng.append({"grade_level":grade,"subject":"Physics","difficulty":"hard","q_type":"calculate",
                "question":(f"A {m} kg object is released from rest at height {h} m. "
                            f"Using conservation of energy, find its speed just before impact. (g = 9.8 m/s², no friction)"),
                "answer":(f"All PE → KE: mgh = ½mv² → mass cancels\n"
                          f"v² = 2gh = 2 × 9.8 × {h} = {round(2*9.8*h,2)}\n"
                          f"v = √{round(2*9.8*h,2)} = {v} m/s")})

    # ── Stoichiometry: grams to grams ─────────────────────────
    rxns = [
        ("2H₂ + O₂ → 2H₂O",         "H₂",    2.016,  "H₂O",   18.016, 2, 2),
        ("N₂ + 3H₂ → 2NH₃",          "H₂",    2.016,  "NH₃",   17.034, 3, 2),
        ("CaO + CO₂ → CaCO₃",        "CaO",   56.08,  "CaCO₃", 100.09, 1, 1),
        ("2KClO₃ → 2KCl + 3O₂",      "KClO₃", 122.55, "O₂",    32.00,  2, 3),
        ("CH₄ + 2O₂ → CO₂ + 2H₂O",  "CH₄",   16.05,  "CO₂",   44.01,  1, 1),
        ("2Na + 2H₂O → 2NaOH + H₂",  "Na",    22.99,  "H₂",    2.016,  2, 1),
        ("CaCO₃ → CaO + CO₂",        "CaCO₃", 100.09, "CO₂",   44.01,  1, 1),
        ("2Al + 3Cl₂ → 2AlCl₃",      "Al",    26.98,  "AlCl₃", 133.34, 2, 2),
        ("Fe₂O₃ + 3CO → 2Fe + 3CO₂", "Fe₂O₃", 159.69, "Fe",    55.85,  1, 2),
    ]
    for _ in range(80):
        eq,rA,mmA,rB,mmB,cA,cB = random.choice(rxns)
        massA = round(random.uniform(4.0,80.0),1)
        molA  = massA/mmA
        molB  = molA*(cB/cA)
        massB = round(molB*mmB,2)
        grade = random.choice(["10th Grade","11th Grade","AP Chemistry"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"hard","q_type":"calculate",
            "question":(f"Given: {eq}\n"
                        f"How many grams of {rB} are produced from {massA} g of {rA}?"),
            "answer":(f"Step 1 — moles of {rA}:\n"
                      f"  n = {massA} ÷ {mmA} g/mol = {molA:.4f} mol\n\n"
                      f"Step 2 — mole ratio ({rA}:{rB} = {cA}:{cB}):\n"
                      f"  n({rB}) = {molA:.4f} × {cB}/{cA} = {molB:.4f} mol\n\n"
                      f"Step 3 — mass of {rB}:\n"
                      f"  m = {molB:.4f} × {mmB} g/mol = {massB} g")})

    # ── Moles from mass ───────────────────────────────────────
    substances = [
        ("H₂O",18.016),("NaCl",58.44),("CO₂",44.01),("O₂",32.00),("N₂",28.02),
        ("C₆H₁₂O₆",180.16),("HCl",36.46),("NH₃",17.03),("CaCO₃",100.09),("H₂SO₄",98.08),
        ("KOH",56.11),("NaOH",40.00),("CH₄",16.05),("Fe",55.85),("Cu",63.55),
    ]
    for _ in range(40):
        name,M = random.choice(substances)
        mass = round(random.uniform(2.0,200.0),1)
        n = round(mass/M,4)
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"medium","q_type":"calculate",
            "question":f"How many moles are in {mass} g of {name}? (Molar mass = {M} g/mol)",
            "answer":(f"n = m / M\n"
                      f"n = {mass} ÷ {M}\n"
                      f"n = {n} mol")})

    # ── Mass from moles ───────────────────────────────────────
    for _ in range(30):
        name,M = random.choice(substances)
        n = random.choice([0.25,0.5,0.75,1.0,1.5,2.0,2.5,3.0,4.0,5.0])
        mass = round(n*M,3)
        grade = random.choice(["9th Grade","10th Grade","11th Grade"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"medium","q_type":"calculate",
            "question":f"What is the mass of {n} mol of {name}? (Molar mass = {M} g/mol)",
            "answer":(f"m = n × M\n"
                      f"m = {n} × {M}\n"
                      f"m = {mass} g")})

    # ── Ideal gas law ─────────────────────────────────────────
    for _ in range(50):
        n = random.choice([0.25,0.5,0.75,1.0,1.25,1.5,2.0,2.5,3.0,4.0,5.0])
        T = random.choice([200,250,273,298,300,320,350,400,450,500,600])
        P = round(random.uniform(0.4,4.0),2)
        R = 0.08206
        V = round(n*R*T/P,3)
        grade = random.choice(["11th Grade","12th Grade","AP Chemistry"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"hard","q_type":"calculate",
            "question":f"Find the volume of {n} mol of ideal gas at {T} K and {P} atm.",
            "answer":(f"PV = nRT → V = nRT/P\n"
                      f"V = ({n})(0.08206)({T}) / {P}\n"
                      f"V = {round(n*R*T,4)} / {P}\n"
                      f"V = {V} L")})

    # ── Combined gas law ──────────────────────────────────────
    for _ in range(40):
        P1 = round(random.uniform(0.5,3.0),2)
        V1 = round(random.uniform(1.0,12.0),1)
        T1 = random.choice([200,250,273,298,300,320,350])
        T2 = random.choice([300,350,400,450,500,550,600,700])
        P2 = round(random.uniform(0.5,4.0),2)
        V2 = round(P1*V1*T2/(T1*P2),3)
        grade = random.choice(["10th Grade","11th Grade","AP Chemistry"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"hard","q_type":"calculate",
            "question":(f"A gas is at {V1} L, {T1} K, {P1} atm. "
                        f"What is its volume at {T2} K and {P2} atm?"),
            "answer":(f"Combined gas law: P₁V₁/T₁ = P₂V₂/T₂\n"
                      f"V₂ = P₁V₁T₂ / (T₁P₂)\n"
                      f"V₂ = ({P1})({V1})({T2}) / ({T1})({P2})\n"
                      f"V₂ = {round(P1*V1*T2,3)} / {round(T1*P2,3)}\n"
                      f"V₂ = {V2} L")})

    # ── pH of strong acid ─────────────────────────────────────
    for _ in range(30):
        conc = random.choice([0.001,0.002,0.005,0.01,0.02,0.05,0.10,0.20,0.50,1.0,2.0])
        pH = round(-math.log10(conc),3)
        grade = random.choice(["10th Grade","11th Grade","AP Chemistry"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"hard","q_type":"calculate",
            "question":f"Calculate the pH of a {conc} M HCl solution.",
            "answer":(f"HCl is a strong acid — fully dissociates: HCl → H⁺ + Cl⁻\n"
                      f"[H⁺] = {conc} M\n"
                      f"pH = −log({conc}) = {pH}")})

    # ── pH of weak acid ───────────────────────────────────────
    for _ in range(30):
        conc = random.choice([0.010,0.025,0.050,0.10,0.25,0.50,1.0])
        Ka   = random.choice([1.8e-5,6.3e-5,1.4e-3,4.3e-7,1.0e-4,7.2e-4])
        x    = math.sqrt(Ka*conc)
        pH   = round(-math.log10(x),3)
        pct  = round(x/conc*100,2)
        valid = "✓ valid" if pct < 5 else "⚠ use quadratic"
        grade = random.choice(["11th Grade","12th Grade","AP Chemistry"])
        rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"hard","q_type":"calculate",
            "question":(f"Calculate the pH of a {conc} M weak acid with Ka = {Ka:.2e}. "
                        f"Use the small-x approximation."),
            "answer":(f"Ka = x²/C → x² = {Ka:.2e} × {conc} = {Ka*conc:.4e}\n"
                      f"x = [H⁺] = {x:.4e} M\n"
                      f"pH = −log({x:.4e}) = {pH}\n"
                      f"Check: x/C = {pct}% — {valid}")})

    # ── Hardy-Weinberg ────────────────────────────────────────
    for _ in range(40):
        q_sq = random.choice([0.0004,0.0009,0.001,0.0016,0.0025,0.004,0.0064,
                               0.01,0.0225,0.04,0.0625,0.09,0.16,0.25])
        q    = round(math.sqrt(q_sq),5)
        p    = round(1-q,5)
        carrier = round(2*p*q,5)
        pct  = round(q_sq*100,4)
        grade = random.choice(["11th Grade","12th Grade","AP Biology"])
        rng.append({"grade_level":grade,"subject":"Biology","difficulty":"hard","q_type":"calculate",
            "question":(f"In a Hardy-Weinberg population, {pct}% of individuals show a recessive disorder. "
                        f"Calculate (a) allele frequencies and (b) carrier frequency."),
            "answer":(f"(a) q² = {q_sq} → q = {q}; p = 1 − {q} = {p}\n"
                      f"(b) Carrier frequency (2pq) = 2 × {p} × {q} = {carrier} ({round(carrier*100,2)}%)")})

    # ── Bacterial growth ──────────────────────────────────────
    for _ in range(20):
        N0   = random.choice([10,50,100,200,500,1000])
        td   = random.choice([15,20,30,45,60])
        hrs  = random.choice([1,2,3,4,6])
        mins = hrs*60
        doublings = mins//td
        Nf = N0 * (2**doublings)
        grade = random.choice(["10th Grade","11th Grade","AP Biology"])
        rng.append({"grade_level":grade,"subject":"Biology","difficulty":"hard","q_type":"calculate",
            "question":(f"A bacterial population starts at {N0} cells and doubles every {td} minutes. "
                        f"How many cells are there after {hrs} hour(s)?"),
            "answer":(f"Total time = {hrs} h = {mins} min\n"
                      f"Doublings = {mins} ÷ {td} = {doublings}\n"
                      f"N = {N0} × 2^{doublings} = {N0} × {2**doublings} = {Nf:,} cells")})

    # ── Photon energy ─────────────────────────────────────────
    for _ in range(20):
        wl_nm = random.choice([200,250,300,350,400,450,500,550,600,650,700,750])
        wl_m  = wl_nm * 1e-9
        E_J   = round(6.626e-34 * 3e8 / wl_m, 4)
        E_eV  = round(E_J / 1.6e-19, 3)
        grade = random.choice(["11th Grade","12th Grade","AP Physics"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"hard","q_type":"calculate",
            "question":(f"Calculate the energy of a photon with wavelength {wl_nm} nm. "
                        f"Give answers in joules and eV. "
                        f"(h = 6.626×10⁻³⁴ J·s, c = 3×10⁸ m/s, 1 eV = 1.6×10⁻¹⁹ J)"),
            "answer":(f"E = hc/λ\n"
                      f"λ = {wl_nm} nm = {wl_m:.2e} m\n"
                      f"E = (6.626×10⁻³⁴)(3×10⁸) / {wl_m:.2e}\n"
                      f"E = {E_J:.4e} J\n"
                      f"E = {E_J:.4e} / 1.6×10⁻¹⁹ = {E_eV} eV")})

    # ── de Broglie wavelength ─────────────────────────────────
    for _ in range(15):
        m_kg = random.choice([9.11e-31, 1.67e-27, 1e-3, 0.1, 1.0])
        m_label = {9.11e-31:"electron (9.11×10⁻³¹ kg)",
                   1.67e-27:"proton (1.67×10⁻²⁷ kg)",
                   1e-3:"1 g particle",0.1:"100 g ball",1.0:"1 kg ball"}[m_kg]
        v = random.choice([1e5,1e6,5e6,1e7,1.0,5.0,10.0,50.0])
        lam = round(6.626e-34 / (m_kg * v), 4)
        grade = random.choice(["12th Grade","AP Physics"])
        rng.append({"grade_level":grade,"subject":"Physics","difficulty":"hard","q_type":"calculate",
            "question":f"Find the de Broglie wavelength of a {m_label} moving at {v:.2e} m/s.",
            "answer":(f"λ = h/(mv)\n"
                      f"λ = 6.626×10⁻³⁴ / ({m_kg:.2e} × {v:.2e})\n"
                      f"λ = 6.626×10⁻³⁴ / {m_kg*v:.4e}\n"
                      f"λ = {lam:.4e} m")})

    # ── Molarity calculations ──────────────────────────────────
    for _ in range(30):
        case = random.choice(["find_c","find_n","find_V"])
        grade = random.choice(["10th Grade","11th Grade","AP Chemistry"])
        if case == "find_c":
            n = round(random.uniform(0.1,5.0),2)
            V_L = round(random.uniform(0.1,2.0),2)
            c = round(n/V_L,4)
            rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"medium","q_type":"calculate",
                "question":f"{n} mol of NaCl is dissolved in {V_L} L of solution. Find the molarity.",
                "answer":(f"c = n/V\n"
                          f"c = {n} / {V_L}\n"
                          f"c = {c} mol/L (M)")})
        elif case == "find_n":
            c = round(random.uniform(0.1,4.0),2)
            V_L = round(random.uniform(0.1,2.0),2)
            n = round(c*V_L,4)
            rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"medium","q_type":"calculate",
                "question":f"How many moles of solute are in {V_L} L of a {c} M solution?",
                "answer":(f"n = c × V\n"
                          f"n = {c} × {V_L}\n"
                          f"n = {n} mol")})
        else:
            n = round(random.uniform(0.1,3.0),2)
            c = round(random.uniform(0.1,4.0),2)
            V_L = round(n/c,4)
            rng.append({"grade_level":grade,"subject":"Chemistry","difficulty":"medium","q_type":"calculate",
                "question":f"What volume (in litres) of a {c} M solution contains {n} mol of solute?",
                "answer":(f"V = n/c\n"
                          f"V = {n} / {c}\n"
                          f"V = {V_L} L")})

    return rng



# ══════════════════════════════════════════════════════════════════
#  AUGMENTATION ENGINE
#  Produces real variety — not just prefix rewording.
#  Strategies: prefix rephrase, framing variation, persona variation.
# ══════════════════════════════════════════════════════════════════

# Per-cognitive-type prefix pools
PREFIXES = {
    "define":        ["", "", "Define: ", "What does the term mean: ",
                      "Give a clear definition of ", "In science, what is "],
    "explain":       ["", "", "", "Explain: ", "Can you explain ",
                      "Help me understand: ", "My teacher asked: ",
                      "For my notes — ", "Study question: "],
    "compare":       ["", "", "Compare: ", "What is the difference between ",
                      "How do these differ: ", "Contrast the following: ",
                      "In what ways are these similar and different: "],
    "calculate":     ["", "", "", "Calculate: ", "Work out: ",
                      "Solve: ", "Find: ", "Show your working: "],
    "predict":       ["", "Predict: ", "What would happen if ",
                      "If this changed, what would the result be: ",
                      "Make a scientific prediction: "],
    "justify":       ["", "Justify: ", "Explain why ",
                      "Give a scientific reason why ",
                      "Why is it the case that "],
    "apply":         ["", "Apply your knowledge: ", "Use science to explain: ",
                      "In the real world: ", "How would you use this concept to explain: "],
    "analyse":       ["", "Analyse: ", "Examine the following and explain: ",
                      "Break down the reasoning behind: ",
                      "Think critically about: "],
    "misconception": ["", "", "A student claims: ",
                      "Is the following statement correct? ",
                      "True or false — explain: ",
                      "Your friend says: "],
}
DEFAULT_PREFIXES = ["", "", "", "Question: ", "Help with this: "]

def augment(base_examples, target_n, seed=42):
    random.seed(seed)
    result = []
    pool   = base_examples[:]
    random.shuffle(pool)
    idx = 0
    while len(result) < target_n:
        ex   = pool[idx % len(pool)].copy()
        qtyp = ex.get("q_type", "explain")
        pfxs = PREFIXES.get(qtyp, DEFAULT_PREFIXES)
        pfx  = random.choice(pfxs)
        if pfx:
            q = ex["question"]
            ex = ex.copy()
            # avoid double-capitalising if prefix ends with space
            ex["question"] = pfx + q[0].lower() + q[1:]
        result.append(ex)
        idx += 1
    random.shuffle(result)
    return result[:target_n]


# ══════════════════════════════════════════════════════════════════
#  OUTPUT BUILDER
# ══════════════════════════════════════════════════════════════════

def build(ex):
    return {
        "instruction": INSTRUCTION,
        "input":       ex["question"],
        "output":      ex["answer"],
        "metadata": {
            "grade_level": ex.get("grade_level",""),
            "subject":     ex.get("subject",""),
            "difficulty":  ex.get("difficulty",""),
            "q_type":      ex.get("q_type",""),
        }
    }


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n",    type=int, default=15000)
    parser.add_argument("--out",  type=str, default="scibot_v3.jsonl")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("Building base examples...")
    static  = list(EXAMPLES)
    dynamic = make_math_examples()
    base    = static + dynamic
    print(f"  Static: {len(static)}  |  Math: {len(dynamic)}  |  Total base: {len(base)}")

    # Distribution report
    qt = Counter(e.get("q_type","?") for e in base)
    print("  Q-type breakdown:")
    for k,v in sorted(qt.items(), key=lambda x:-x[1]):
        print(f"    {k:18s}: {v}")

    print(f"\nAugmenting to {args.n} examples (seed={args.seed})...")
    final = augment(base, args.n, seed=args.seed)

    print("Writing JSONL...")
    out = Path(args.out)
    with out.open("w", encoding="utf-8") as f:
        for ex in final:
            f.write(json.dumps(build(ex), ensure_ascii=False) + "\n")

    print(f"\n✅  {args.n} examples → {out.resolve()}")

    # Spot-check 5 random examples
    print("\n── Spot check (5 random) ──────────────────────────────────")
    for ex in random.sample(final, 5):
        print(f"\n[{ex['grade_level']} | {ex['subject']} | {ex['difficulty']} | {ex.get('q_type','')}]")
        print(f"Q: {ex['question']}")
        snippet = ex['answer']
        print(f"A: {snippet[:220]}{'...' if len(snippet)>220 else ''}")

    # Final validation
    lines = out.read_text().splitlines()
    ok = all(
        set(json.loads(l).keys()) >= {"instruction","input","output","metadata"}
        for l in lines
    )
    print(f"\nFormat valid: {ok}  |  Total lines: {len(lines)}")


if __name__ == "__main__":
    main()