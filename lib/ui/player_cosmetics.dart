import 'package:flutter/material.dart';

import '../models/game_models.dart';

/// Per-player colour and avatar.
///
/// The server never sends these — they're derived client-side from the
/// player id so every client shows the same person the same way. Kept in the
/// UI layer (rather than on [GamePlayer]) so the model stays pure Dart and can
/// be decoded and tested without Flutter.
extension PlayerCosmetics on GamePlayer {
  /// Stable cosmetic colour derived from the id.
  Color get color => _colors[_slot(id, _colors.length)];

  /// Stable cosmetic avatar derived from the id.
  IconData get avatar => _avatars[_slot(id, _avatars.length)];
}

/// Deterministic bucket for [id].
///
/// Deliberately not `String.hashCode`: Dart only guarantees that to be
/// consistent within a single process, so the VM and dart2js disagree and an
/// iOS player and a web player would see different colours for the same
/// person — confusing in a game where you identify people by their colour.
int _slot(String id, int buckets) =>
    id.codeUnits.fold(0, (hash, unit) => (hash * 31 + unit) % 1000003) % buckets;

const List<Color> _colors = [
  Colors.blue,
  Colors.pink,
  Colors.green,
  Colors.orange,
  Colors.purple,
  Colors.tealAccent,
  Colors.amber,
];

const List<IconData> _avatars = [
  Icons.person,
  Icons.face_2,
  Icons.face_3,
  Icons.face_4,
  Icons.face_5,
  Icons.face_6,
];
