
# youtube-ai-resume

**Generate concise AI summaries of YouTube videos from the command line.**

It works in two steps:

1. Downloads the video caption (subtitles) with `pytubefix`.
2. Sends the caption to the OpenAI API and returns a summary in the language you choose.

<p align="center">
  <img src="https://img.shields.io/pypi/v/youtube-ai-resume?color=brightgreen" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/youtube-ai-resume" alt="Python Version">
  <img src="https://img.shields.io/github/license/fberbert/youtube-ai-resume" alt="License">
</p>

---

## Features

* **Zero-setup CLI** → `youtube-ai-resume <video_url>`
* Summaries in any language (default `en_US`)
* Works with models like **`gpt-4.1-mini`** (configurable)
* Rich-formatted output with colours
* Usable as a *library* (`import youtube_ai_resume`)

---

## Installation

```bash
# Python ≥ 3.9
pip install youtube-ai-resume
```

Or, from source for development:

```bash
git clone https://github.com/fberbert/youtube-ai-resume.git
cd youtube-ai-resume
pip install -e ".[dev]"     # editable + dev tools
```

## Quick start

### Command Line Usage

```bash
export OPENAI_API_KEY="sk-..."
youtube-ai-resume https://www.youtube.com/watch?v=Ht2QW5PV-eY
```

Sample output:

```plaintext
Summary:

The speaker, Dashish, an engineer on OpenAI’s product team, discusses advancements in AI agents that integrate improved models with powerful tools to 
enhance user experience. Key points include:

- **Symbiotic Improvement**: Better tools enable more capable AI agents, which in turn can utilize more powerful tools, creating a continuous cycle of 
enhancement.
- **Agent Capabilities**: The AI agent can access various personal tools and data sources, such as Gmail and Google Calendar, through connectors to perform
complex tasks.
- **Use Case - Booking a Tennis Tournament Itinerary**:
  - The agent is tasked with planning a detailed itinerary for a tennis tournament in Palm Springs, focusing on semi-final dates.
  - It checks the tournament schedule, the user’s calendar availability, flight options, hotel bookings, match attendance, and dining plans.
  - The agent uses a visual browser and personal data access to gather and coordinate all necessary information.
- **User Experience**: The agent automates the research and planning process, handling logistical details like travel time and meeting schedules, then 
notifies the user with a comprehensive plan to review.
- **Benefit**: This automation frees users from mundane tasks, allowing them to focus on the core activities they care about.

Overall, the presentation highlights how integrating AI models with personal data and external tools can create intelligent agents that manage complex, 
personalized planning tasks efficiently.
```

### Library usage

```python
from youtube_ai_resume import caption, summarizer

txt = caption.fetch_caption("Ht2QW5PV-eY")
summary = summarizer.summarize(
    transcript=txt,
    api_key="sk-…",
    model="gpt-4.1-mini",
    out_lang="en_US"
)
print(summary)
```


## Proxy Support (Optional)

If you need to access YouTube or OpenAI via a proxy (for example, in cloud environments or to bypass IP restrictions), you can configure HTTP and HTTPS proxies in your config file.

### How to configure

Add the following fields to your `~/.config/youtube-ai-resume/config.json`:

```json
{
  "proxy_http": "http://username:password@proxy_ip:proxy_port",
  "proxy_https": "http://username:password@proxy_ip:proxy_port"
}
```

**Example:**

```json
{
  "proxy_http": "http://fabio:xxxx@187.84.229.156:3128",
  "proxy_https": "http://fabio:xxxx@187.84.229.156:3128"
}
```

If you do not need a proxy, simply leave these fields blank or omit them.

**Design rationale:**
- Proxy configuration is optional and does not affect local usage.
- The format is compatible with standard Python libraries and environment variables (`HTTP_PROXY`, `HTTPS_PROXY`).
- Credentials and port are included in the URL for authenticated proxies.

**Security note:** Never share your proxy password publicly.

---


## Voice narration (Text-to-Speech) [Optional]

You can optionally have the summary narrated aloud using Google Cloud Text-to-Speech (TTS).

### Optional Requirements (only if you want voice narration)

- A service account key (JSON) with permission to use TTS
- The dependencies `google-cloud-texttospeech` and `playsound` (already included in requirements.txt)

### Optional Setup

1. Create a project in Google Cloud and enable the Text-to-Speech API.
2. Generate and download a service account credentials file (JSON).
3. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your credentials file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
```

The default path is `~/.config/youtube-ai-resume/.google-credentials.json`. You can customize this path in your config file.

```json
{
    "google_credentials": "~/.config/youtube-ai-resume/.google-credentials.json"
}
```

### Usage

- To hear the summary narration, add the `--voice` option to the command:

```bash
youtube-ai-resume --voice 'https://www.youtube.com/watch?v=Ht2QW5PV-eY'
```

- To enable narration by default, add to your config.json:

```json
{
    "voice_enabled": true
}
```

You can customize voice, language, and speed in config.json (see code examples).

---

You can set the OpenAI API key as an environment variable or in a config file.

Environment variable:

```bash
OPENAI_API_KEY="sk-..."
```

Config file at ~/.config/youtube-ai-resume/config.json (auto-created on first run) lets you change the default model.

```json
{
    "model": "gpt-4.1-mini",
    "out_lang": "en"
}
```

## Development

Contributions are welcome!

Fork ➜ branch ➜ PR.

ruff check . and pytest must pass.

Describe your change clearly.

## License

Released under the MIT License – see LICENSE.

## Author

Fabio Berbert <fberbert@gmail.com>

I am open for job opportunities and collaborations.

## References

- [PyPI: youtube-ai-resume](https://pypi.org/project/youtube-ai-resume/)
- [GitHub: fberbert/youtube-ai-resume](https://github.com/fberbert/youtube-ai-resume)