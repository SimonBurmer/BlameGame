import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// The dark gradient background every screen sits on.
///
/// The three screens genuinely use three *different* gradients, so this widget
/// takes the variant rather than unifying them — unifying would be a visual
/// change, and this extraction is meant to be invisible. What is shared is the
/// [Scaffold] + [Container] + [SafeArea] sandwich, which was copied four times.
enum AppGradient {
  /// Home and lobby: diagonal, all three background stops.
  diagonal,

  /// Game: vertical, and skips the middle stop.
  verticalTwoStop,

  /// Results: vertical, all three stops.
  verticalThreeStop,
}

class GradientScaffold extends StatelessWidget {
  final AppGradient gradient;
  final Widget child;

  const GradientScaffold({
    super.key,
    required this.gradient,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.colors;
    final (begin, end, colors) = switch (gradient) {
      AppGradient.diagonal => (
        Alignment.topLeft,
        Alignment.bottomRight,
        [c.bgTop, c.bgMid, c.bgBottom],
      ),
      AppGradient.verticalTwoStop => (
        Alignment.topCenter,
        Alignment.bottomCenter,
        [c.bgTop, c.bgBottom],
      ),
      AppGradient.verticalThreeStop => (
        Alignment.topCenter,
        Alignment.bottomCenter,
        [c.bgTop, c.bgMid, c.bgBottom],
      ),
    };
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(begin: begin, end: end, colors: colors),
        ),
        child: SafeArea(child: child),
      ),
    );
  }
}
