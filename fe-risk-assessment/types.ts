import { Href } from "expo-router";
import { Icon } from "phosphor-react-native";
import React, { ReactNode } from "react";
import {
  TextInput,
  TextInputProps,
  TextProps,
  TextStyle,
  TouchableOpacityProps,
  ViewStyle,
} from "react-native";

export type ScreenWrapperProps = {
  style?: ViewStyle;
  children: React.ReactNode;
};
export type ModalWrapperProps = {
  style?: ViewStyle;
  children: React.ReactNode;
  bg?: string;
};
export type accountOptionType = {
  title: string;
  icon: React.ReactNode;
  bgColor: string;
  routeName?: any;
};

export type TypoProps = {
  size?: number;
  color?: string;
  fontWeight?: TextStyle["fontWeight"];
  children: any | null;
  style?: TextStyle;
  textProps?: TextProps;
};

export type IconComponent = React.ComponentType<{
  height?: number;
  width?: number;
  strokeWidth?: number;
  color?: string;
  fill?: string;
}>;

export type IconProps = {
  name: string;
  color?: string;
  size?: number;
  strokeWidth?: number;
  fill?: string;
};

export type HeaderProps = {
  title?: string;
  style?: ViewStyle;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
};

export type BackButtonProps = {
  style?: ViewStyle;
  iconSize?: number;
};

export type TransactionType = {
  id?: string;
  type: string;
  amount: number;
  category?: string;
  date: Date | string;
  description?: string;
  image?: any;
  uid?: string;
  walletId: string;
};

export type CategoryType = {
  label: string;
  value: string;
  icon: Icon;
  bgColor: string;
};
export type ExpenseCategoriesType = {
  [key: string]: CategoryType;
};

export type TransactionListType = {
  data: TransactionType[];
  title?: string;
  loading?: boolean;
  emptyListMessage?: string;
};

export type TransactionItemProps = {
  item: TransactionType;
  index: number;
  handleClick: Function;
};

export interface InputProps extends TextInputProps {
  icon?: React.ReactNode;
  endicon?: React.ReactNode;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
  inputRef?: React.RefObject<TextInput>;
}

export interface CustomButtonProps extends TouchableOpacityProps {
  style?: ViewStyle;
  onPress?: () => void;
  loading?: boolean;
  children: React.ReactNode;
}

export type ImageUploadProps = {
  file?: any;
  onSelect: (file: any) => void;
  onClear: () => void;
  containerStyle?: ViewStyle;
  imageStyle?: ViewStyle;
  placeholder?: string;
};

export type UserType = {
  uid?: string;
  email?: string | null;
  firstName: string | null;
  lastName: string | null;
} | null;

export type UserDataType = {
  name: string;
  image?: any;
};

export type AuthContextType = {
  user: UserType;
  setUser: Function;
  results: SearchResult;
  setResults: Function;
  login: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
  register: (
    firstName: string,
    lastName: string,
    email: string,
    password: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
  search: (
    search: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
  userDetails: (
    email: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
  updateUser: (
    firstName: string,
    lastName: string,
    email: string,
    oldPassword: string,
    newPassword: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
  forgotPassword: (
    email: string
  ) => Promise<{ success: boolean; msg?: any; status_code?: number }>;
};

export type ResponseType = {
  success: boolean;
  data?: any;
  msg?: string;
};

export type WalletType = {
  id?: string;
  name: string;
  amount?: number;
  totalIncome?: number;
  totalExpenses?: number;
  image: any;
  uid?: string;
  created?: Date;
};

export type SearchResult = {
  Address: Array<any>;
  "Birth Place": Array<any>;
  "Business Phone": Array<any>;
  "Credit Card": Array<any>;
  DDL: Array<any>;
  DoB: Array<any>;
  Education: Array<any>;
  Email: Array<any>;
  Employer: Array<any>;
  "Facebook Account": Array<any>;
  Gender: Array<any>;
  "Instagram Account": Array<any>;
  Location: Array<any>;
  Name: Array<any>;
  "Passport #": Array<any>;
  "Personal Cell": Array<any>;
  Phone: Array<any>;
  SSN: Array<any>;
  "Twitter Account": Array<any>;
  risk_level: string;
  risk_score: number;
};
