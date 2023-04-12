# UGC beat generator

## Operation modes
### Microservice

* `docker build --tag ugc-beat-generator . `
* `docker run -p 5001:5001  ugc-beat-generator:latest`

### CLI

* [Install ffmpeg](https://www.ffmpeg.org/download.html)
* `pip3 install -r cli/requirements.py`
* `python3 cli/cli.py --help`

