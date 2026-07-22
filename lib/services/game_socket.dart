import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config.dart';
import '../models/game_models.dart';

/// Wraps the game WebSocket and exposes a typed [Stream] of [GameEvent]s.
///
/// Connect with a room code and the player's id; the backend pushes events
/// (player_joined, round_started, round_revealed, guess_result, game_finished)
/// which we decode into [GameEvent] objects.
class GameSocket {
  final WebSocketChannel _channel;

  GameSocket._(this._channel);

  factory GameSocket.connect(String code, String playerId) {
    final channel = WebSocketChannel.connect(
      Uri.parse('$wsBase/ws/$code/$playerId'),
    );
    return GameSocket._(channel);
  }

  /// Decoded events from the server.
  Stream<GameEvent> get events => _channel.stream.map((raw) {
        final json = jsonDecode(raw as String) as Map<String, dynamic>;
        return GameEvent.fromJson(json);
      });

  void close() => _channel.sink.close();
}
