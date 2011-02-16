#!/usr/bin/env python2
from github2.client import Github
from flask import Flask, render_template, request, redirect
from datetime import timedelta
from babel.dates import format_date
import json

app = Flask(__name__)
github = Github()

CACHE_MAX_SIZE = 1000 
data_cache = {} 

def previous_monday(date):
    delta = timedelta(days=date.weekday())
    return date - delta

class RepoStats(object): 
    '''Computs stats about individual repositories on github.
       Stores weekly commits in json format.'''

    def __init__(self, repo_url, branch='master'):
        self.url = repo_url
        self.weekly_commits = []
        self.max_commits = 0
        self.branch = branch

    def compute_stats(self):
        try:
            commits = github.commits.list(self.url, self.branch)
        except RuntimeError:
            raise LookupError('Error occured while fetching commits for ' + self.url)

        # increment commit count or create a new count
        for c in reversed(commits):
            date_id = format_date(previous_monday(c.committed_date.date()))
            if not self.weekly_commits:
                self.weekly_commits.append({'date': date_id, 'count': 1})
            elif self.weekly_commits[-1]['date'] == date_id:
                self.weekly_commits[-1]['count'] += 1
            else:
                self.weekly_commits.append({'date': date_id, 'count': 1})

            self.max_commits = max(self.max_commits, self.weekly_commits[-1]['count'])

        self.weekly_commits = json.dumps(self.weekly_commits)

@app.route('/')
@app.route('/weekly_commits/<username>')
def weekly_commits(username='ramin32'):
    if username not in data_cache:
        try:
            repos = github.repos.list(username)
        except RuntimeError:
            return render_template('error.html', username=username, error='Invalid Username')

        repos_data = []

        # count commits per week for each repo
        for repo in repos:
            relative_repo_url = '%s/%s' % (username, repo.name)
            repo_stats = RepoStats(relative_repo_url)
            try:
                repo_stats.compute_stats()
            except LookupError, e:
                repo_stats.error = e

            repos_data.append(repo_stats)

        # ensure cache size
        if len(data_cache) > CACHE_MAX_SIZE:
            data_cache.clear()

        data_cache[username] = repos_data

    return render_template('commits.html', 
            username=username,
            repos_data=data_cache[username])

@app.route('/clear_cache')
def clear_cache():
    data_cache.clear()
    return redirect('/')


if __name__ == "__main__":
    app.debug = True
    app.run()
