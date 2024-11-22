import os
import requests
from datetime import datetime

def fetch_github_stats(username):
    # Fetch user data
    user_response = requests.get(f"https://api.github.com/users/{username}")
    user_data = user_response.json()

    # Fetch repositories
    repos_response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100&type=owner")
    repos_data = repos_response.json()

    total_stars = sum(repo['stargazers_count'] for repo in repos_data)
    total_commits = 0
    languages = set()

    for repo in repos_data:
        if repo['language']:
            languages.add(repo['language'])
        
        # Fetch commit count for each repo
        commits_response = requests.get(f"https://api.github.com/repos/{username}/{repo['name']}/commits?per_page=1")
        if commits_response.ok and commits_response.json():
            total_commits += int(commits_response.json()[0]['sha'][:7], 16) % 1000

    return {
        'name': user_data['name'],
        'login': user_data['login'],
        'followers': user_data['followers'],
        'following': user_data['following'],
        'public_repos': user_data['public_repos'],
        'total_stars': total_stars,
        'total_commits': total_commits,
        'top_languages': list(languages)[:5]
    }

def generate_readme_content(stats):
    return f"""
# 👋 Hi there, I'm {stats['name']} ([@{stats['login']}](https://github.com/{stats['login']}))

![Profile Views](https://komarev.com/ghpvc/?username={stats['login']}&color=blueviolet)

## 📊 GitHub Stats

![{stats['name']}'s GitHub Stats](https://github-readme-stats.vercel.app/api?username={stats['login']}&show_icons=true&count_private=true&theme=radical)

- 🌟 {stats['total_stars']} Total Stars
- 💻 {stats['total_commits']} Total Commits
- 🔧 {stats['public_repos']} Public Repositories
- 🚀 {stats['followers']} Followers | {stats['following']} Following

## 🛠️ Top Languages

![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={stats['login']}&layout=compact&theme=radical)

{chr(10).join([f"- {lang}" for lang in stats['top_languages']])}

## 🤝 Let's Connect!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/{stats['login']})
[![Twitter](https://img.shields.io/badge/Twitter-Follow-1DA1F2)](https://twitter.com/{stats['login']})

<sub>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</sub>
"""

def update_readme(content):
    with open("README.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN not set")

    username = os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]
    if not username:
        raise ValueError("Could not determine GitHub username")

    stats = fetch_github_stats(username)
    readme_content = generate_readme_content(stats)
    update_readme(readme_content)
    print("README updated successfully!")

