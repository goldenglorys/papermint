import os
import json
import requests


def generate_metadata(temp_dir, chatgpt_token, chatgpt_topic):
    if chatgpt_token:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {chatgpt_token}",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a JSON generator. You only return valid JSON. You generate JSON with information about realistic scientific research papers for a given topic. The fields in the returned JSON object are: journal_name, thanks, author_name, author_organization, author_email, paper_title, paper_abstract",
                },
                {
                    "role": "user",
                    "content": f"Generate a valid JSON object with metadata about an award-winning research paper related to '{chatgpt_topic}'. Include the journal name, author thanks, author name, author organization, author email, paper title, and paper abstract.",
                },
            ],
        }
        response = requests.post(url, headers=headers, json=data)
        metadata = json.loads(response.json()["choices"][0]["message"]["content"])
        with open(f"{temp_dir}/metadata.json", "w") as f:
            json.dump(metadata, f)
        with open(f"{temp_dir}/metadata.md", "w") as f:
            f.write(
                f"""---
documentclass: IEEEtran
classoption:
  - journal
  - letterpaper
journal: |
  {metadata['journal_name']}
title: |
  {metadata['paper_title']}
thanks: |
  {metadata['thanks']}
author: 
  - |
    {metadata['author_name']}

    {metadata['author_organization']}

    [{metadata['author_email']}](mailto:{metadata['author_email']})
abstract: |
  {metadata['paper_abstract']}
...


"""
            )
    else:
        with open(f"{temp_dir}/metadata.md", "w") as f:
            f.write(
                """---
documentclass: IEEEtran
classoption:
  - journal
  - letterpaper
journal: |
  International Journal of Cybersecurity Research (IJCR)
title: |
  Adaptive Threat Intelligence Framework for Proactive Cyber Defense
thanks: |
  The authors would like to express their gratitude to the Cybersecurity
  Research Institute (CRI) for providing valuable resources and support
  during the research process
author: 
  - |
    Emily Collins, PhD

    Cybersecurity Institute for Advanced Research (CIAR)

    [`ecollins@ciar.org`](mailto:ecollins@ciar.org)
abstract: |
  In this paper, we present a novel approach for detecting advanced persistent
  threats (APTs) using deep learning techniques. APTs pose significant
  challenges to traditional security systems due to their stealthy and
  persistent nature. Our proposed method leverages a combination of
  convolutional neural networks and recurrent neural networks to analyze
  large-scale network traffic data. We introduce a novel attention mechanism
  that identifies subtle patterns in the data, enabling the detection of APTs
  with high accuracy. Experimental results on real-world datasets demonstrate
  the effectiveness of our approach in identifying previously unknown APTs
  while minimizing false positives. The framework offers a promising solution
  for enhancing the security posture of modern network infrastructures against
  sophisticated cyber threats.
...


"""
            )
