import 'package:flutter/material.dart';

/// A small rounded pill — the lobby's HOST badge and the game screen's round
/// and score chips.
///
/// The three call sites differ in padding, radius and fill alpha, so those
/// stay parameters; the shape is what is shared.
class PillBadge extends StatelessWidget {
  final Color color;
  final double fillAlpha;
  final double radius;
  final EdgeInsetsGeometry padding;
  final Widget child;

  const PillBadge({
    super.key,
    required this.color,
    required this.child,
    this.fillAlpha = 0.2,
    this.radius = 8,
    this.padding = const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: color.withValues(alpha: fillAlpha),
        borderRadius: BorderRadius.circular(radius),
      ),
      child: child,
    );
  }
}
