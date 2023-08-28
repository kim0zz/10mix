from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flasgger import Swagger
from enum import Enum

app = Flask(__name__)
Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventList.db'
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    match_time = db.Column(db.DateTime, default=datetime.utcnow)
    mix10 = db.Column(db.Boolean, default=False)

class Team(Enum):
    CT = 'CT'
    TT = 'TT'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team = db.Column(db.Enum(Team), default=None, nullable=True)

@app.route('/api/event', methods=['GET'])
def get_all_events():
    """
    Get a list of all events
    ---
    tags:
      - Event API
    responses:
      200:
        description: A list of existing events
    """
    events = Event.query.all()
    event_list = [{"id": event.id, "name": event.name, "match_time": event.match_time, "mix10": event.mix10} for event in events]
    return jsonify(event_list)

@app.route('/api/event', methods=['POST'])
def create_event():
    """
    Create a new event
    ---
    tags:
      - Event API
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: Event name
      - name: match_time
        in: formData
        type: string
        required: true
        description: Event match time in format "YYYY-MM-DDTHH:MM:SS"
      - name: mix10
        in: formData
        type: boolean
        required: false
        description: Boolean indicating if event is mix10
    responses:
      201:
        description: Event created successfully
    """
    data = request.form
    event_name = data.get('name')
    match_time_string = data.get('match_time')
    match_time = datetime.strptime(match_time_string, '%Y-%m-%dT%H:%M:%S')
    mix10 = data.get('mix10', False)

    new_event = Event(name=event_name, match_time=match_time, mix10=mix10)
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event added successfully'}), 201

@app.route('/api/event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """
    Get details of a specific event
    ---
    tags:
      - Event API
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: Event ID
    responses:
      200:
        description: Event details
      404:
        description: Event not found
    """
    event = Event.query.get(event_id)

    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    return jsonify({'id': event.id, 'name': event.name, "match_time": event.match_time, "mix10": event.mix10})

@app.route('/api/event/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """
    Update details of a specific event
    ---
    tags:
      - Event API
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: Event ID
      - name: name
        in: formData
        type: string
        required: true
        description: New event name
      - name: match_time
        in: formData
        type: string
        required: true
        description: New event match time in format "YYYY-MM-DDTHH:MM:SS"
      - name: mix10
        in: formData
        type: boolean
        required: false
        description: New boolean indicating if event is mix10
    responses:
      200:
        description: Event updated successfully
      404:
        description: Event not found
    """
    event = Event.query.get(event_id)

    if not event:
        return jsonify({'message': 'Event not found'}), 404

    data = request.form
    new_name = data.get('name')
    new_time_string = data.get('match_time')
    new_time = datetime.strptime(new_time_string, '%Y-%m-%dT%H:%M:%S')
    mix10 = data.get('mix10', False)

    event.match_time = new_time
    event.name = new_name
    event.mix10 = mix10
    db.session.commit()
    return jsonify({'message': 'Event updated successfully'})

@app.route('/api/event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """
    Delete a specific event
    ---
    tags:
      - Event API
    parameters:
      - name: event_id
        in: path
        type: integer
        required: true
        description: Event ID
    responses:
      200:
        description: Event deleted successfully
      404:
        description: Event not found
    """
    event = Event.query.get(event_id)

    if not event:
        return jsonify({'message': 'Event not found'}), 404
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})

@app.route('/api/player', methods=['GET'])
def get_all_players():
    """
    Get a list of all players
    ---
    tags:
      - Player API
    responses:
      200:
        description: A list of players
    """
    players = Player.query.all()
    player_list = [{"id": player.id, "name": player.name, "event_id": player.event_id, "team": player.team.value if player.team else None} for player in players]
    return jsonify(player_list)

@app.route('/api/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """
    Get details of a specific player
    ---
    tags:
      - Player API
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: Player ID
    responses:
      200:
        description: Player details
      404:
        description: Player not found
    """
    player = Player.query.get(player_id)

    if not player:
        return jsonify({'message': 'Player not found'}), 404
    
    return jsonify({'id': player.id, 'name': player.name, "event_id": player.event_id, "team": player.team.value if player.team else None})

@app.route('/api/player', methods=['POST'])
def create_player():
    """
    Create a new player
    ---
    tags:
      - Player API
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: Player name
      - name: event_id
        in: formData
        type: integer
        required: true
        description: Event ID to associate with the player
      - name: team
        in: formData
        type: string
        required: false
        description: Team name (CT or TT)
    responses:
      201:
        description: Player created successfully
    """
    data = request.form
    player_name = data.get('name')
    event_id = data.get('event_id')
    team = data.get('team')

    new_player = Player(name=player_name, event_id=event_id, team=Team[team] if team else None)
    db.session.add(new_player)
    db.session.commit()
    return jsonify({'message': 'Player added successfully'}), 201

@app.route('/api/player/<int:player_id>', methods=['PUT'])
def update_player(player_id):
    """
    Update details of a specific player
    ---
    tags:
      - Player API
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: Player ID
      - name: name
        in: formData
        type: string
        required: true
        description: New player name
      - name: event_id
        in: formData
        type: integer
        required: true
        description: New event ID to associate with the player
      - name: team
        in: formData
        type: string
        required: false
        description: New team name (CT or TT)
    responses:
      200:
        description: Player updated successfully
      404:
        description: Player not found
    """
    player = Player.query.get(player_id)

    if not player:
        return jsonify({'message': 'Player not found'}), 404

    data = request.form
    new_name = data.get('name')
    new_event_id = data.get('event_id')
    new_team = data.get('team')

    player.name = new_name
    player.event_id = new_event_id
    player.team = Team[new_team] if new_team else None
    db.session.commit()
    return jsonify({'message': 'Player updated successfully'})

@app.route('/api/player/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    """
    Delete a specific player
    ---
    tags:
      - Player API
    parameters:
      - name: player_id
        in: path
        type: integer
        required: true
        description: Player ID
    responses:
      200:
        description: Player deleted successfully
      404:
        description: Player not found
    """
    player = Player.query.get(player_id)

    if not player:
        return jsonify({'message': 'Player not found'}), 404
    
    db.session.delete(player)
    db.session.commit()
    return jsonify({'message': 'Player deleted successfully'})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=True)