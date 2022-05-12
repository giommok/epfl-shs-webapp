import base64
import io
import json
import string

import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import pandas as pd
import seaborn as sns
from flask import Flask, request, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap

from forms import QuizForm, NameForm, PuzzleForm, ContinueForm

app = Flask(__name__)
Bootstrap(app)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Open puzzles file
with open('puzzles.json', encoding="utf8") as f:
    original_puzzles = json.load(f)
    f.close()

# Open questions file
with open('questions.json', encoding="utf8") as f:
    questions = json.load(f)
    f.close()

# Open bars file
with open('bars.db') as f:
    data = json.load(f)
    f.close()

bars_list = [[d, data[d][0], data[d][1]] for d in data]
bars_df = pd.DataFrame(bars_list, columns=['Bar', 'Level', 'Bar type'])


# Login function
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
        session['old_bars_df'] = None

        # Initialize puzzles
        session['puzzles'] = original_puzzles

        return redirect(url_for('play'))
    return render_template('index.html', name_form=name_form)


# Choose answer function
@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'username' not in session:
        return redirect(url_for('login'))

    quiz_form = QuizForm()
    current_question = session['question_number']
    bars_df = pd.read_json(session['bars_df'], orient='split')
    old_bars_df = pd.read_json(session['old_bars_df'], orient='split') if session['old_bars_df'] is not None else None

    if request.method == 'POST':
        # Retrieve choice
        choice = int(quiz_form.question.data)
        session['last_choice'] = choice

        # Update bars
        session['old_bars_df'] = bars_df.copy(deep=True).to_json(orient='split')
        old_bars_df = bars_df.copy(deep=True)
        rewards = pd.Series(questions[current_question][2][choice], dtype=int)
        bars_df['Level'] = bars_df['Level'].add(rewards)
        session['bars_df'] = bars_df.copy(deep=True).to_json(orient='split')

        # Retrieve feedback for last choice
        message = questions[current_question][4][int(quiz_form.question.data)]

        # Update question number
        session['question_number'] += 1
        current_question += 1

        if message.replace(" ", "") != "":  # If there is a feedback, show the feedback page
            return redirect(url_for('feedback'))

    plot_url = create_plot(old_bars_df, bars_df)
    money = get_money(bars_df)

    game_over = current_question == len(questions)

    if game_over:
        if game_lost(bars_df):
            game_over_message = "You lost the game :( !"
        else:
            game_over_message = "Congrats, you won the game!"
        session.pop('username', None)
        return render_template('game_over.html',
                               game_over_message=game_over_message, plot_url=plot_url, money=money)

    question = questions[current_question][0]
    number_of_choices = questions[current_question][1]
    topic = questions[current_question][3]
    quiz_form.question.choices = [(i, string.ascii_uppercase[i]) for i in range(number_of_choices)]

    return render_template('play.html', quiz_form=quiz_form,
                           question=question, topic=topic,
                           plot_url=plot_url, money=money)


# Show feedback function
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session['question_number'] == 0:
        return redirect(url_for('play'))

    continue_form = ContinueForm()
    previous_question = session['question_number'] - 1
    bars_df = pd.read_json(session['bars_df'], orient='split')
    old_bars_df = pd.read_json(session['old_bars_df'], orient='split')

    if request.method == 'POST':
        return redirect(url_for('play'))

    plot_url = create_plot(old_bars_df, bars_df)
    money = get_money(bars_df)
    question = questions[previous_question][0]
    topic = questions[previous_question][3]
    message = questions[previous_question][4][session['last_choice']]

    return render_template('feedback.html', continue_form=continue_form, message=message,
                           question=question, topic=topic,
                           plot_url=plot_url, money=money)


