from dotenv import load_dotenv
import os
import google.generativeai as genai
import pyttsx3 

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Combined Music & City Keywords ---
MUSIC_TERMS = [
    'music', 'song', 'band', 'artist', 'album', 'lyrics', 'genre',
    'tune', 'melody', 'harmony', 'chord', 'tempo', 'beat', 'rhythm',
    'concert', 'festival', 'gig', 'tour', 'single', 'EP', 'vinyl',
    'radio', 'charts', 'playlist', 'soundtrack', 'composition',
    'british', 'uk', 'english', 'scottish', 'welsh', 'celtic',
    'britpop', 'motown british invasion', 'northern soul',
    'punk', 'new wave', 'post-punk', 'synthpop', 'drum and bass',
    'grime', 'trip hop', 'shoegaze', 'heavy metal', 'folk rock',
    'london', 'camden', 'brixton', 'manchester', 'liverpool',
    'birmingham', 'bristol', 'glasgow', 'leeds', 'sheffield',
    'newcastle', 'nottingham', 'brighton', 'oxford', 'cambridge',
    'southampton', 'portsmouth', 'norwich', 'leicester', 'coventry',
    'hull', 'exeter', 'plymouth', 'stoke', 'york', 'canterbury',
    'edinburgh', 'dundee', 'aberdeen', 'inverness', 'cardiff',
    'swansea', 'newport', 'bangor', 'belfast', 'derry',
    'isle of wight', 'channel islands',
    'abbey road', 'cavern club', 'roundhouse', 'royal albert hall',
    'beatles', 'rolling stones', 'david bowie', 'queen', 'oasis',
    'radiohead', 'amy winehouse', 'adele', 'stormzy'
]

# --- City-Specific Intros ---
city_keywords = {
    'london': "London's legendary music scene spans",
    'camden': "Camden Town's iconic venues birthed",
    'brixton': "Brixton's multicultural sound forged",
    'manchester': "Manchester's revolutionary music legacy includes",
    'liverpool': "Liverpool's unparalleled musical heritage features",
    'birmingham': "Birmingham's influential contributions encompass",
    'bristol': "Bristol's groundbreaking sonic innovations include",
    'leeds': "Leeds' dynamic music culture showcases",
    'sheffield': "Sheffield's industrial musical roots produced",
    'newcastle': "Newcastle's Geordie sound is celebrated for",
    'nottingham': "Nottingham's eclectic scene blends",
    'brighton': "Brighton's seaside music culture thrives on",
    'oxford': "Oxford's academic music tradition nurtured",
    'cambridge': "Cambridge's folk and jazz heritage features",
    'southampton': "Southampton's port city sound mixes",
    'portsmouth': "Portsmouth's naval town punk spirit created",
    'norwich': "Norwich's underground scene cultivated",
    'leicester': "Leicester's multicultural music fusion combines",
    'coventry': "Coventry's 2-Tone revolution pioneered",
    'hull': "Hull's working-class music tradition includes",
    'exeter': "Exeter's West Country sound embraces",
    'plymouth': "Plymouth's maritime music culture features",
    'stoke': "Stoke-on-Trent's pottery town sound developed",
    'york': "York's medieval music revival blends",
    'canterbury': "Canterbury's progressive rock scene birthed",
    'glasgow': "Glasgow's fiercely independent music scene champions",
    'edinburgh': "Edinburgh's festival city sound incorporates",
    'dundee': "Dundee's post-industrial music resurgence features",
    'aberdeen': "Aberdeen's granite city sound resonates with",
    'inverness': "Inverness' Highland music tradition preserves",
    'cardiff': "Cardiff's Welsh language music revival celebrates",
    'swansea': "Swansea's copperopolis sound fuses",
    'newport': "Newport's working-class punk energy spawned",
    'bangor': "Bangor's North Wales music tradition honors",
    'belfast': "Belfast's Troubles-era music resilience produced",
    'derry': "Derry's border city sound synthesizes",
    'isle of wight': "The Isle of Wight's festival heritage inspired",
    'channel islands': "The Channel Islands' isolation cultivated"
}

def validate_query(query):
    query_lower = query.lower()
    if not any(term in query_lower for term in MUSIC_TERMS):
        return False, "I specialize in UK music - try asking about artists, genres, or cities like London or Belfast."
    return True, ""

def format_response(query, response_text):
    query_lower = query.lower()
    for city, intro in city_keywords.items():
        if city in query_lower:
            if not response_text.startswith(intro):
                return f"{intro} {response_text.lower()}"
    general_terms = ['music', 'song', 'genre', 'band', 'artist']
    if any(term in query_lower for term in general_terms):
        if not response_text.startswith(("In British music", "The UK music")):
            return f"In British music, {response_text.lower()}"
    return response_text

def generate_response(chat, query):
    is_valid, rejection_reason = validate_query(query)
    if not is_valid:
        return rejection_reason
    try:
        response = chat.send_message(
            f"Respond from UK music perspective: {query}",
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE'
            }
        )
        return format_response(query, response.text)
    except Exception as e:
        return f"Error: {str(e)}"

def initialize_chat():
    system_rules = """You are a British music expert. Rules:
    1. Only discuss UK music (England/Scotland/Wales/N. Ireland)
    2. Reject all non-music queries immediately
    3. Answer without bullet points, as a verbal prose, friendly and engaging.
    4. For general music terms, apply British context"""
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    return model.start_chat(history=[
        {'role': 'user', 'parts': [system_rules]},
        {'role': 'model', 'parts': ['Understood. I will discuss only British music.']}
    ])

# --- Main Application ---
if __name__ == "__main__":
    print("\n=== BRITISH MUSIC EXPERT ===")
    print("Type 'quit' or 'exit' to end\n")

    chat = initialize_chat()

    engine = pyttsx3.init()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            response = generate_response(chat, user_input)
            print("Bot:", response)

            engine.say(response)
            engine.runAndWait()

        except KeyboardInterrupt:
            print("\nSession ended by user.")
            break
        except Exception as e:
            print(f"System error: {str(e)}")
