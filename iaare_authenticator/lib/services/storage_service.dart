import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/account.dart';

class StorageService {

  static const String key="accounts";

  static Future<void> saveAccounts(List<Account> accounts) async{

    final prefs=await SharedPreferences.getInstance();

    final jsonList=accounts.map((e)=>jsonEncode(e.toJson())).toList();

    await prefs.setStringList(key,jsonList);

  }

  static Future<List<Account>> loadAccounts() async{

    final prefs=await SharedPreferences.getInstance();

    final list=prefs.getStringList(key);

    if(list==null) return [];

    return list.map((e)=>Account.fromJson(jsonDecode(e))).toList();

  }

}