# Claim puzzle function
@app.route('/claim_puzzle', methods=['GET', 'POST'])
def claim_puzzle():
    if 'username' not in session:
        return redirect(url_for('login'))

    puzzle_form = PuzzleForm()
    puzzles = session['puzzles']
    bars_df = pd.read_json(session['bars_df'], orient='split')
    old_bars_df = pd.read_json(session['old_bars_df'], orient='split') if session['old_bars_df'] is not None else None

    message = ""

    if request.method == 'POST':
        # Retrieve choice
        password = puzzle_form.password.data

        if password in puzzles:
            # Update bars
            session['old_bars_df'] = bars_df.copy(deep=True).to_json(orient='split')
            old_bars_df = bars_df.copy(deep=True)
            # Remove puzzle from session puzzles
            rewards = pd.Series(session['puzzles'].pop(password), dtype=int)
            bars_df['Level'] = bars_df['Level'].add(rewards)
            session['bars_df'] = bars_df.copy(deep=True).to_json(orient='split')

            # Retrieve feedback for last puzzle claim
            message = "Rewards claimed! Well done!"
        else:
            message = "Wrong password. Make sure the password is correct if you successfully completed a puzzle."

    plot_url = create_plot(old_bars_df, bars_df)
    money = get_money(bars_df)

    return render_template('claim_puzzle.html', puzzle_form=puzzle_form, message=message,
                           plot_url=plot_url, money=money)


# Helper function to create plots
def create_plot(old_bars, updated_bars):
    # Prepare plot
    img = io.BytesIO()
    # Excluding budget
    updated_bars = updated_bars[updated_bars['Bar'] != 'Budget']

    if old_bars is not None:
        # Excluding budget
        old_bars = old_bars[old_bars['Bar'] != 'Budget']
        temp_updated = updated_bars.copy()
        temp_old = old_bars.copy()
        temp_updated['Time'] = "Current bars"
        temp_old['Time'] = "Old bars"
        temp = temp_updated.append(temp_old, ignore_index=True)

        unique = temp["Time"].unique()
        pal = dict(zip(unique, sns.color_palette(n_colors=len(unique))))
        pal.update({"Total": "k"})

        plot = sns.catplot(x="Bar", y="Level", hue="Time", hue_order=["Old bars", "Current bars"],  # col="Bar type",
                           data=temp, alpha=0.7, edgecolor="white",
                           kind="bar", ci=None, palette=pal, sharex=False, sharey=False, dodge=True)
        sns.move_legend(plot, "upper center", bbox_to_anchor=(0.5, 1.1), ncol=2, title=None, frameon=False)

    else:
        plot = sns.catplot(x="Bar", y="Level",  # col="Bar type",
                           data=updated_bars, saturation=.5,
                           kind="bar", ci=None, sharex=False, sharey=False)
    plot.axes[0][0].axhline(100, color='red', ls='--')
    # plot.axes[0][1].axhline(100, color='red', ls='--')
    for axes in plot.axes.flat:
        axes.set_xlabel('')
        axes.set_ylabel('')
        axes.set_ylim(top=230)
        _ = axes.set_xticklabels(axes.get_xticklabels(), rotation=30, horizontalalignment='right')
        trans = mtrans.Affine2D().translate(-0, 0)
        for t in axes.get_xticklabels():
            t.set_transform(t.get_transform() + trans)
    # plot.set_titles("{col_name}")
    plt.tight_layout()
    plt.savefig(img, format='png', transparent=True, bbox_inches='tight')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url


# Helper function to get money
def get_money(df):
    return df[df['Bar'] == 'Budget'].Level[0]


# Helper function to check if the game is lost
def game_lost(df):
    sustainability_df = df[df['Bar type'] == 'Sustainability']
    product_quality_df = df[df['Bar'] == 'Product quality']
    budget_df = df[df['Bar'] == 'Budget']

    return (sustainability_df['Level'] > 100).any() or (product_quality_df['Level'] < 100).any() or (
            budget_df['Level'] < 0).any()


# Function to start the webapp
if __name__ == "__main__":
    app.run(debug=True)
