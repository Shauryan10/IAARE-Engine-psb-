import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const IAAREAuthenticator());
}

class IAAREAuthenticator extends StatelessWidget {
  const IAAREAuthenticator({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "IAARE Authenticator",
      theme: ThemeData(
        primaryColor: const Color(0xFFC8102E),
        scaffoldBackgroundColor: Colors.white,

        appBarTheme: const AppBarTheme(
           backgroundColor: Color(0xFFC8102E),
           foregroundColor: Colors.white,
          ),

        floatingActionButtonTheme: const FloatingActionButtonThemeData(
           backgroundColor: Color(0xFFC8102E),
           foregroundColor: Colors.white,
          ),
      ),
      home: const HomeScreen(),
    );
  }
}