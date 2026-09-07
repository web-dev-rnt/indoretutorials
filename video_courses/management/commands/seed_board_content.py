from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from base.models import User
from elibrary.models import ELibraryCourse
from testseries.models import Question, Subject, Test, TestSeries
from video_courses.models import Category


def mcq(subject, text, options, answer, explanation, difficulty="medium"):
    return {
        "subject": subject,
        "question_type": "mcq_single",
        "difficulty": difficulty,
        "question_text": text,
        "options": dict(zip("abcd", options)),
        "correct_answer": {"answer": answer},
        "explanation": explanation,
    }


def grade_mcq(subject, text, options, answer, explanation, difficulty="medium"):
    return mcq(subject, text, options, answer, explanation, difficulty)


SUBJECTS = {
    "CBSEMATH": ("CBSE Class 10 Mathematics", "#2563EB", "fas fa-calculator"),
    "CBSESCI": ("CBSE Class 10 Science", "#16A34A", "fas fa-flask"),
    "ICSEMATH": ("ICSE Class 10 Mathematics", "#7C3AED", "fas fa-square-root-alt"),
    "ICSEPHY": ("ICSE Class 10 Physics", "#0284C7", "fas fa-atom"),
    "ICSECHEM": ("ICSE Class 10 Chemistry", "#EA580C", "fas fa-vial"),
    "ICSEBIO": ("ICSE Class 10 Biology", "#059669", "fas fa-dna"),
    "MATH": ("Mathematics", "#2563EB", "fas fa-calculator"),
    "SCI": ("Science and EVS", "#16A34A", "fas fa-leaf"),
    "ENGLISH": ("English", "#EA580C", "fas fa-book-open"),
}


COURSES = [
    {
        "title": "CBSE Class 10 Mathematics Study Library",
        "board": "CBSE",
        "short_description": "Concept notes and guided practice for the complete Class 10 Mathematics syllabus.",
        "description": "An original, curriculum-aligned study collection covering real numbers, algebra, coordinate geometry, trigonometry, circles, mensuration, statistics and probability. Designed for concept revision and exam practice; it is not an official CBSE publication.",
        "tags": "CBSE, Class 10, Mathematics, board exam, revision",
        "difficulty_level": "intermediate",
    },
    {
        "title": "CBSE Class 10 Science Study Library",
        "board": "CBSE",
        "short_description": "Focused Physics, Chemistry and Biology revision for CBSE Class 10 learners.",
        "description": "Original chapter-wise learning support for chemical reactions, acids and bases, carbon compounds, life processes, heredity, light, electricity, magnetism and the environment. Curriculum-aligned, but not an official CBSE publication.",
        "tags": "CBSE, Class 10, Science, Physics, Chemistry, Biology",
        "difficulty_level": "intermediate",
    },
    {
        "title": "ICSE Class 10 Mathematics Study Library",
        "board": "ICSE",
        "short_description": "Structured ICSE Mathematics revision with commercial maths and application practice.",
        "description": "Original revision material covering GST, banking, shares, algebra, matrices, geometry, mensuration, trigonometry, statistics and probability. Built around ICSE learning outcomes; it is not an official CISCE publication.",
        "tags": "ICSE, Class 10, Mathematics, GST, board exam",
        "difficulty_level": "intermediate",
    },
    {
        "title": "ICSE Class 10 Science Study Library",
        "board": "ICSE",
        "short_description": "Integrated Physics, Chemistry and Biology preparation for ICSE Class 10.",
        "description": "An original ICSE-aligned collection for force and energy, light, electricity, periodic properties, bonding, electrolysis, organic chemistry, genetics, plant physiology and human systems. Not an official CISCE publication.",
        "tags": "ICSE, Class 10, Science, Physics, Chemistry, Biology",
        "difficulty_level": "intermediate",
    },
]


