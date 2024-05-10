import httpx

url = "http://localhost:8000/api/v1/h2ogpt/converse?instruction=tell+me+a+short+story"

# data = {"pipelines": [], "dois": [], "urls": [], "h2ogpt_path": []}

headers = {
    "accept": "application/json",
    "Content-Type": "*/*",  # TODO: change this whatever the server returns
}


with httpx.stream("POST", url, headers=headers, timeout=None) as r:
    # set timeout to None. gradio too slow locally
    for chunk in r.iter_bytes():
        print(chunk)
