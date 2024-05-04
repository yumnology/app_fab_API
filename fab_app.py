from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')



db = SQLAlchemy(app)

class EmotionEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'emotion': self.emotion,
            'date': self.date.isoformat()
        }

BASE_URL = '/api/v1/'

@app.route('/')
def home():
    return 'Welcome to the Emotion API'

@app.route(BASE_URL + 'emotions', methods=['POST'])
def create_emotion_entry():
    if not request.json or 'emotion' not in request.json:
        abort(400, description='Missing "emotion" in JSON data')

    emotion_score = request.json['emotion']
    if not (1 <= emotion_score <= 5):
        abort(400, description='Invalid emotion score. Must be between 1 and 5.')

    emotion_map = {
        1: "Sad",
        2: "Angry",
        3: "Meh",
        4: "Happy",
        5: "Joy"
    }
    emotion_text = emotion_map[emotion_score]

    entry = EmotionEntry(emotion=emotion_text)
    db.session.add(entry)
    db.session.commit()

    return jsonify({'emotion_entry': entry.to_json()}), 201

@app.route(BASE_URL + 'emotions', methods=['GET'])
def get_emotions():
    entries = EmotionEntry.query.all()
    return jsonify({'emotions': [entry.to_json() for entry in entries]})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