CBSE_MATH = [
    mcq("CBSEMATH", "The HCF of 306 and 657 is:", ["3", "9", "18", "27"], "b", "Euclid's algorithm gives 657 = 2×306 + 45, 306 = 6×45 + 36, 45 = 1×36 + 9, and 36 = 4×9; hence HCF = 9.", "easy"),
    mcq("CBSEMATH", "If the zeroes of x² - 7x + 10 are α and β, then αβ equals:", ["-10", "-7", "7", "10"], "d", "For ax²+bx+c, the product of zeroes is c/a. Here it is 10/1 = 10.", "easy"),
    mcq("CBSEMATH", "For what value of k does 2x + 3y = 7 and 4x + 6y = k have infinitely many solutions?", ["7", "10", "12", "14"], "d", "The second equation must be exactly twice the first, so k = 2×7 = 14."),
    mcq("CBSEMATH", "The 20th term of the AP 5, 9, 13, ... is:", ["77", "79", "81", "85"], "c", "a20 = a + 19d = 5 + 19×4 = 81."),
    mcq("CBSEMATH", "The distance between A(2, -1) and B(5, 3) is:", ["4", "5", "6", "7"], "b", "Distance = √[(5-2)² + (3+1)²] = √(9+16) = 5."),
    mcq("CBSEMATH", "If tan θ = 3/4 for an acute angle θ, then sin θ is:", ["3/5", "4/5", "3/4", "5/4"], "a", "A 3-4-5 right triangle has opposite 3 and hypotenuse 5, so sin θ = 3/5."),
    mcq("CBSEMATH", "From an external point P, PA and PB are tangents to a circle. If PA = 8 cm, PB is:", ["4 cm", "8 cm", "16 cm", "Cannot be found"], "b", "Tangents drawn from the same external point to a circle are equal."),
    mcq("CBSEMATH", "A die is thrown once. The probability of obtaining a prime number is:", ["1/3", "1/2", "2/3", "5/6"], "b", "The prime outcomes are 2, 3 and 5: 3 favourable outcomes out of 6, giving 1/2."),
    mcq("CBSEMATH", "The discriminant of 3x² - 5x + 2 = 0 is:", ["1", "7", "25", "49"], "a", "D = b² - 4ac = 25 - 24 = 1."),
    mcq("CBSEMATH", "The curved surface area of a cylinder of radius 7 cm and height 10 cm (use π = 22/7) is:", ["220 cm²", "308 cm²", "440 cm²", "880 cm²"], "c", "Curved surface area = 2πrh = 2×22/7×7×10 = 440 cm²."),
]


CBSE_SCIENCE = [
    mcq("CBSESCI", "Which equation is correctly balanced?", ["H₂ + O₂ → H₂O", "2H₂ + O₂ → 2H₂O", "H₂ + 2O₂ → 2H₂O", "2H₂ + 2O₂ → H₂O"], "b", "Two molecules of hydrogen react with one molecule of oxygen to form two molecules of water.", "easy"),
    mcq("CBSESCI", "A solution with pH 2 is best described as:", ["Strongly acidic", "Weakly acidic", "Neutral", "Basic"], "a", "A pH well below 7 indicates an acidic solution; pH 2 is strongly acidic.", "easy"),
    mcq("CBSESCI", "Which metal is commonly extracted by electrolytic reduction because it is highly reactive?", ["Copper", "Iron", "Sodium", "Mercury"], "c", "Sodium is above carbon in the reactivity series and is extracted by electrolysis of its molten compound."),
    mcq("CBSESCI", "Successive members of a homologous series differ by:", ["CH", "CH₂", "CH₃", "C₂H₂"], "b", "Adjacent homologues differ by one –CH₂– unit, corresponding to 14 u."),
    mcq("CBSESCI", "Most absorption of digested food in humans occurs in the:", ["Stomach", "Small intestine", "Large intestine", "Oesophagus"], "b", "The small intestine has villi that greatly increase surface area for absorption."),
    mcq("CBSESCI", "In a monohybrid cross Tt × Tt, the probability of a dwarf offspring (tt) is:", ["0", "1/4", "1/2", "3/4"], "b", "The genotypes are TT, Tt, Tt and tt, so one of four offspring is expected to be dwarf."),
    mcq("CBSESCI", "An object is placed beyond 2F of a convex lens. The image formed is:", ["Virtual, erect and enlarged", "Real, inverted and diminished", "Real, erect and same size", "Virtual and diminished"], "b", "For an object beyond 2F, a convex lens forms a real, inverted, diminished image between F and 2F."),
    mcq("CBSESCI", "Two resistors of 6 Ω each are connected in parallel. Their equivalent resistance is:", ["3 Ω", "6 Ω", "12 Ω", "36 Ω"], "a", "For equal resistors in parallel, equivalent resistance is half of either resistor: 3 Ω."),
    mcq("CBSESCI", "The direction of magnetic field around a straight current-carrying wire is found using the:", ["Fleming left-hand rule", "Right-hand thumb rule", "Snell's law", "Lenz's law"], "b", "The right-hand thumb rule gives the circular direction of magnetic field lines around the conductor."),
    mcq("CBSESCI", "Why are food chains usually limited to only a few trophic levels?", ["Energy increases at each level", "Only a small fraction of energy passes to the next level", "Decomposers stop energy flow", "Producers consume all oxygen"], "b", "Most energy is used or lost as heat at each transfer, leaving too little to support many higher levels."),
]


