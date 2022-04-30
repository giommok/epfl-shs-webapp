import base64
import io
import json
import string

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from flask import Flask, request, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap

from forms import QuizForm, NameForm

app = Flask(__name__)
Bootstrap(app)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Open questions file
with open('choices.db') as f:
    data = json.load(f)
    f.close()

# Create list of questions (question, number of answers, changes of bars per answer, topic, feedback per answer)
questions = [(d, (data[d][0], data[d][1], data[d][2], data[d][3])) for d in data]

# Open bars file
with open('bars.db') as f:
    data = json.load(f)
    f.close()

bars_list = [[d, data[d]] for d in data]
bars_df = pd.DataFrame(bars_list, columns=['Bar', 'Level'])

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('play'))
    name_form = NameForm()
    if request.method == 'POST':
        team_name = name_form.name.data
        session['username'] = team_name

        # Initialize question number
        session['question_number'] = 0

        # Initialize bars
        session['bars_df'] = bars_df.copy(deep=True).to_json(orient='split')

        return redirect(url_for('play'))
    return render_template('index.html', name_form=name_form)


@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'username' not in session:
        return redirect(url_for('login'))

    quiz_form = QuizForm()
    current_question = session['question_number']
    bars_df = pd.read_json(session['bars_df'], orient='split')

    message = ""

    if request.method == 'POST':
        # Retrieve choice
        choice = int(quiz_form.question.data)

        # Update bars
        rewards = pd.Series(questions[current_question][1][1][choice], dtype=int)
        bars_df['Level'] = bars_df['Level'].add(rewards)
        session['bars_df'] = bars_df.copy(deep=True).to_json(orient='split')

        # Retrieve feedback for last choice
        message = questions[current_question][1][3][int(quiz_form.question.data)]

        # Update question number
        session['question_number'] += 1
        current_question += 1

    # Prepare plot
    img = io.BytesIO()
    pal = sns.color_palette("Set2")
    plot = sns.catplot(x="Bar", y="Level",
                data=bars_df, saturation=.5,
                kind="bar", ci=None, aspect=1.5, palette=pal)
    for axes in plot.axes.flat:
        _ = axes.set_xticklabels(axes.get_xticklabels(), rotation=90)
    plt.xlabel('Bar', fontsize=15)
    plt.ylabel('Level', fontsize=15)
    plt.tight_layout()
    plt.savefig(img, format='png', transparent=True)
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    game_over = current_question == len(questions)
    if game_over:
        session.pop('username', None)
        return render_template('game_over.html', message=message, plot_url=plot_url)

    question = questions[current_question][0]
    number_of_choices = questions[current_question][1][0]
    topic = questions[current_question][1][2]
    quiz_form.question.choices = [(i, string.ascii_uppercase[i]) for i in range(number_of_choices)]

    return render_template('play.html', quiz_form=quiz_form, message=message, question=question, topic=topic,
                           plot_url=plot_url)


if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)
