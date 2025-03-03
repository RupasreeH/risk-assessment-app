import { StyleSheet, Text, View } from "react-native";
import React from "react";
import ScreenWrapper from "@/components/ScreenWrapper";
import BackButton from "@/components/BackButton";
import Typo from "@/components/Typo";
import Header from "@/components/Header";
import { spacingY } from "@/constants/theme";
import ModalWrapper from "@/components/ModalWrapper";

const Policy = () => {
  return (
    <ModalWrapper>
      <View style={styles.container}>
        <Header
          title="Privacy Policy"
          leftIcon={<BackButton />}
          style={{ marginBottom: spacingY._10 }}
        />
        <Typo style={{ textAlign: "left", paddingBottom: 5 }} size={20}>
          Introduction
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          Our Risk assessment app analyzes publicly available data for
          Personally Identifiable Information (PII) to assess potential privacy
          risks.
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          We are committed to protecting users data which is collected while
          Sign up and ensuring compliance with relevant privacy laws.
        </Typo>
        <Typo
          style={{ textAlign: "left", paddingTop: 13, paddingBottom: 5 }}
          size={20}
        >
          Data Collection
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          The app scans the Google search engine for PII such as names, emails,
          phone numbers, and addresses.Only User signup Data is stored.
        </Typo>
    
        <Typo style={{ textAlign: "left" }} size={16}>
          Basic user information is collected only when User signup the
          application.
        </Typo>
        <Typo
          style={{ textAlign: "left", paddingTop: 13, paddingBottom: 5 }}
          size={20}
        >
          Data Processing & Usage
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          Collected PII is processed solely for risk assessment purposes.
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          We do not sell, share, or use data for marketing.
        </Typo>
        <Typo
          style={{ textAlign: "left", paddingTop: 13, paddingBottom: 5 }}
          size={20}
        >
          Data Storage & Security
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          We are not saving any of the PII data which our app fetches.
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          Only basic information given by the user while signup the application
          is stored and passwords are Hashed.
        </Typo>
        <Typo
          style={{ textAlign: "left", paddingTop: 13, paddingBottom: 5 }}
          size={20}
        >
          User Rights & Compliance
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          Users can request access or deletion of their data.
        </Typo>
        <Typo style={{ textAlign: "left" }} size={16}>
          The app complies with GDPR, CCPA, and relevant privacy laws.
        </Typo>
      </View>
    </ModalWrapper>
  );
};

export default Policy;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    padding: 10,
  },
});
