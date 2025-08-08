import requests

def workflow_dispatch(workflow_name, owner, repo, gh_token, branch = "main", inputs = None):
    """
    Trigger a GitHub Actions workflow dispatch event.
    :param workflow_name: Name of the workflow file (e.g., "build.yml").
    :param owner: Owner of the repository.
    :param repo: Name of the repository.
    :param gh_token: GitHub personal access token with repo permissions.
    :param branch: Branch to run the workflow on (default is "main").
    :param inputs: Optional dictionary of inputs to pass to the workflow.
    :return: Dictionary with the status code of the request.
    """
    try:
        url = f'https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_name}/dispatches'
        headers = {
            'Authorization': f'token {gh_token}',
            'Accept'       : 'application/vnd.github+json',
            'Content-Type' : 'application/json'
        }
        data = {
            'ref': branch
        }
        if inputs:
            data["inputs"] = inputs
        response = requests.post(url, headers = headers, json = data)
        return {"status": response.status_code}
    except:
        pass
    return {"status": 500}
