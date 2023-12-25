from github import Github, Auth


def github_login():
    auth = Auth.Token("redacted")
    g = Github(auth=auth)

    repo = g.get_user().get_repo('DS_database')
    return repo


def github_save(repo, file_name):
    with open(f'./{file_name}', 'r') as file:
        content = file.read()

    git_file = f'Database/{file_name}'
    try:
        contents = repo.get_contents(git_file)
        repo.update_file(contents.path, "database update", content, contents.sha, branch="master")
    except Exception:
        repo.create_file(git_file, "database create", content, branch="master")
