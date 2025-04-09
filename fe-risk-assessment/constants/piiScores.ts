// disclosure weight measures of each PII
export const PII_Weight = {
  Name: 1,
  Address: 1,
  DoB: 2,
  "Birth Place": 2,
  Email: 0.1,
  Phone: 0.5,
  "Business Phone:": 0.1,
  "Facebook Account": 1,
  "Twitter Account": 0.1,
  "Instagram Account": 0.1,
  DDL: 2,
  "Passport #": 2,
  "Credit Card": 2,
  SSN: 10,
};

// disclosure willingness measure of each PII
export const PII_Willingness = {
  "Business Phone:": 1,
  "Facebook Account": 1,
  "Twitter Account": 1,
  "Instagram Account": 1,
  Name: 0.6,
  DoB: 0.57,
  Phone: 0.12,
  Email: 0.1,
  Address: 0.034,
  "Birth Place": 0.01,
  DDL: 0.01,
  "Passport #": 0.01,
  "Credit Card": 0.01,
  SSN: 0.001,
};
