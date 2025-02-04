import { StyleSheet, Text, View } from "react-native";
import React from "react";
import ScreenWrapper from "@/components/ScreenWrapper";
import BackButton from "@/components/BackButton";
import Typo from "@/components/Typo";

const Policy = () => {
  return (
    <ScreenWrapper>
      <View style={styles.container}>
        <BackButton iconSize={28} />
        <Typo style={{ textAlign: "center" }} size={30} fontWeight={"800"}>
          Privacy Policy
        </Typo>
      </View>
    </ScreenWrapper>
  );
};

export default Policy;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    padding: 10,
  },
});