ICSE_MATH = [
    mcq("ICSEMATH", "An article marked ₹2,000 is sold at 10% discount. GST at 18% is charged on the discounted price. The amount paid is:", ["₹1,800", "₹2,000", "₹2,124", "₹2,160"], "c", "Discounted price = ₹1,800. GST = 18% of ₹1,800 = ₹324, so the bill is ₹2,124."),
    mcq("ICSEMATH", "The annual dividend on 50 shares of face value ₹100 at 8% is:", ["₹40", "₹400", "₹500", "₹4,000"], "b", "Dividend per share is 8% of ₹100 = ₹8; for 50 shares it is ₹400."),
    mcq("ICSEMATH", "If A = [[1, 2], [3, 4]] and B = [[2, 0], [1, 5]], the top-right entry of A + B is:", ["0", "2", "5", "7"], "b", "Matrices are added entry-wise; the top-right entry is 2 + 0 = 2."),
    mcq("ICSEMATH", "The roots of x² - 9x + 20 = 0 are:", ["4 and 5", "-4 and -5", "2 and 10", "1 and 20"], "a", "x² - 9x + 20 factors as (x-4)(x-5)."),
    mcq("ICSEMATH", "The remainder when 2x³ - 3x² + 4x - 5 is divided by x - 2 is:", ["-1", "3", "5", "7"], "d", "By the remainder theorem, substitute x=2: 16 - 12 + 8 - 5 = 7."),
    mcq("ICSEMATH", "The reflection of the point (3, -2) in the y-axis is:", ["(-3, -2)", "(3, 2)", "(-3, 2)", "(2, -3)"], "a", "Reflection in the y-axis changes the sign of x but leaves y unchanged."),
    mcq("ICSEMATH", "If a ladder 10 m long reaches a window 8 m above the ground, its foot is how far from the wall?", ["2 m", "4 m", "6 m", "8 m"], "c", "By Pythagoras, distance = √(10²-8²) = √36 = 6 m."),
    mcq("ICSEMATH", "The mean of 6, 8, 10, 12 and 14 is:", ["8", "9", "10", "11"], "c", "Their sum is 50 and 50÷5 = 10."),
    mcq("ICSEMATH", "A bag contains 5 red, 3 blue and 2 green balls. The probability of drawing a blue ball is:", ["1/5", "3/10", "1/3", "1/2"], "b", "There are 10 balls in total and 3 are blue, so the probability is 3/10."),
    mcq("ICSEMATH", "A cone and a cylinder have the same base radius and height. The ratio of their volumes is:", ["1:2", "1:3", "2:3", "3:1"], "b", "Cone volume is (1/3)πr²h while cylinder volume is πr²h, giving 1:3."),
]


ICSE_SCIENCE = [
    mcq("ICSEPHY", "A machine has mechanical advantage 4 and velocity ratio 5. Its efficiency is:", ["20%", "40%", "80%", "125%"], "c", "Efficiency = (MA/VR)×100 = (4/5)×100 = 80%."),
    mcq("ICSEPHY", "A 100 W appliance operates for 2 hours. The electrical energy consumed is:", ["0.02 kWh", "0.2 kWh", "2 kWh", "200 kWh"], "b", "100 W = 0.1 kW; energy = 0.1×2 = 0.2 kWh."),
    mcq("ICSEPHY", "When light travels from air into glass, it normally:", ["Speeds up and bends away from normal", "Slows down and bends towards normal", "Slows down and bends away from normal", "Keeps the same speed"], "b", "Glass is optically denser than air, so light slows and bends towards the normal."),
    mcq("ICSEPHY", "The specific heat capacity of water is 4200 J kg⁻¹ K⁻¹. Heat needed to raise 0.5 kg water by 2 K is:", ["1,050 J", "2,100 J", "4,200 J", "8,400 J"], "c", "Q = mcΔT = 0.5×4200×2 = 4200 J."),
    mcq("ICSECHEM", "Across a period from left to right, atomic size generally:", ["Increases", "Decreases", "Remains constant", "First decreases then always doubles"], "b", "Increasing nuclear charge pulls electrons closer while they are added to the same principal shell."),
    mcq("ICSECHEM", "The gas evolved at the cathode during electrolysis of acidified water is:", ["Oxygen", "Hydrogen", "Chlorine", "Nitrogen"], "b", "H⁺ ions gain electrons at the cathode and form hydrogen gas."),
    mcq("ICSECHEM", "Which compound contains a covalent bond?", ["NaCl", "MgO", "HCl", "KBr"], "c", "Hydrogen and chlorine share a pair of electrons to form a polar covalent H–Cl bond."),
    mcq("ICSEBIO", "Crossing over that produces genetic variation occurs during:", ["Prophase I of meiosis", "Prophase of mitosis", "Telophase II", "Cytokinesis"], "a", "Homologous chromosomes pair and exchange segments during prophase I of meiosis."),
    mcq("ICSEBIO", "Water rises through xylem mainly because of:", ["Root pressure alone", "Transpiration pull", "Active transport in leaves", "Diffusion through phloem"], "b", "Evaporation from leaves creates a tension that pulls the continuous water column upward through xylem."),
    mcq("ICSEBIO", "Which hormone lowers blood glucose concentration?", ["Adrenaline", "Thyroxine", "Insulin", "Glucagon"], "c", "Insulin promotes uptake and storage of glucose, thereby lowering its concentration in blood."),
]


