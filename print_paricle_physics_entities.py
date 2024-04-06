import spacy
import wikipediaapi

# Get the text data from wikipedia page

with open("myEmail.txt", "r") as file:
    email = file.read()
wiki = wikipediaapi.Wikipedia(f"master-keyword-extraction ({email})", language = "en", extract_format=wikipediaapi.ExtractFormat.WIKI)
page = wiki.page("Particle Physics")
nlp = spacy.load("en_core_web_lg")
text = page.summary
doc = nlp(text)
print(doc.ents)
