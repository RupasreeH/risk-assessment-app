import { StyleSheet, Text, View } from "react-native";
import React from "react";
import Button from "@/components/Button";
import Typo from "@/components/Typo";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/authContext";
import ScreenWrapper from "@/components/ScreenWrapper";

const Profile = () => {
  const { setUser } = useAuth();
  const handleLogout = () => {
    setUser(null);
  };
  return (
    <ScreenWrapper>
      <Typo>Profile</Typo>
      <Button onPress={handleLogout}>
        <Typo color={colors.white}>Logout</Typo>
      </Button>
    </ScreenWrapper>
  );
};

export default Profile;

const styles = StyleSheet.create({});
