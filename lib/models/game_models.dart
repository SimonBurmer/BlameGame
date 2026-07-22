import 'package:flutter/material.dart';

/// A player as reported by the backend. Colors/avatars are NOT sent by the
/// server — they're derived client-side from the id for a stable, cosmetic look.
class GamePlayer {
  final String id;
  final String name;
  final int score;
  final bool isHost;

  const GamePlayer({
    required this.id,
    required this.name,
    this.score = 0,
    this.isHost = false,
  });

  factory GamePlayer.fromJson(Map<String, dynamic> json) => GamePlayer(
        id: json['id'] as String,
        name: json['name'] as String,
        score: (json['score'] as num?)?.toInt() ?? 0,
        isHost: json['is_host'] as bool? ?? false,
      );

  /// Stable cosmetic color derived from the id.
  Color get color => _cosmeticColors[id.hashCode.abs() % _cosmeticColors.length];

  /// Stable cosmetic avatar derived from the id.
  IconData get avatar => _cosmeticAvatars[id.hashCode.abs() % _cosmeticAvatars.length];
}

const List<Color> _cosmeticColors = [
  Colors.blue,
  Colors.pink,
  Colors.green,
  Colors.orange,
  Colors.purple,
  Colors.tealAccent,
  Colors.amber,
];

const List<IconData> _cosmeticAvatars = [
  Icons.person,
  Icons.face_2,
  Icons.face_3,
  Icons.face_4,
  Icons.face_5,
  Icons.face_6,
];

/// A photo reference from the backend (URL is relative to [apiBase]).
class PhotoInfo {
  final String id;
  final String ownerId;
  final String url;

  const PhotoInfo({required this.id, required this.ownerId, required this.url});

  factory PhotoInfo.fromJson(Map<String, dynamic> json) => PhotoInfo(
        id: json['id'] as String,
        ownerId: json['owner_id'] as String,
        url: json['url'] as String,
      );
}

/// Base type for events pushed over the WebSocket. We decode by the `type`
/// field into one of the concrete subclasses below.
sealed class GameEvent {
  const GameEvent();

  factory GameEvent.fromJson(Map<String, dynamic> json) {
    switch (json['type'] as String) {
      case 'player_joined':
        return PlayerJoined(
          GamePlayer.fromJson(json['player'] as Map<String, dynamic>),
        );
      case 'round_started':
        return RoundStarted(
          roundIndex: (json['round_index'] as num).toInt(),
          photo: PhotoInfo.fromJson(json['photo'] as Map<String, dynamic>),
        );
      case 'round_revealed':
        return RoundRevealed(
          roundIndex: (json['round_index'] as num).toInt(),
          ownerId: json['owner_id'] as String,
        );
      case 'guess_result':
        return GuessResult(
          guesserId: json['guesser_id'] as String,
          points: (json['points'] as num).toInt(),
          correct: json['correct'] as bool,
        );
      case 'game_finished':
        return GameFinished(
          (json['rankings'] as List<dynamic>)
              .map((e) => GamePlayer.fromJson(e as Map<String, dynamic>))
              .toList(),
        );
      default:
        return UnknownEvent(json['type'] as String);
    }
  }
}

class PlayerJoined extends GameEvent {
  final GamePlayer player;
  const PlayerJoined(this.player);
}

class RoundStarted extends GameEvent {
  final int roundIndex;
  final PhotoInfo photo;
  const RoundStarted({required this.roundIndex, required this.photo});
}

class RoundRevealed extends GameEvent {
  final int roundIndex;
  final String ownerId;
  const RoundRevealed({required this.roundIndex, required this.ownerId});
}

class GuessResult extends GameEvent {
  final String guesserId;
  final int points;
  final bool correct;
  const GuessResult({
    required this.guesserId,
    required this.points,
    required this.correct,
  });
}

class GameFinished extends GameEvent {
  final List<GamePlayer> rankings;
  const GameFinished(this.rankings);
}

class UnknownEvent extends GameEvent {
  final String type;
  const UnknownEvent(this.type);
}
