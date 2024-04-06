import wikipediaapi
from openai import OpenAI
from sqlite3 import connect

class ChatCompletion:
    """
    A class to wrap the OpenAI chat completion.
    """
    def __init__(self, client = None, model = None):
        self.client = client if client else OpenAI()
        self.model = model if model else "gpt-3.5-turbo"
    def __call__(self, query, seed = 0):
        answer = self.client.chat.completions.create(
            model=self.model,
            seed = seed,
            messages=[
                {
                    "role": "system",
                    "content": query
                }
            ]
        )
        self.fingerprint = answer.system_fingerprint
        return answer.choices[0].message.content
chat = ChatCompletion()
with open("myEmail.txt", "r") as file:
    email = file.read()
wiki = wikipediaapi.Wikipedia(f"master-keyword-extraction ({email})", language = "en", extract_format=wikipediaapi.ExtractFormat.WIKI)

con = connect("physics_terms.sqlite")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS terms (term TEXT UNIQUE, links_collected BOOLEAN, physics_term_checked BOOLEAN, is_technical_term BOOLEAN)")
con.commit()

def addWikipediaPageLinksToDatabase(pageTitle):
    cur.execute("INSERT OR IGNORE INTO terms (term, links_collected, physics_term_checked, is_technical_term) VALUES (?, ?, ?, ?)", (pageTitle, False, False, False))
    # Check if the links have already been collected
    cur.execute("SELECT links_collected FROM terms WHERE term = ?", (pageTitle,))
    links_collected = cur.fetchone()
    if links_collected and links_collected[0]:
        return
    cur.execute("UPDATE terms SET links_collected = 1 WHERE term = ?", (pageTitle,))
    # Get the page object
    page = wiki.page(pageTitle)
    # Add the links to the database
    for linkkey, linkvalue in page.links.items():
        if not ":" in linkvalue.title:
            cur.execute("INSERT OR IGNORE INTO terms (term, links_collected, physics_term_checked, is_technical_term) VALUES (?, ?, ?, ?)", (linkvalue.title, False, False, False))
    con.commit()

def chackAllUncheckedPhysicsTerms(manual = False):
    cur.execute("SELECT term FROM terms WHERE physics_term_checked = 0")
    terms = cur.fetchall()
    for term in terms:
        term = term[0]
        answer = chat(f"Is '{term}' a technical term in physics? (answer y or n)") if not manual else input(f"Is '{term}' a technical term in physics? (answer y or n)")
        if answer == "y":
            cur.execute("UPDATE terms SET is_technical_term = 1 WHERE term = ?", (term,))
        cur.execute("UPDATE terms SET physics_term_checked = 1 WHERE term = ?", (term,))
        con.commit()

addWikipediaPageLinksToDatabase("Physics")
chackAllUncheckedPhysicsTerms()
