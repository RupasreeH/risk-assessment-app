import { Alert, Pressable, StyleSheet, Text, View } from "react-native";
import React, { useRef, useState } from "react";
import ScreenWrapper from "@/components/ScreenWrapper";
import Typo from "@/components/Typo";
import { colors, spacingX, spacingY } from "@/constants/theme";
import { verticalScale } from "@/utils/styling";
import BackButton from "@/components/BackButton";
import Input from "@/components/Input";
import * as Icons from "phosphor-react-native";
import Button from "@/components/Button";
import { useRouter } from "expo-router";
import { useAuth } from "@/context/authContext";
import { UserType } from "@/types";
import { CheckBox } from "@rneui/themed";

const Register = () => {
  const emailRef = useRef("");
  const passwordRef = useRef("");
  const firstNameRef = useRef("");
  const lastNameRef = useRef("");
  const [isLoading, setIsloading] = useState(false);
  const [checked, setChecked] = useState<boolean>(false);
  const { register: registerUser, setUser } = useAuth();

  const router = useRouter();

  const handleSubmit = async () => {
    if (
      !emailRef.current ||
      !passwordRef.current ||
      !firstNameRef.current ||
      !lastNameRef.current
    ) {
      Alert.alert("Sign up", "Please fill all the fields");
      return;
    }

    setIsloading(true);
    const res = await registerUser(
      firstNameRef.current,
      lastNameRef.current,
      emailRef.current,
      passwordRef.current
    );
    setIsloading(false);

    if (!res.success) {
      Alert.alert("Sign up", res.msg);
      return;
    }
    if (res.success && res.status_code !== 200) {
      Alert.alert("Sign up", res.msg.message);
      return;
    }

    const user: UserType = res?.msg?.user ? res?.msg?.user : null;
    if (!user) {
      Alert.alert("Sign up", "Something went wrong please try after some time");
      return;
    }

    setUser({
      uid: user.uid,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
    });
  };
  return (
    <ScreenWrapper>
      <View style={styles.container}>
        {/* Back button */}
        <BackButton iconSize={28} />
        <View style={{ gap: 5, marginTop: spacingY._5 }}>
          <Typo size={30} fontWeight={"800"}>
            Let's,
          </Typo>
          <Typo size={30} fontWeight={"800"}>
            Get Started
          </Typo>
        </View>

        {/* Register form */}
        <View style={styles.form}>
          <Typo size={16} color={colors.textLight}>
            Create an account to tract your risk score
          </Typo>
          <Input
            placeholder="Enter your first name"
            onChangeText={(value) => (firstNameRef.current = value)}
            icon={
              <Icons.User
                size={verticalScale(26)}
                color={colors.neutral300}
                weight="fill"
              />
            }
          />
          <Input
            placeholder="Enter your last name"
            onChangeText={(value) => (lastNameRef.current = value)}
            icon={
              <Icons.User
                size={verticalScale(26)}
                color={colors.neutral300}
                weight="fill"
              />
            }
          />
          <Input
            placeholder="Enter your email"
            onChangeText={(value) => (emailRef.current = value)}
            icon={
              <Icons.At
                size={verticalScale(26)}
                color={colors.neutral300}
                weight="fill"
              />
            }
          />
          <Input
            placeholder="Enter your password"
            secureTextEntry
            onChangeText={(value) => (passwordRef.current = value)}
            icon={
              <Icons.Lock
                size={verticalScale(26)}
                color={colors.neutral300}
                weight="fill"
              />
            }
          />
          <CheckBox
            title={
              <View>
                <Typo size={14}>
                  Yes, I agree to the terms of services and{" "}
                </Typo>
                <Pressable onPress={() => router.push("/(details)/policy")}>
                  <Typo
                    size={14}
                    color={colors.primary}
                    style={{ padding: 0, margin: 0, top: 0 }}
                  >
                    Privacy policy
                  </Typo>
                </Pressable>
              </View>
            }
            checked={checked}
            onPress={() => setChecked(!checked)}
          />
          <Button
            loading={isLoading}
            onPress={handleSubmit}
            disabled={!checked}
          >
            <Typo fontWeight={"700"} color={colors.white} size={21}>
              Sign Up
            </Typo>
          </Button>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Typo size={15}>Already have an account?</Typo>
          <Pressable onPress={() => router.push("/(auth)/login")}>
            <Typo size={15} fontWeight={"700"} color={colors.primary}>
              Login
            </Typo>
          </Pressable>
        </View>
      </View>
    </ScreenWrapper>
  );
};

export default Register;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    gap: spacingY._30,
    paddingHorizontal: spacingX._20,
  },
  welcomeText: {
    fontSize: verticalScale(20),
    fontWeight: "bold",
    color: colors.text,
  },
  form: {
    gap: spacingY._10,
  },
  forgotPassword: {
    textAlign: "right",
    fontWeight: "500",
    color: colors.text,
  },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    alignContent: "center",
    gap: 5,
  },
  footerText: {
    textAlign: "center",
    color: colors.text,
    fontSize: verticalScale(15),
  },
});