# Original foundation questions based on learning outcomes common to the two
# boards. Class 10 retains separate subject papers below.
GRADE_PAPERS = {
    1: [
        grade_mcq("MATH", "What number comes after 19?", ["18", "20", "21", "29"], "b", "Counting forward one number from 19 gives 20.", "easy"),
        grade_mcq("MATH", "What is 7 + 5?", ["10", "11", "12", "13"], "c", "Seven objects joined with five objects make twelve.", "easy"),
        grade_mcq("MATH", "Which shape has three sides?", ["Circle", "Triangle", "Square", "Rectangle"], "b", "A triangle is a closed shape with three sides.", "easy"),
        grade_mcq("MATH", "Which is the greatest number?", ["6", "9", "4", "7"], "b", "Nine is greater than 7, 6 and 4.", "easy"),
        grade_mcq("SCI", "Which body part helps us to see?", ["Ears", "Eyes", "Nose", "Tongue"], "b", "We use our eyes to see.", "easy"),
        grade_mcq("SCI", "Which of these is a living thing?", ["Stone", "Chair", "Tree", "Ball"], "c", "A tree grows, needs water and is living.", "easy"),
        grade_mcq("SCI", "Which part of a plant is usually under the soil?", ["Flower", "Leaf", "Fruit", "Root"], "d", "Roots usually grow under the soil and absorb water.", "easy"),
        grade_mcq("ENGLISH", "Choose the correct plural of 'cat'.", ["cats", "cates", "cat", "cat's"], "a", "We usually add s to make the plural: cat becomes cats.", "easy"),
        grade_mcq("ENGLISH", "Which word names a colour?", ["Run", "Blue", "Sing", "Jump"], "b", "Blue is the name of a colour.", "easy"),
        grade_mcq("ENGLISH", "Complete the sentence: I ___ a student.", ["am", "is", "are", "be"], "a", "The verb used with I in the present tense is am.", "easy"),
    ],
    2: [
        grade_mcq("MATH", "What is 46 + 23?", ["59", "67", "69", "79"], "c", "Add ones: 6+3=9; add tens: 4+2=6, giving 69.", "easy"),
        grade_mcq("MATH", "What is 80 - 35?", ["35", "45", "55", "65"], "b", "80 minus 30 is 50, and minus 5 more is 45.", "easy"),
        grade_mcq("MATH", "How many minutes are in one hour?", ["30", "45", "60", "100"], "c", "One hour contains 60 minutes.", "easy"),
        grade_mcq("MATH", "Two ₹10 coins and one ₹5 coin make:", ["₹15", "₹20", "₹25", "₹30"], "c", "10 + 10 + 5 = ₹25.", "easy"),
        grade_mcq("SCI", "Which animal gives us wool?", ["Sheep", "Hen", "Duck", "Fish"], "a", "Wool is obtained mainly from the fleece of sheep.", "easy"),
        grade_mcq("SCI", "Water changes into ice when it:", ["Heats", "Freezes", "Boils", "Evaporates"], "b", "On freezing, liquid water becomes solid ice.", "easy"),
        grade_mcq("SCI", "Which meal is normally eaten in the morning?", ["Dinner", "Lunch", "Breakfast", "Supper"], "c", "The first meal of the day is breakfast.", "easy"),
        grade_mcq("ENGLISH", "Choose the opposite of 'hot'.", ["Warm", "Cold", "Bright", "Dry"], "b", "Cold is the opposite of hot.", "easy"),
        grade_mcq("ENGLISH", "Which sentence is correctly punctuated?", ["where are you", "Where are you?", "where are you.", "Where are you!"], "b", "A question begins with a capital letter and ends with a question mark.", "easy"),
        grade_mcq("ENGLISH", "Choose the describing word: 'The red ball bounced.'", ["The", "red", "ball", "bounced"], "b", "Red describes the colour of the ball, so it is an adjective.", "easy"),
    ],
    3: [
        grade_mcq("MATH", "What is 8 × 7?", ["48", "54", "56", "64"], "c", "Eight groups of seven make 56.", "easy"),
        grade_mcq("MATH", "What is 72 ÷ 9?", ["6", "7", "8", "9"], "c", "Because 9×8=72, 72÷9=8.", "easy"),
        grade_mcq("MATH", "Which fraction represents one part out of four equal parts?", ["1/2", "1/3", "1/4", "4/1"], "c", "One selected part from four equal parts is one-fourth.", "easy"),
        grade_mcq("MATH", "A rectangle is 5 cm long and 3 cm wide. Its perimeter is:", ["8 cm", "15 cm", "16 cm", "30 cm"], "c", "Perimeter = 2×(5+3) = 16 cm."),
        grade_mcq("SCI", "Which part of a plant makes most of its food?", ["Root", "Stem", "Leaf", "Flower"], "c", "Leaves contain chlorophyll and make food by photosynthesis."),
        grade_mcq("SCI", "Which of these is a source of clean drinking water after treatment?", ["Sewage", "Purified tap water", "Sea water", "Muddy puddle"], "b", "Properly treated tap water is made safe for drinking."),
        grade_mcq("SCI", "Earth takes about how long to rotate once?", ["12 hours", "24 hours", "7 days", "30 days"], "b", "One complete rotation of Earth takes about 24 hours."),
        grade_mcq("ENGLISH", "Identify the noun: 'Riya reads quietly.'", ["Riya", "reads", "quietly", "none"], "a", "Riya is the name of a person and is a proper noun."),
        grade_mcq("ENGLISH", "Choose the correct past tense of 'go'.", ["goed", "goes", "went", "going"], "c", "Went is the irregular past-tense form of go."),
        grade_mcq("ENGLISH", "Choose the correct article: ___ umbrella.", ["A", "An", "Thee", "No article"], "b", "Umbrella begins with a vowel sound, so we use an."),
    ],
    4: [
        grade_mcq("MATH", "What is the place value of 7 in 47,325?", ["7", "70", "700", "7,000"], "d", "The digit 7 is in the thousands place, so its value is 7,000."),
        grade_mcq("MATH", "Which number is a factor of 24?", ["5", "6", "7", "9"], "b", "24÷6=4 with no remainder, so 6 is a factor."),
        grade_mcq("MATH", "An angle smaller than 90° is called:", ["Acute", "Right", "Obtuse", "Straight"], "a", "An acute angle measures less than 90°."),
        grade_mcq("MATH", "The area of a square with side 6 cm is:", ["12 cm²", "24 cm²", "36 cm²", "48 cm²"], "c", "Area of a square = side×side = 6×6 = 36 cm²."),
        grade_mcq("SCI", "Which state of matter has a fixed volume but no fixed shape?", ["Solid", "Liquid", "Gas", "All three"], "b", "A liquid keeps its volume but takes the shape of its container."),
        grade_mcq("SCI", "In a simple food chain, green plants are:", ["Consumers", "Producers", "Decomposers", "Predators"], "b", "Green plants produce their own food using sunlight."),
        grade_mcq("SCI", "Which organ pumps blood around the body?", ["Lungs", "Brain", "Heart", "Stomach"], "c", "The heart contracts to pump blood through blood vessels."),
        grade_mcq("ENGLISH", "Choose the correct pronoun: Aman and I are friends. ___ play together.", ["He", "She", "We", "They"], "c", "We refers to the speaker together with another person."),
        grade_mcq("ENGLISH", "Which word is an adverb in 'The tortoise walked slowly'?", ["tortoise", "walked", "slowly", "the"], "c", "Slowly tells us how the tortoise walked."),
        grade_mcq("ENGLISH", "Choose the correctly spelled word.", ["becaus", "because", "beacause", "becose"], "b", "The correct spelling is because."),
    ],
    5: [
        grade_mcq("MATH", "What is 3/4 + 1/8?", ["4/12", "4/8", "7/8", "1"], "c", "3/4 is 6/8; 6/8+1/8=7/8."),
        grade_mcq("MATH", "Which decimal is equal to 7/10?", ["0.07", "0.7", "7.0", "70.0"], "b", "Seven tenths is written as 0.7."),
        grade_mcq("MATH", "The volume of a cuboid 4 cm × 3 cm × 2 cm is:", ["9 cm³", "12 cm³", "18 cm³", "24 cm³"], "d", "Volume = length×breadth×height = 4×3×2 = 24 cm³."),
        grade_mcq("MATH", "25% of 200 is:", ["25", "40", "50", "75"], "c", "25% is one-fourth, and one-fourth of 200 is 50."),
        grade_mcq("SCI", "Which planet is known for its prominent rings?", ["Mars", "Earth", "Saturn", "Mercury"], "c", "Saturn has the Solar System's most prominent ring system."),
        grade_mcq("SCI", "The process by which plants lose water vapour through leaves is:", ["Respiration", "Transpiration", "Germination", "Pollination"], "b", "Loss of water vapour from aerial plant parts is transpiration."),
        grade_mcq("SCI", "Which nutrient mainly helps build and repair body tissues?", ["Proteins", "Carbohydrates", "Water", "Roughage"], "a", "Proteins supply materials needed for growth and tissue repair."),
        grade_mcq("ENGLISH", "Choose the conjunction: 'I stayed home because it rained.'", ["stayed", "home", "because", "rained"], "c", "Because joins the reason to the main clause."),
        grade_mcq("ENGLISH", "Which sentence is in the future tense?", ["I walk daily.", "I walked yesterday.", "I will walk tomorrow.", "I am walking now."], "c", "Will walk expresses an action expected in the future."),
        grade_mcq("ENGLISH", "Choose the synonym of 'brave'.", ["cowardly", "courageous", "silent", "careless"], "b", "Courageous has the same meaning as brave."),
    ],
    6: [
        grade_mcq("MATH", "What is (-8) + 13?", ["-21", "-5", "5", "21"], "c", "Moving 13 units right from -8 reaches 5."),
        grade_mcq("MATH", "Simplify the ratio 18:24.", ["2:3", "3:4", "4:3", "9:12 only"], "b", "Divide both terms by their HCF, 6, to get 3:4."),
        grade_mcq("MATH", "If x + 7 = 19, x equals:", ["10", "11", "12", "26"], "c", "Subtract 7 from both sides: x=19-7=12."),
        grade_mcq("MATH", "The mean of 4, 6, 8 and 10 is:", ["6", "7", "8", "9"], "b", "The sum is 28; dividing by 4 gives 7."),
        grade_mcq("SCI", "Which method separates an insoluble solid from a liquid?", ["Filtration", "Evaporation only", "Churning", "Magnetism"], "a", "A filter traps insoluble solid particles while the liquid passes through."),
        grade_mcq("SCI", "The basic structural and functional unit of life is the:", ["Organ", "Cell", "Tissue", "Nucleus"], "b", "All organisms are composed of cells, the basic units of life."),
        grade_mcq("SCI", "Speed is calculated as:", ["time ÷ distance", "distance ÷ time", "distance × time", "mass ÷ volume"], "b", "Average speed is distance travelled divided by time taken."),
        grade_mcq("ENGLISH", "Identify the subject in 'The little puppy chased the ball.'", ["chased", "the ball", "The little puppy", "little"], "c", "The little puppy is who performs the action."),
        grade_mcq("ENGLISH", "Choose the correct comparative form of 'good'.", ["gooder", "more good", "better", "best"], "c", "Good has the irregular comparative form better."),
        grade_mcq("ENGLISH", "Which sentence uses an apostrophe correctly?", ["The dogs tail wagged.", "The dog's tail wagged.", "The dogs' tail wagged for one dog.", "The dog,s tail wagged."], "b", "For one dog, the possessive form is dog's."),
    ],
    7: [
        grade_mcq("MATH", "What is (-3/5) × (10/9)?", ["-2/3", "-1/3", "2/3", "3/2"], "a", "Cancel common factors: (-3×10)/(5×9) = -30/45 = -2/3."),
        grade_mcq("MATH", "A shirt costs ₹800 and is discounted by 15%. Its sale price is:", ["₹120", "₹680", "₹720", "₹785"], "b", "Discount is ₹120; ₹800-₹120=₹680."),
        grade_mcq("MATH", "Simple interest on ₹1,000 at 5% per year for 2 years is:", ["₹50", "₹100", "₹150", "₹200"], "b", "SI = PRT/100 = 1000×5×2/100 = ₹100."),
        grade_mcq("MATH", "If 3x - 4 = 17, x is:", ["5", "6", "7", "9"], "c", "3x=21, so x=7."),
        grade_mcq("SCI", "Heat transfer through direct contact is called:", ["Radiation", "Convection", "Conduction", "Reflection"], "c", "Conduction transfers heat between neighbouring particles without bulk movement."),
        grade_mcq("SCI", "Plants use carbon dioxide and water to make food during:", ["Respiration", "Photosynthesis", "Transpiration", "Digestion"], "b", "Photosynthesis uses light energy to form glucose from carbon dioxide and water."),
        grade_mcq("SCI", "Blue litmus paper turns red in a/an:", ["Acid", "Base", "Neutral salt only", "Metal"], "a", "Acids turn blue litmus red."),
        grade_mcq("ENGLISH", "Identify the figure of speech: 'The wind whispered through the trees.'", ["Simile", "Personification", "Hyperbole", "Alliteration only"], "b", "The wind is given the human action of whispering."),
        grade_mcq("ENGLISH", "Choose the passive form of 'The chef cooked the meal.'", ["The meal cooked the chef.", "The meal was cooked by the chef.", "The chef was cooked by the meal.", "The meal is cooking."], "b", "The object becomes the subject and the past passive uses was cooked."),
        grade_mcq("ENGLISH", "Which word is a preposition in 'The book is under the table'?", ["book", "is", "under", "table"], "c", "Under shows the relationship between the book and the table."),
    ],
    8: [
        grade_mcq("MATH", "Simplify 2³ × 2⁴.", ["2⁷", "4⁷", "2¹²", "4¹²"], "a", "When multiplying powers with the same base, add exponents: 2^(3+4)=2⁷."),
        grade_mcq("MATH", "Solve 5x - 9 = 26.", ["5", "6", "7", "8"], "c", "5x=35, hence x=7."),
        grade_mcq("MATH", "A trader buys an item for ₹500 and sells it for ₹575. The profit percentage is:", ["10%", "12%", "15%", "75%"], "c", "Profit is ₹75; (75/500)×100=15%."),
        grade_mcq("MATH", "The square root of 1764 is:", ["38", "40", "42", "44"], "c", "42×42=1764."),
        grade_mcq("SCI", "The control centre of a cell is the:", ["Cell wall", "Nucleus", "Vacuole", "Cytoplasm"], "b", "The nucleus contains genetic material and regulates cell activities."),
        grade_mcq("SCI", "Pressure equals:", ["force × area", "force ÷ area", "area ÷ force", "mass × acceleration × area"], "b", "Pressure is force acting per unit area."),
        grade_mcq("SCI", "Which gas is necessary for combustion?", ["Nitrogen", "Oxygen", "Carbon dioxide", "Hydrogen"], "b", "Oxygen supports the burning of most fuels."),
        grade_mcq("ENGLISH", "Choose the sentence with correct subject-verb agreement.", ["Each student have a book.", "Each student has a book.", "Each students has a book.", "Each student having a book."], "b", "The singular subject each student takes the singular verb has."),
        grade_mcq("ENGLISH", "The clause 'because she was tired' is a/an:", ["Independent clause", "Subordinate clause", "Main clause", "Noun phrase only"], "b", "It begins with a subordinating conjunction and cannot stand alone."),
        grade_mcq("ENGLISH", "Choose the antonym of 'scarce'.", ["rare", "limited", "abundant", "small"], "c", "Abundant means plentiful, the opposite of scarce."),
    ],
    9: [
        grade_mcq("MATH", "Which of the following is irrational?", ["0.25", "√2", "7/9", "-3"], "b", "√2 cannot be expressed as a ratio of integers, so it is irrational."),
        grade_mcq("MATH", "If p(x)=x²-5x+6, then p(2) equals:", ["-2", "0", "2", "4"], "b", "p(2)=4-10+6=0."),
        grade_mcq("MATH", "The point (-4, 3) lies in quadrant:", ["I", "II", "III", "IV"], "b", "A negative x-coordinate and positive y-coordinate place the point in quadrant II."),
        grade_mcq("MATH", "Two supplementary angles are in the ratio 2:3. The smaller angle is:", ["60°", "72°", "90°", "108°"], "b", "Five parts equal 180°, so each part is 36° and the smaller angle is 72°."),
        grade_mcq("SCI", "During a change of state at constant pressure, temperature remains constant because heat is used as:", ["Kinetic energy only", "Latent heat", "Electrical energy", "Nuclear energy"], "b", "Latent heat changes intermolecular separation without raising temperature."),
        grade_mcq("SCI", "The atomic number of an element equals its number of:", ["Neutrons only", "Protons", "Nucleons", "Shells"], "b", "Atomic number is defined as the number of protons in the nucleus."),
        grade_mcq("SCI", "An object moving at constant speed in a circle has:", ["Zero acceleration", "Constant velocity", "Changing velocity", "No force acting"], "c", "Its direction changes continuously, so velocity changes even when speed is constant."),
        grade_mcq("ENGLISH", "Choose the correctly reported form: Ravi said, 'I am busy.'", ["Ravi said that I am busy.", "Ravi said that he was busy.", "Ravi says he is busy yesterday.", "Ravi said that he is busy always."], "b", "The pronoun and tense normally shift in reported speech: I am becomes he was."),
        grade_mcq("ENGLISH", "Identify the modal expressing obligation: 'You must wear a helmet.'", ["you", "must", "wear", "helmet"], "b", "Must is a modal verb showing strong obligation."),
        grade_mcq("ENGLISH", "Choose the correctly spelled word.", ["seperate", "separate", "separete", "seperrate"], "b", "The correct spelling is separate."),
    ],
}


