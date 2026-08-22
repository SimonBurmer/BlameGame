import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:blame_game/models/game_models.dart';
import 'package:blame_game/ui/player_cosmetics.dart';

void main() {
  group('PlayerCosmetics', () {
    test('the same id always maps to the same colour and avatar', () {
      const a = GamePlayer(id: 'abc', name: 'X');
      const b = GamePlayer(id: 'abc', name: 'Y', score: 500, isHost: true);
      expect(a.color, b.color);
      expect(a.avatar, b.avatar);
    });

    // Pins the actual mapping. Every client in a room derives cosmetics
    // independently, so the algorithm changing would silently give the same
    // person different colours on different devices — these values are the
    // contract, not an implementation detail.
    test('ids map to a pinned slot, so all clients agree', () {
      const cases = <String, (Color, IconData)>{
        'abc': (Colors.amber, Icons.person),
        'player-1': (Colors.purple, Icons.face_3),
        'player-2': (Colors.tealAccent, Icons.face_4),
        'zzzz': (Colors.orange, Icons.face_6),
      };
      cases.forEach((id, expected) {
        final player = GamePlayer(id: id, name: 'n');
        expect(player.color, expected.$1, reason: 'colour for "$id"');
        expect(player.avatar, expected.$2, reason: 'avatar for "$id"');
      });
    });

    test('different ids spread across more than one slot', () {
      final colors = {
        for (final id in ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
          GamePlayer(id: id, name: 'n').color,
      };
      expect(colors.length, greaterThan(1));
    });
  });
}
