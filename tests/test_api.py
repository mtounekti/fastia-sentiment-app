import pytest
from fastapi.testclient import TestClient
from api import app

# Client de test FastAPI — simule des requêtes HTTP sans lancer le serveur
client = TestClient(app)


# ──────────────────────────────────────────
# Tests de la route GET /
# ──────────────────────────────────────────

def test_root_status_code():
    """La route racine doit retourner un statut 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_message():
    """La route racine doit retourner le bon message de bienvenue."""
    response = client.get("/")
    assert "message" in response.json()


# ──────────────────────────────────────────
# Tests de la route POST /analyse_sentiment/
# ──────────────────────────────────────────

def test_analyse_sentiment_status_code():
    """La route d'analyse doit retourner un statut 200."""
    response = client.post("/analyse_sentiment/", json={"texte": "I love this!"})
    assert response.status_code == 200


def test_analyse_sentiment_keys():
    """La réponse doit contenir les 4 clés : neg, neu, pos, compound."""
    response = client.post("/analyse_sentiment/", json={"texte": "I love this!"})
    data = response.json()
    assert "neg" in data
    assert "neu" in data
    assert "pos" in data
    assert "compound" in data


def test_analyse_sentiment_scores_range():
    """Les scores neg, neu, pos doivent être entre 0 et 1."""
    response = client.post("/analyse_sentiment/", json={"texte": "This is okay."})
    data = response.json()
    assert 0.0 <= data["neg"] <= 1.0
    assert 0.0 <= data["neu"] <= 1.0
    assert 0.0 <= data["pos"] <= 1.0


def test_analyse_sentiment_compound_range():
    """Le score compound doit être entre -1 et 1."""
    response = client.post("/analyse_sentiment/", json={"texte": "This is okay."})
    data = response.json()
    assert -1.0 <= data["compound"] <= 1.0


# ──────────────────────────────────────────
# Tests avec parametrize — plusieurs textes
# ──────────────────────────────────────────

@pytest.mark.parametrize("texte, sentiment_attendu", [
    ("I love this, it's absolutely amazing!", "positif"),
    ("I hate this, it's terrible and awful!", "negatif"),
    ("The meeting is at 3pm.", "neutre"),
])
def test_sentiment_global(texte, sentiment_attendu):
    """Vérifie l'interprétation globale du sentiment selon le score compound."""
    response = client.post("/analyse_sentiment/", json={"texte": texte})
    assert response.status_code == 200
    compound = response.json()["compound"]

    if sentiment_attendu == "positif":
        assert compound >= 0.05, f"Attendu positif, compound={compound}"
    elif sentiment_attendu == "negatif":
        assert compound <= -0.05, f"Attendu négatif, compound={compound}"
    else:
        assert -0.05 < compound < 0.05, f"Attendu neutre, compound={compound}"


# ──────────────────────────────────────────
# Test avec fixture — données réutilisables
# ──────────────────────────────────────────

@pytest.fixture
def texte_positif():
    return {"texte": "I love this project, it's fantastic and wonderful!"}

@pytest.fixture
def texte_negatif():
    return {"texte": "I hate this, it's horrible and disgusting!"}


def test_texte_positif_compound(texte_positif):
    """Un texte positif doit avoir un compound >= 0.05."""
    response = client.post("/analyse_sentiment/", json=texte_positif)
    assert response.json()["compound"] >= 0.05


def test_texte_negatif_compound(texte_negatif):
    """Un texte négatif doit avoir un compound <= -0.05."""
    response = client.post("/analyse_sentiment/", json=texte_negatif)
    assert response.json()["compound"] <= -0.05


# ──────────────────────────────────────────
# Test — texte vide
# ──────────────────────────────────────────

def test_texte_vide():
    """Un texte vide doit retourner un statut 200 avec compound = 0.0."""
    response = client.post("/analyse_sentiment/", json={"texte": ""})
    assert response.status_code == 200
    assert response.json()["compound"] == 0.0


# ──────────────────────────────────────────
# Test — champ manquant dans la requête
# ──────────────────────────────────────────

def test_champ_manquant():
    """Une requête sans le champ 'texte' doit retourner une erreur 422."""
    response = client.post("/analyse_sentiment/", json={})
    assert response.status_code == 422