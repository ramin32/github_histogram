#!/usr/bin/env python2
from github2.client import Github
from flask import Flask, render_template, request, redirect
from datetime import timedelta
from babel.dates import format_date
import json
from collections import OrderedDict

app = Flask(__name__)
github = Github()

app.jinja_env.filters['format_date'] = lambda d: format_date(d, locale='en')

data_cache = {}

def previous_monday(date):
    delta = timedelta(days=date.weekday())
    return date - delta

@app.route('/')
@app.route('/weekly_commits/<username>')
def weekly_commits(username='ramin32'):
    if username not in data_cache:
        try:
            repos = github.repos.list(username)
        except RuntimeError:
            return render_template('commits.html', 
                username=username,
                error='Invalid Username')

        repos_data = []

        
        for repo in repos:
            relative_repo_url = '%s/%s' % (username, repo.name)

            try:
                commits = github.commits.list(relative_repo_url, 'master')
            except RuntimeError:
                return render_template('commits.html', 
                    username=username,
                    error='An error occured while trying to fetch commits.')

            weekly_commits = []
            max_commits = 0

            for c in reversed(commits):
                date_id = format_date(previous_monday(c.committed_date.date()))
                if not weekly_commits:
                    weekly_commits.append({'date': date_id, 'count': 1})
                elif weekly_commits[-1]['date'] == date_id:
                    weekly_commits[-1]['count'] += 1
                else:
                    weekly_commits.append({'date': date_id, 'count': 1})
                max_commits = max(max_commits, weekly_commits[-1]['count'])

            data = dict(url=relative_repo_url,
                        weekly_commits=json.dumps(weekly_commits),
                        max_commits=max_commits)
            repos_data.append(data)

            data_cache[username] = repos_data

        if not repos:
            data_cache[username] = []

    return render_template('commits.html', 
            username=username,
            repos_data=data_cache[username])

@app.route('/clear_cache')
def clear_cache():
    data_cache.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run()
