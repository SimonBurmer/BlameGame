import 'package:flutter/material.dart';

/// The game's palette.
///
/// A [ThemeExtension] rather than loose constants so screens read colours from
/// the theme instead of hardcoding them, and so the whole look can change in
/// one place. Values are the ones the screens already used.

/// Foreground tints over the dark background. Declared as top-level constants
/// so both [AppColors] and the const [TextTheme] below can use them.
const _white = Colors.white;
const _whiteMuted = Color(0xB3FFFFFF); // 70%
const _whiteFaint = Color(0x80FFFFFF); // 50%

@immutable
class AppColors extends ThemeExtension<AppColors> {
  /// Background gradient, top to bottom.
  final Color bgTop;
  final Color bgMid;
  final Color bgBottom;

  /// Brand red — primary actions.
  final Color brand;

  /// Teal accent — secondary actions and "plenty of time left".
  final Color accent;

  /// Podium colours.
  final Color gold;
  final Color silver;
  final Color bronze;

  /// Result feedback.
  final Color correct;
  final Color wrong;

  /// Foreground tints over the dark background.
  final Color onSurfaceStrong;
  final Color onSurfaceMuted;
  final Color onSurfaceFaint;

  /// Fills for cards and pills.
  final Color surfaceTint;
  final Color surfaceTintStrong;

  const AppColors({
    required this.bgTop,
    required this.bgMid,
    required this.bgBottom,
    required this.brand,
    required this.accent,
    required this.gold,
    required this.silver,
    required this.bronze,
    required this.correct,
    required this.wrong,
    required this.onSurfaceStrong,
    required this.onSurfaceMuted,
    required this.onSurfaceFaint,
    required this.surfaceTint,
    required this.surfaceTintStrong,
  });

  static const dark = AppColors(
    bgTop: Color(0xFF1A1A2E),
    bgMid: Color(0xFF16213E),
    bgBottom: Color(0xFF0F3460),
    brand: Color(0xFFE94560),
    accent: Color(0xFF4ECDC4),
    gold: Color(0xFFFFD700),
    silver: Color(0xFFC0C0C0),
    bronze: Color(0xFFCD7F32),
    correct: Colors.greenAccent,
    wrong: Color(0xFFE94560),
    onSurfaceStrong: _white,
    onSurfaceMuted: _whiteMuted,
    onSurfaceFaint: _whiteFaint,
    surfaceTint: Color(0x14FFFFFF), // white @ 8%
    surfaceTintStrong: Color(0x26FFFFFF), // white @ 15%
  );

  @override
  AppColors copyWith() => this;

  @override
  AppColors lerp(AppColors? other, double t) => other ?? this;
}

/// Convenience: `context.colors.brand`.
extension AppColorsOf on BuildContext {
  AppColors get colors => Theme.of(this).extension<AppColors>() ?? AppColors.dark;
}

ThemeData buildAppTheme() {
  const c = AppColors.dark;
  final scheme = ColorScheme.fromSeed(
    seedColor: c.brand,
    brightness: Brightness.dark,
  ).copyWith(primary: c.brand, surface: c.bgTop);

  final base = ThemeData(colorScheme: scheme, useMaterial3: true);

  return base.copyWith(
    extensions: const [c],
    scaffoldBackgroundColor: Colors.transparent,
    // This is a touch app: keep Material's 48x48 minimum tap target instead of
    // the host-adaptive density, which shrinks controls on desktop.
    visualDensity: VisualDensity.standard,
    textTheme: base.textTheme.copyWith(
      displayLarge: const TextStyle(
        fontSize: 44,
        fontWeight: FontWeight.w900,
        letterSpacing: 4,
        height: 1.1,
        color: _white,
      ),
      headlineLarge: const TextStyle(
        fontSize: 36,
        fontWeight: FontWeight.w900,
        color: _white,
      ),
      titleLarge: const TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        letterSpacing: 3,
        color: _white,
      ),
      titleMedium: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: _white,
      ),
      labelLarge: const TextStyle(
        fontSize: 13,
        fontWeight: FontWeight.w600,
        letterSpacing: 2,
        color: _whiteMuted,
      ),
      labelSmall: const TextStyle(
        fontSize: 15,
        fontWeight: FontWeight.bold,
        letterSpacing: 2,
        color: _white,
      ),
      bodyMedium: const TextStyle(fontSize: 14, color: _whiteMuted),
    ),
  );
}
