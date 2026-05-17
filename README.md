# Observing Eagles: A Practitioners Guide

This project contains the documentation and supporting infrastructure for the "Observing Eagles" guide.

## Project Structure

- `docs/`: Contains the Markdown files and assets for the documentation site.
- `worker.js`: A Cloudflare Worker that proxies lake level data from the USACE API to handle CORS and caching.
- `wrangler.toml`: Configuration for the Cloudflare Worker deployment.
- `mkdocs.yml`: Configuration for the MkDocs site.

## Site Setup & Development

The documentation site is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

### Prerequisites
- Python 3.x
- pip

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Local Development
To run the site locally for preview:
```bash
mkdocs serve
```
The site will be available at `http://127.0.0.1:8000`.

### Building the Site
To build the static site for deployment:
```bash
mkdocs build
```

## Cloudflare Worker Deployment

The `worker.js` file provides a proxy to the USACE lake level API.

### Prerequisites
- [Node.js](https://nodejs.org/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

### Deployment
1. Authenticate with Cloudflare:
   ```bash
   npx wrangler login
   ```
2. Deploy the worker:
   ```bash
   npx wrangler deploy worker.js
   ```

## Live Site
The published documentation can be found at: [https://laszewski.github.io/raptors/](https://laszewski.github.io/raptors/)