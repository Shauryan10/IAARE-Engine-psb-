class Account {

  String id;

  String issuer;

  String accountName;

  String secret;

  Account({
    required this.id,
    required this.issuer,
    required this.accountName,
    required this.secret,
  });

  Map<String,dynamic> toJson() => {
    "id": id,
    "issuer": issuer,
    "accountName": accountName,
    "secret": secret
  };

  factory Account.fromJson(Map<String,dynamic> json){

    return Account(
      id: json["id"],
      issuer: json["issuer"],
      accountName: json["accountName"],
      secret: json["secret"],
    );

  }

}