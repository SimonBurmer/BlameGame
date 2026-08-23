import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Full-width primary/secondary buttons.
///
/// The call sites use three different heights (50, 52, 56) and two different
/// radii (14, 16). Those differences are preserved as parameters rather than
/// unified: collapsing them would be a visual change, and this extraction is
/// meant to be invisible. What is shared is the `SizedBox(width: infinity)` +
/// `styleFrom` + bold letter-spaced label, which was copied six times.
///
/// [defaultButtonHeight] / [defaultButtonRadius] are the most common values,
/// not a house style — pass explicitly wherever the original differed.
const double defaultButtonHeight = 52;
const double defaultButtonRadius = 14;

/// Filled button. [color] defaults to the brand red.
class PrimaryButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback? onPressed;
  final double height;
  final double radius;
  final Color? color;

  /// Shown instead of the label while an action is in flight.
  final bool busy;

  /// Label size; null keeps the button's default.
  final double? fontSize;

  const PrimaryButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.height = defaultButtonHeight,
    this.radius = defaultButtonRadius,
    this.color,
    this.busy = false,
    this.fontSize,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final background = color ?? colors.brand;
    final style = ElevatedButton.styleFrom(
      backgroundColor: background,
      // Only the lobby's START button set this explicitly; Material's own
      // disabled fill is close but not identical, so keep it for every filled
      // button rather than leaving one call site visually different.
      disabledBackgroundColor: background.withValues(alpha: 0.3),
      foregroundColor: colors.onSurfaceStrong,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radius),
      ),
    );
    final text = Text(
      label,
      style: TextStyle(
        color: colors.onSurfaceStrong,
        fontSize: fontSize,
        fontWeight: FontWeight.bold,
        letterSpacing: 2,
      ),
    );
    final child = busy
        ? SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: colors.onSurfaceStrong,
            ),
          )
        : text;

    return SizedBox(
      width: double.infinity,
      height: height,
      child: icon == null
          ? ElevatedButton(onPressed: onPressed, style: style, child: child)
          : ElevatedButton.icon(
              onPressed: onPressed,
              style: style,
              icon: Icon(icon),
              label: child,
            ),
    );
  }
}

/// Outlined button with the faint white border used across the app.
class SecondaryButton extends StatelessWidget {
  final String label;
  final IconData? icon;
  final VoidCallback? onPressed;
  final double height;
  final double radius;

  /// Replaces the leading icon with a spinner while an action is in flight.
  final bool busy;

  /// The lobby's ADD PHOTOS label has no letter-spacing while the home
  /// screen's does, so it stays per-call-site rather than being unified.
  final double? letterSpacing;

  const SecondaryButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.height = defaultButtonHeight,
    this.radius = defaultButtonRadius,
    this.busy = false,
    this.letterSpacing = 2,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final style = OutlinedButton.styleFrom(
      side: BorderSide(color: colors.onSurfaceStrong.withValues(alpha: 0.3)),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radius),
      ),
    );
    final text = Text(
      label,
      style: TextStyle(
        color: colors.onSurfaceStrong,
        fontWeight: FontWeight.bold,
        letterSpacing: letterSpacing,
      ),
    );
    final leading = busy
        ? SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: colors.onSurfaceStrong,
            ),
          )
        : Icon(icon, color: colors.onSurfaceStrong);

    return SizedBox(
      width: double.infinity,
      height: height,
      child: icon == null && !busy
          ? OutlinedButton(onPressed: onPressed, style: style, child: text)
          : OutlinedButton.icon(
              onPressed: onPressed,
              style: style,
              icon: leading,
              label: text,
            ),
    );
  }
}
