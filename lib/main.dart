import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const PhotoRouletteApp());
}

class PhotoRouletteApp extends StatelessWidget {
  const PhotoRouletteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Photo Roulette',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE94560),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