PAPERS = [
    ("cbse-class-10-practice", "CBSE Class 10 Board Practice", "CBSE", "CBSE Mathematics Competency Practice Paper 1", "cbse-mathematics-practice-1", "CBSE_MATH", CBSE_MATH),
    ("cbse-class-10-practice", "CBSE Class 10 Board Practice", "CBSE", "CBSE Science Competency Practice Paper 1", "cbse-science-practice-1", "CBSE_SCI", CBSE_SCIENCE),
    ("icse-class-10-practice", "ICSE Class 10 Board Practice", "ICSE", "ICSE Mathematics Competency Practice Paper 1", "icse-mathematics-practice-1", "ICSE_MATH", ICSE_MATH),
    ("icse-class-10-practice", "ICSE Class 10 Board Practice", "ICSE", "ICSE Science Competency Practice Paper 1", "icse-science-practice-1", "ICSE_PHY", ICSE_SCIENCE),
]


class Command(BaseCommand):
    help = "Add original CBSE and ICSE Class 10 e-library courses and practice papers."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for board in ("CBSE", "ICSE"):
            categories[board], _ = Category.objects.update_or_create(
                name=board,
                defaults={"description": f"{board} curriculum-aligned learning resources"},
            )

        creator = User.objects.filter(is_superuser=True).first() or User.objects.first()
        for data in COURSES:
            board = data["board"]
            course_defaults = {key: value for key, value in data.items() if key != "board"}
            ELibraryCourse.objects.update_or_create(
                title=data["title"],
                defaults={
                    **course_defaults,
                    "category": categories[board],
                    "instructor": "EduTrellis Academic Team",
                    "is_free": True,
                    "price": Decimal("0.00"),
                    "discount_price": None,
                    "is_featured": True,
                    "is_active": True,
                    "created_by": creator,
                },
            )

        subjects = {}
        for code, (name, color, icon) in SUBJECTS.items():
            subjects[code], _ = Subject.objects.update_or_create(
                code=code,
                defaults={"name": name, "color": color, "icon": icon, "is_active": True},
            )

        series_cache = {}
        for series_slug, series_title, board, test_title, test_slug, _, questions in PAPERS:
            if series_slug not in series_cache:
                series_cache[series_slug], _ = TestSeries.objects.update_or_create(
                    slug=series_slug,
                    defaults={
                        "title": series_title,
                        "category": categories[board],
                        "description": "Original curriculum-aligned competency practice. These are EduTrellis practice papers, not official board papers.",
                        "is_free": True,
                        "price": Decimal("0.00"),
                        "difficulty": "medium",
                        "estimated_duration": "30 minutes per practice paper",
                        "has_negative_marking": False,
                        "negative_marks": Decimal("0.00"),
                        "pass_percentage": 40,
                        "is_active": True,
                        "is_featured": True,
                    },
                )

            test, _ = Test.objects.update_or_create(
                test_series=series_cache[series_slug],
                slug=test_slug,
                defaults={
                    "title": test_title,
                    "description": "Ten original, syllabus-aligned questions with worked explanations. This is a compact practice set rather than an official specimen paper.",
                    "duration_minutes": 30,
                    "shuffle_questions": False,
                    "show_result_immediately": True,
                    "allow_review": True,
                    "max_attempts": 3,
                    "is_active": True,
                },
            )

            for order, data in enumerate(questions, start=1):
                subject = subjects[data["subject"]]
                question_defaults = {key: value for key, value in data.items() if key != "subject"}
                Question.objects.update_or_create(
                    test=test,
                    order=order,
                    defaults={
                        **question_defaults,
                        "subject": subject,
                        "marks": 2,
                        "negative_marks": Decimal("0.00"),
                    },
                )
            test.questions.filter(order__gt=len(questions)).delete()
            test.update_stats()

        for board in ("CBSE", "ICSE"):
            for grade, questions in GRADE_PAPERS.items():
                series_slug = f"{board.lower()}-class-{grade}-practice"
                series, _ = TestSeries.objects.update_or_create(
                    slug=series_slug,
                    defaults={
                        "title": f"{board} Class {grade} Practice Tests",
                        "category": categories[board],
                        "description": (
                            f"Original {board} Class {grade} foundation practice in Mathematics, "
                            "English and Science/EVS. This is EduTrellis learning material, not an "
                            "official board paper."
                        ),
                        "is_free": True,
                        "price": Decimal("0.00"),
                        "difficulty": "easy" if grade <= 5 else "medium",
                        "estimated_duration": "25 minutes per practice paper",
                        "has_negative_marking": False,
                        "negative_marks": Decimal("0.00"),
                        "pass_percentage": 40,
                        "is_active": True,
                        "is_featured": grade in (1, 5, 9),
                    },
                )
                series_cache[series_slug] = series

                test, _ = Test.objects.update_or_create(
                    test_series=series,
                    slug=f"{board.lower()}-class-{grade}-foundation-paper-1",
                    defaults={
                        "title": f"{board} Class {grade} Foundation Practice Paper 1",
                        "description": (
                            "Ten age-appropriate questions across Mathematics, English and "
                            "Science/EVS, with answers and explanations."
                        ),
                        "duration_minutes": 25,
                        "shuffle_questions": False,
                        "show_result_immediately": True,
                        "allow_review": True,
                        "max_attempts": 3,
                        "is_active": True,
                    },
                )

                for order, data in enumerate(questions, start=1):
                    subject = subjects[data["subject"]]
                    question_defaults = {
                        key: value for key, value in data.items() if key != "subject"
                    }
                    Question.objects.update_or_create(
                        test=test,
                        order=order,
                        defaults={
                            **question_defaults,
                            "subject": subject,
                            "marks": 2,
                            "negative_marks": Decimal("0.00"),
                        },
                    )
                test.questions.filter(order__gt=len(questions)).delete()
                test.update_stats()

        for series in series_cache.values():
            series.update_stats()

        self.stdout.write(self.style.SUCCESS(
            "Board content ready: Classes 1-10 for CBSE and ICSE, 22 papers and 220 questions."
        ))
