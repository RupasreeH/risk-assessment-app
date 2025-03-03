import { Alert, StyleSheet, Text, View } from "react-native";
import React, { useState } from "react";
import ModalWrapper from "@/components/ModalWrapper";
import Header from "@/components/Header";
import BackButton from "@/components/BackButton";
import { colors, spacingY } from "@/constants/theme";
import Typo from "@/components/Typo";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { UserType } from "@/types";
import { useAuth } from "@/context/authContext";
import { useRouter } from "expo-router";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const { forgotPassword } = useAuth();
  const router = useRouter();
  const onSubmit = async () => {
    if (!email) {
      Alert.alert("Forgot Password", "Please enter email");
      return;
    }

    setLoading(true);
    const res = await forgotPassword(email);
    setLoading(false);

    if (!res.success) {
      Alert.alert("Forgot Password", res.msg);
      return;
    }

    if (res.success && res.status_code !== 200) {
      Alert.alert("Forgot Password", res.msg.message);
      return;
    }
    Alert.alert("Forgot Password", res.msg.message);
    setEmail("");
    router.replace("/(auth)/login");
  };
  return (
    <ModalWrapper>
      <View style={styles.container}>
        <Header
          title="Forgot Password"
          leftIcon={<BackButton />}
          style={{ marginBottom: spacingY._10 }}
        />
        <View style={[styles.inputContainer, { flex: 1, marginTop: "50%" }]}>
          <Typo color={colors.black}>Email</Typo>
          <Input
            placeholder="Email"
            value={email}
            onChangeText={(value) => {
              setEmail(value);
            }}
          />
          <Button onPress={onSubmit} loading={loading}>
            <Typo color={colors.white} fontWeight={"700"}>
              Submit
            </Typo>
          </Button>
        </View>
      </View>
    </ModalWrapper>
  );
};

export default ForgotPassword;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: spacingY._20,
  },
  inputContainer: {
    gap: spacingY._5,
  },
});
