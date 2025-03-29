from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from datetime import datetime

app = Flask(__name__, template_folder=".", static_folder=".")

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Fetch user submissions
    submissions_url = f"https://codeforces.com/api/user.status?handle={username}"
    response = requests.get(submissions_url)
    
    if response.status_code != 200:
        return jsonify({"error": "Error calling Codeforces API"}), 500

    submissions_data = response.json()
    if submissions_data.get("status") != "OK":
        return jsonify({"error": "Invalid response from Codeforces"}), 500

    submissions = submissions_data["result"]

    # Process solved problems by rating
    ratings_count = {}
    for sub in submissions:
        if sub.get('verdict') == 'OK':
            problem = sub.get('problem', {})
            rating = problem.get('rating')
            if rating:
                ratings_count[rating] = ratings_count.get(rating, 0) + 1

    return jsonify({"ratings": ratings_count})

@app.route('/fetch_problems', methods=['GET'])
def fetch_problems():
    username = request.args.get('username', '').strip()
    rating = request.args.get('rating', '').strip()

    if not username or not rating.isdigit():
        return jsonify({"error": "Invalid request parameters"}), 400

    rating = int(rating)

    # Fetch user submissions
    submissions_url = f"https://codeforces.com/api/user.status?handle={username}"
    response = requests.get(submissions_url)
    
    if response.status_code != 200:
        return jsonify({"error": "Error fetching Codeforces API"}), 500

    submissions_data = response.json()
    if submissions_data.get("status") != "OK":
        return jsonify({"error": "Invalid response from Codeforces API"}), 500

    submissions = submissions_data["result"]

    # Filter solved problems of selected rating
    solved_problems = []
    for sub in submissions:
        if sub.get('verdict') == 'OK':
            problem = sub.get('problem', {})
            if problem.get('rating') == rating:
                solved_problems.append({
                    "name": problem.get("name", "Unknown Problem"),
                    "contestId": problem.get("contestId"),
                    "index": problem.get("index"),
                    "submission_time": sub.get("creationTimeSeconds", 0)
                })

    # Fetch contest list
    contest_info = {}
    contests_url = "https://codeforces.com/api/contest.list?gym=false"
    contests_response = requests.get(contests_url)
    
    if contests_response.status_code == 200:
        contest_data = contests_response.json()
        if contest_data.get("status") == "OK":
            for contest in contest_data["result"]:
                contest_info[contest["id"]] = {
                    "startTime": contest.get("startTimeSeconds", 0),
                    "name": contest.get("name", "")
                }

    # Attach contest details
    for problem in solved_problems:
        contest_data = contest_info.get(problem.get('contestId'), {})
        problem['contest_name'] = contest_data.get('name', "Unknown Contest")

    # Sort problems by submission time (descending)
    solved_problems.sort(key=lambda p: p.get('submission_time', 0), reverse=True)

    return jsonify({"problems": solved_problems})

@app.route('/result')
def result():
    username = request.args.get('username', '')
    rating = request.args.get('rating', '')

    if not username or not rating:
        return "Invalid request parameters", 400

    return render_template('result.html', username=username, rating=rating)

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(".", filename)

if __name__ == '__main__':
    app.run(debug=True)
