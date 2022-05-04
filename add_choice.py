import json

# Use this code to generate the correct text for python
# For texts, use this template:

TEXT = """<p>Nowadays, when a phone is broken it is completely replaced by the company. This way, you give the user a new fully functioning phone, so the company does not need to repair the phone and the user will cover the expensive cost of replacing the broken phone. Your company takes the smartphones and gives you another working device.</p>

    <p>You have thought of possible ways to manage this issue:
    <ol>
      <li>Design the device in a way so that the user can open and repair it by themselves.</li>
      <li>The client can send their old phones for free, to be recycled or to have a second life.</li>
      <li>The client can send the broken phone to the company and get a new one for free. The company does not have to recycle the broken phone and just throw it away in the landfill.</li>
      <li>Ignore the issue.</li>
    </ol>
    </p>

    <p>What do you do?</p>

    <ol type = 'A'>
             <li>1</li>
             <li>2</li>
             <li>3</li>
             <li>1 and 2</li>
             <li>1 and 3</li>
             <li>4</li>
    </ol>"""

with open('questions.json', encoding="utf8") as f:
    old_questions = json.load(f)
    f.close()

with open('questions.json', 'w', encoding='utf-8') as f:

    question = """<p>A local representative just started suing your company because the smartphone produced contains a high amount of toxic metals (Nickel for casing and electronics, Antimony for the chip…). Those need to be recycled in high performing facilities and in developing countries they get dispersed in nature where they intoxicate animals and can cause cancer for those exposed to it.</p>
    <p>You have various options:
    <ol>
      <li>Hire good layers to win the trial and keep doing so.</li>
      <li>Invest in R&D to more efficient ways to recycle those metals.</li>
      <li>Recognize your errors and try to help building more performant facilities in those developing countries.</li>
    </ol>
    </p>

    <p>What do you do?</p>

    <ol type = 'A'>
             <li>1</li>
             <li>2</li>
             <li>3</li>
             <li>2 and 3</li>
    </ol>"""

    number_of_answers = 4
    rewards = [[20, 10, 50, 90, 13] for _ in range(number_of_answers)]
    topic = "Pollution"
    feedbacks = ["FB" for _ in range(number_of_answers)]
    new_choice = [question, number_of_answers, rewards, topic, feedbacks]

    json.dump(old_questions + [new_choice], f, ensure_ascii=False, indent=4)
