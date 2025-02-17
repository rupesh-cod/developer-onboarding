import requests
import networkx as nx
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS onboarding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            experience TEXT NOT NULL,
            languages TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    email = data['email']
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
              (email, username, password))
    conn.commit()
    user_id = c.lastrowid
    conn.close()

    return jsonify({'user_id': user_id})

def detect_technologies_from_commit(commit_message):
    """Detects mentioned technologies in commit messages."""
    technologies = ["Python", "Django", "Flask", "JavaScript", "React", "Node.js", "AWS", "Terraform"]
    detected_technologies = [tech for tech in technologies if tech.lower() in commit_message.lower()]
    return detected_technologies

def build_skill_graph():
    """Creates a directed graph of skill dependencies."""
    G = nx.DiGraph()
    G.add_edge("Python", "Django")
    G.add_edge("Python", "Flask")
    G.add_edge("JavaScript", "React")
    G.add_edge("JavaScript", "Node.js")
    G.add_edge("AWS", "Terraform")
    return G

def recommend_skills(commits):
    """Recommends new skills based on detected technologies in commit messages."""
    G = build_skill_graph()
    detected_skills = set()

    for commit in commits:
        technologies = detect_technologies_from_commit(commit["commit"]["message"])
        detected_skills.update(technologies)

    print(f"Detected Technologies: {detected_skills}")  # Debug print

    recommendations = set()
    for skill in detected_skills:
        if skill in G:
            recommendations.update(G.successors(skill))

    print(f"Recommended Skills: {recommendations}")  # Debug print

    return list(recommendations)

def fetch_repos(username, token):
    """Fetches a list of user repositories from GitHub."""
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repos: {response.status_code}, {response.text}")
        return []

def fetch_commit_history(username, repo_name, token):
    """Fetches commit history for a specific repository."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching commits for {repo_name}: {response.status_code}, {response.text}")
        return []

@app.route('/analyze_github', methods=['POST'])
def analyze_github():
    data = request.json
    github_username = data['githubUsername']
    github_token = data['githubToken']

    repos = fetch_repos(github_username, github_token)
    if not repos:
        return jsonify({"error": "No repositories found or authentication issue."})

    all_commits = []
    for repo in repos[:3]:  # Limit to first 3 repos for efficiency
        commits = fetch_commit_history(github_username, repo['name'], github_token)
        all_commits.extend(commits)

    recommended_skills = recommend_skills(all_commits)
    return jsonify({"recommended_skills": recommended_skills})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
