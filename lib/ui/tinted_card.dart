import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// A rounded, translucent card — the lobby's game-code box and player tiles,
/// the settings panel, and the results leaderboard rows.
///
/// Every call site uses a slightly different fill alpha, radius and padding,
/// so those stay parameters; what is shared is the rounded translucent shape
/// itself.
///
/// The fill is painted by a [Material] rather than a `BoxDecoration`, because
/// these cards contain tappable things. Ink splashes and `ListTile` backgrounds
/// are drawn on the nearest [Material] ancestor, so a decorated box painted
/// *over* that ancestor swallows them — the settings panel's switch had no
/// ripple at all, and Flutter asserts on exactly this arrangement.
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
    final card = Material(
      color: base.withValues(alpha: fillAlpha),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radius),
        // strokeAlign defaults to inside, the same place BoxDecoration drew
        // this border, so the card's outer size is unchanged.
        side: borderAlpha == null
            ? BorderSide.none
            : BorderSide(
                color: base.withValues(alpha: borderAlpha!),
                width: borderWidth,
              ),
      ),
      child: padding == null ? child : Padding(padding: padding!, child: child),
    );
    return margin == null ? card : Padding(padding: margin!, child: card);
  }
}
