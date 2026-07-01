import 'package:flutter/material.dart';
import 'add_account_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  static const Color primaryRed = Color(0xFFC8102E);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,

      appBar: AppBar(
        backgroundColor: primaryRed,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          "IAARE Authenticator",
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [

            Icon(
              Icons.security,
              size: 90,
              color: primaryRed,
            ),

            SizedBox(height: 20),

            Text(
              "No Accounts Added",
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),

            SizedBox(height: 10),

            Text(
              "Tap the + button to add an account",
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),

      floatingActionButton: FloatingActionButton(
        backgroundColor: primaryRed,
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () async {

           final result = await Navigator.push(
             context,
             MaterialPageRoute(
               builder: (_) => const AddAccountScreen(),
    ),
  );

  if(result == true){
    setState(() {});
  }

},
      ),
    );
  }
}