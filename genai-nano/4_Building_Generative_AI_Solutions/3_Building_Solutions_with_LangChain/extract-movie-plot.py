import requests


def get_movie_plot(movie_name):
    headers = {
        'User-Agent': 'MoviePlotFetcher/1.0'
    }
    
    base_url = f"https://en.wikipedia.org/w/api.php"
        
    def is_movie_page(title):
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "categories|revisions",
            "rvprop": "content",
            "cllimit": "max"
        }
    
        response = requests.get(base_url, headers=headers, params=params)
        data = response.json()
    
        try:
            page = list(data["query"]["pages"].values())[0]
            
            # Check categories for Movie indication
            categories = [cat["title"] for cat in page.get("categories", [])]
            for category in categories:
                if "films" in category.lower():
                    return True
                    
            # Check for infobox movie in the page content
            content = page["revisions"][0]["*"]
            if "{{Infobox film" in content:
                return True
                
        except Exception as e:
            pass

        return False
    
    def extract_plot_from_text(full_text):
        try:
            # Find the start of the Plot section
            plot_start = full_text.index("== Plot ==") + len("== Plot ==")
            
            # Find the start of the next section
            next_section_start = full_text.find("==", plot_start)

            # If no next section is found, use the end of the text
            if next_section_start == -1:
                next_section_start = len(full_text)

            # Extract the plot text and strip leading/trailing whitespace
            plot_text = full_text[plot_start:next_section_start].strip()

            # Return the extracted plot
            return plot_text

        except ValueError:
            # Return a message if the Plot section isn't found
            return "Plot section not found in the text."
        
    def extract_first_paragraph(full_text):
        # Find the first double newline
        end_of_first_paragraph = full_text.find("\n\n")

        # If found, slice the string to get the first paragraph
        if end_of_first_paragraph != -1:
            return full_text[:end_of_first_paragraph].strip()

        # If not found, return the whole text as it might be just one paragraph
        return full_text.strip()

    
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": movie_name,
        "utf8": 1,
        "srlimit": 5  # Top 5 search results
    }

    response = requests.get(base_url, headers=headers, params=search_params)
    data = response.json()
    
    # Go through top search results to find a movie page
    for search_result in data["query"]["search"]:
        title = search_result["title"]
        if is_movie_page(title):
            # Fetch plot for the movie page
            plot_params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "explaintext": True,
            }
            
            plot_response = requests.get(base_url, headers=headers, params=plot_params)
            plot_data = plot_response.json()
            
            try:
                page = list(plot_data["query"]["pages"].values())[0]
                full_text = page.get("extract", "No text...")
                return f"""Overview:\n{extract_first_paragraph(full_text)}\nPlot:\n{extract_plot_from_text(full_text)}""".strip()
            except:
                return "Error fetching plot."

    return "Movie not found."


        
# Test the function
movie_name = "Nightmare before Christmas"
print(get_movie_plot(movie_name))
