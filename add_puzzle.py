import json

# In puzzles.json, puzzles are saved as a dictionary with passwords (to claim the puzzle)
# as keys and rewards as list of rewards (where each position is linked to a specific bar,
# in the same order as in the file bars.db)

try:
    with open('puzzles.json', encoding="utf8") as f:
        old_puzzles = json.load(f)
        f.close()
except:
    old_puzzles = dict()

with open('puzzles.json', 'w', encoding='utf-8') as f:
    # Password that players have to submit to claim the puzzle
    # IMPORTANT: all puzzles must have different passwords!
    puzzle_password = 'examplePuzzlePassword'
    # For order of rewards, check file bars.db
    puzzle_rewards = [15, 10, 50, 90, 13]

    old_puzzles[puzzle_password] = puzzle_rewards

    json.dump(old_puzzles, f, ensure_ascii=False, indent=4)
