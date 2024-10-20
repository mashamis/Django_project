import csv
import re
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

def load_data_from_csv(csv_file):
    training_data = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        sentence = ""
        entities = []
        start = 0

        for row in reader:
            token, label = row

            if token == '|':  # Reset for new sentence (| represents sentence boundary)
                if sentence:
                    training_data.append((sentence.strip(), {"entities": entities}))
                sentence = ""
                entities = []
                start = 0
                continue

            sentence += f" {token}"
            end = start + len(token)
            
            if label != '-':  # Skip tokens without labels
                entities.append((start, end, label))

            start = end + 1  # Account for space in between tokens

    return training_data

# Load the data
csv_file = 'data/products.csv' 
training_data = load_data_from_csv(csv_file)

def train_ner_model(training_data, iterations=10):
    nlp = spacy.blank("en")  # Create a blank English model
    ner = nlp.add_pipe("ner", last=True)

    # Add labels to the NER
    for _, annotations in training_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    optimizer = nlp.begin_training()

    for itn in range(iterations):
        losses = {}
        batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            for text, annotations in batch:
                # Create Example objects for training
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                # Update the model using Example objects
                nlp.update([example], drop=0.5, losses=losses)
        print(f"Iteration {itn} - Losses: {losses}")

    nlp.to_disk("model/ner_model")  # Save the model
    return nlp

# Train the NER model
if __name__ == "__main__":
    nlp = train_ner_model(training_data)
    print("Model training complete.")