import 'package:flutter/material.dart';

class Player {
  final String name;
  final Color color;
  final IconData avatar;
  int score;

  Player({
    required this.name,
    required this.color,
    required this.avatar,
    this.score = 0,
  });
}

final List<Player> mockPlayers = [
  Player(name: 'You', color: Colors.blue, avatar: Icons.person),
  Player(name: 'Emma', color: Colors.pink, avatar: Icons.face_2),
  Player(name: 'Jake', color: Colors.green, avatar: Icons.face_3),
  Player(name: 'Sofia', color: Colors.orange, avatar: Icons.face_4),
  Player(name: 'Liam', color: Colors.purple, avatar: Icons.face_5),
];
