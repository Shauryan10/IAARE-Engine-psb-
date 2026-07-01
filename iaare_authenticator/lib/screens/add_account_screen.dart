import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';

import '../models/account.dart';
import '../services/storage_service.dart';

class AddAccountScreen extends StatefulWidget {
  const AddAccountScreen({super.key});

  @override
  State<AddAccountScreen> createState() => _AddAccountScreenState();
}

class _AddAccountScreenState extends State<AddAccountScreen> {
  final _formKey = GlobalKey<FormState>();

  final issuerController = TextEditingController();
  final accountController = TextEditingController();
  final secretController = TextEditingController();

  bool isSaving = false;

  Future<void> saveAccount() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      isSaving = true;
    });

    final accounts = await StorageService.loadAccounts();

    accounts.add(
      Account(
        id: const Uuid().v4(),
        issuer: issuerController.text.trim(),
        accountName: accountController.text.trim(),
        secret: secretController.text.trim(),
      ),
    );

    await StorageService.saveAccounts(accounts);

    if (!mounted) return;

    Navigator.pop(context, true);
  }

  @override
  void dispose() {
    issuerController.dispose();
    accountController.dispose();
    secretController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const primaryRed = Color(0xFFC8102E);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Add Account"),
        backgroundColor: primaryRed,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            children: [

              TextFormField(
                controller: issuerController,
                decoration: const InputDecoration(
                  labelText: "Issuer",
                  border: OutlineInputBorder(),
                ),
                validator: (value) =>
                    value!.isEmpty ? "Issuer is required" : null,
              ),

              const SizedBox(height: 20),

              TextFormField(
                controller: accountController,
                decoration: const InputDecoration(
                  labelText: "Account Name",
                  border: OutlineInputBorder(),
                ),
                validator: (value) =>
                    value!.isEmpty ? "Account name is required" : null,
              ),

              const SizedBox(height: 20),

              TextFormField(
                controller: secretController,
                decoration: const InputDecoration(
                  labelText: "Secret Key",
                  border: OutlineInputBorder(),
                ),
                validator: (value) =>
                    value!.isEmpty ? "Secret key is required" : null,
              ),

              const SizedBox(height: 35),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primaryRed,
                  ),
                  onPressed: isSaving ? null : saveAccount,
                  child: Text(
                    isSaving ? "Saving..." : "Save Account",
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}