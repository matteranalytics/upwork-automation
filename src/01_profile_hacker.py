import urllib.parse

# --------------------------------------------------------------
# Find the top earning profiles in any niche on Upwork
# --------------------------------------------------------------


def generate_upwork_urls(niche_list, revenue, loc="all"):
    base_url = "https://www.upwork.com/ab/profiles/search/?&pt=independent"
    urls = {}
    for niche in niche_list:
        encoded_keyword = urllib.parse.quote(f'"{niche}"')
        url = f"{base_url}&q={encoded_keyword}&revenue={revenue}&loc={loc}"
        urls[niche] = url
    return urls


# Example niches
niche_list = [
    "python",
    "data science",
    "machine learning",
    "deep learning",
    "forecasting",
    "openai",
    "generative ai",
    "software development",
    "web development",
    "project management",
    "data visualization",
    "dashboards",
]
revenue = 1000000
loc = "all"
urls = generate_upwork_urls(niche_list, revenue, loc=loc)
