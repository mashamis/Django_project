import spacy

def load_model():
    model_path = 'model/ner_model'  # Path where the trained model is saved
    return spacy.load(model_path)

# Predict entities from text input
def predict_entities(text):
    nlp = load_model()  # Load the saved model
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities