---
title: BrowserServicePython
emoji: 🖥️
colorFrom: gray
colorTo: yellow
sdk: docker
sdk_version: "1.0"
app_file: app.py
pinned: false
license: gpl-3.0
---

# BrowserServicePython
browservice but from temu and in python

## DISCLAIMER
This project is provided for educational and research purposes only. The author, Arslaan Pathan, is not responsible for any misuse of this software. Users are solely responsible for their own actions.

## Hosting & Running

### Running locally with Docker
Clone the [GitHub repo](https://github.com/RealArslaanYT/BrowserServicePython) and build the docker image from Dockerfile.

```bash
git clone https://github.com/RealArslaanYT/BrowserServicePython.git
cd BrowserServicePython

docker build -t browserservice .
docker run -p 7860:7860 browserservice
```

Open http://localhost:7860 in your browser to access BrowserServicePython.

### Hosting your own copy on Hugging Face Spaces
**IMPORTANT**: Make sure you have created an [access token](https://huggingface.co/settings/tokens) on Hugging Face with write permissions before attempting this.

First, go to [Hugging Face - Create New Space](https://huggingface.co/new-space) and create a space.

Then, clone the [GitHub repo](https://github.com/RealArslaanYT/BrowserServicePython) and add your space as an remote.

```bash
git remote add huggingface https://huggingface.co/spaces/your-username/your-space-name
```

Next, push the repository to your space.

```bash
git push -f huggingface main
```

It may ask you for a username and password.
Use your Hugging Face username as the username, and your **access token** as the password.

## Live demo
If you're too lazy to host your own or don't have the time/resources to, there is a live demo hosted on Hugging Face spaces.

https://devwitharslaan-browserservicepython.hf.space

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0).  
Any modifications or derivatives must also be released under GPL-3.0. See the [LICENSE](LICENSE) file for details.


