import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// A rounded, translucent card — the lobby's game-code box and player tiles,
/// the settings panel, and the results leaderboard rows.
///
/// Every call site uses a slightly different fill alpha, radius and padding,
/// so those stay parameters; what is shared is the
/// `Container(decoration: BoxDecoration(...))` shape itself.
class TintedCard extends StatelessWidget {
  /// Base colour for the fill and border. Defaults to white.
  final Color? tint;

  /// Fill opacity applied to [tint].
  final double fillAlpha;

  /// Border opacity applied to [tint]; null draws no border.
  final double? borderAlpha;

  final double borderWidth;
  final double radius;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final Widget child;

  const TintedCard({
    super.key,
    required this.child,
    this.tint,
    this.fillAlpha = 0.08,
    this.borderAlpha,
    this.borderWidth = 1.0,
    this.radius = 16,
    this.padding,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final base = tint ?? context.colors.onSurfaceStrong;
    return Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: base.withValues(alpha: fillAlpha),
        borderRadius: BorderRadius.circular(radius),
        border: borderAlpha == null
            ? null
            : Border.all(
                color: base.withValues(alpha: borderAlpha!),
                width: borderWidth,
              ),
      ),
      child: child,
    );
  }
}
