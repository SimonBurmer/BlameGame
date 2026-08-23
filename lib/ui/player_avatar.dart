import 'package:flutter/material.dart';

import '../models/game_models.dart';
import 'player_cosmetics.dart';

/// A player's circular avatar, tinted with their cosmetic colour.
///
/// The lobby and the results leaderboard draw the same circle at different
/// sizes, so the radii stay per-call-site.
class PlayerAvatar extends StatelessWidget {
  final GamePlayer player;
  final double radius;
  final double iconSize;

  const PlayerAvatar({
    super.key,
    required this.player,
    required this.radius,
    required this.iconSize,
  });

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: radius,
      backgroundColor: player.color.withValues(alpha: 0.3),
      child: Icon(player.avatar, color: player.color, size: iconSize),
    );
  }
}
