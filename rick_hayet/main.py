import base64
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Identifiants Spotify
CLIENT_ID = "275173bde70142989a7a78435aadd78a"
CLIENT_SECRET = "c1cf8b1dbbfd46379292c7efd771824f"


def get_access_token(client_id, client_secret):
    """
    Fonction pour générer un token d'accès en utilisant le Client Credentials Flow
    """
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    token_url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {client_creds_b64}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Erreur : {response.status_code} {response.text}")


def get_top_tracks(artist_id, access_token):
    """
    Récupérer les 10 morceaux les plus populaires d'un artiste
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tracks = response.json()["tracks"]
        for track in tracks:
            print(f"{track['name']} (Popularité : {track['popularity']})")
            # Rechercher les paroles de la chanson
            lyrics = search_lyrics(track['name'], track['artists'][0]['name'])
            if lyrics:
                # Analyser les paroles et créer un nuage de mots
                analyze_lyrics(lyrics)
                generate_wordcloud(lyrics)
    else:
        print(f"Erreur : {response.status_code}, {response.text}")


def search_lyrics(track_name, artist_name):
    """
    Recherche les paroles d'une chanson en utilisant une API de paroles.
    """
    print(
        f"Recherche des paroles pour \"{track_name}\" de \"{artist_name}\"...")

    response = requests.get(
        "https://lrclib.net/api/get",
        params={"track_name": track_name, "artist_name": artist_name},
    )

    if response.status_code == 200 and "lyrics" in response.json():
        return response.json()["lyrics"]

    print(f"Aucune parole trouvée pour \"{track_name}\" de \"{artist_name}\".")
    return None


def analyze_lyrics(lyrics):
    """
    Analyse les paroles pour les mots les plus utilisés et crée un graphique à barres.
    """
    # Nettoyage des paroles (enlever les retours à la ligne et la ponctuation)
    lyrics = lyrics.replace("\n", " ").lower()
    words = lyrics.split()
    word_count = {}

    # Compter les occurrences des mots
    for word in words:
        word = word.strip(".,!?()[]{}:;'\"")
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1

    # Trier les mots par fréquence
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    print("\nLes mots les plus utilisés :")
    for word, count in sorted_words[
                       :10]:  # Afficher les 10 mots les plus fréquents
        print(f"{word}: {count} fois")

    # Afficher le graphique à barres
    words, counts = zip(*sorted_words[
                         :10])  # Extraire les 10 premiers mots et leurs fréquences
    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.title("Les 10 mots les plus utilisés dans les paroles")
    plt.xlabel("Mots")
    plt.ylabel("Fréquence")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def generate_wordcloud(lyrics):
    """
    Génère un nuage de mots à partir des paroles
    """
    # Nettoyer les paroles (enlever les retours à la ligne et la ponctuation)
    lyrics = lyrics.replace("\n", " ").lower()

    # Créer le nuage de mots
    wordcloud = WordCloud(width=800, height=400,
                          background_color='white').generate(lyrics)

    # Afficher le nuage de mots
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Nuage de mots des paroles de la chanson")
    plt.show()


if __name__ == "__main__":
    try:
        # Obtenir le token d'accès
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

        artist_id = "4dpARuHxo51G3z768sgnrY"  # Remplacer par l'ID de l'artiste souhaité
        get_top_tracks(artist_id, access_token)

    except Exception as e:
        print("Erreur :", e)
