import 'package:flutter/material.dart';

class MockPhoto {
  final String ownerName;
  final Color dominantColor;
  final IconData icon;
  final String label;

  const MockPhoto({
    required this.ownerName,
    required this.dominantColor,
    required this.icon,
    required this.label,
  });
}

const List<MockPhoto> mockPhotos = [
  MockPhoto(
    ownerName: 'Emma',
    dominantColor: Color(0xFFE8B4B8),
    icon: Icons.pets,
    label: 'A cute cat on a sofa',
  ),
  MockPhoto(
    ownerName: 'Jake',
    dominantColor: Color(0xFF87CEEB),
    icon: Icons.surfing,
    label: 'Surfing at sunset',
  ),
  MockPhoto(
    ownerName: 'You',
    dominantColor: Color(0xFF98FB98),
    icon: Icons.restaurant,
    label: 'Fancy dinner plate',
  ),
  MockPhoto(
    ownerName: 'Sofia',
    dominantColor: Color(0xFFDDA0DD),
    icon: Icons.landscape,
    label: 'Mountain hiking trip',
  ),
  MockPhoto(
    ownerName: 'Liam',
    dominantColor: Color(0xFFFFD700),
    icon: Icons.sports_basketball,
    label: 'Basketball game night',
  ),
  MockPhoto(
    ownerName: 'Emma',
    dominantColor: Color(0xFFFF6B6B),
    icon: Icons.cake,
    label: 'Birthday celebration',
  ),
  MockPhoto(
    ownerName: 'You',
    dominantColor: Color(0xFF4ECDC4),
    icon: Icons.flight,
    label: 'Airport selfie',
  ),
];
