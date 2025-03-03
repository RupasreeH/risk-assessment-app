import { Alert, ScrollView, StyleSheet, View } from "react-native";
import React, { useState } from "react";
import ModalWrapper from "@/components/ModalWrapper";
import { colors, spacingX, spacingY } from "@/constants/theme";
import Header from "@/components/Header";
import BackButton from "@/components/BackButton";
import { Image } from "expo-image";
import { scale, verticalScale } from "@/utils/styling";
import Typo from "@/components/Typo";
import Input from "@/components/Input";
import { useAuth } from "@/context/authContext";
import Button from "@/components/Button";
import { UserType } from "@/types";

const ProfileModal = () => {
  const { setUser, user, updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState<any>(user);
  const onSubmit = async () => {
    if (!userData.email || !userData.firstName || !userData.lastName) {
      Alert.alert("User Update", "Please fill all the fields");
      return;
    }

    if (userData.oldPassword && !userData.newPassword) {
      Alert.alert("User Update", "Please enter new password");
      return;
    }
    setLoading(true);
    const res = await updateUser(
      userData.firstName,
      userData.lastName,
      userData.email,
      userData.oldPassword,
      userData.newPassword
    );
    setLoading(false);

    if (!res.success) {
      Alert.alert("User Update", res.msg);
      return;
    }
    if (res.success && res.status_code !== 200) {
      Alert.alert("User Update", res.msg.message);
      return;
    }

    const user: UserType = res?.msg?.user ? res?.msg?.user : null;
    if (!user) {
      Alert.alert(
        "User Update",
        "Something went wrong please try after some time"
      );
      return;
    }
    setUser({
      uid: user.uid,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
    });
    Alert.alert("User Update", "User updated successfully");
    return;
  };
  return (
    <ModalWrapper>
      <View style={styles.container}>
        <Header
          title="Update Profile"
          leftIcon={<BackButton />}
          style={{ marginBottom: spacingY._10 }}
        />
        <ScrollView contentContainerStyle={styles.form}>
          <View style={styles.avatarContainer}>
            <Image
              source={require("../../assets/images/defaultAvatar.png")}
              style={styles.avatar}
              contentFit="cover"
              transition={100}
            />
          </View>
          <View style={styles.inputContainer}>
            <Typo color={colors.black}>First Name</Typo>
            <Input
              placeholder="First Name"
              value={userData?.firstName}
              onChangeText={(value) => {
                setUserData({ ...userData, firstName: value });
              }}
            />
            <Typo color={colors.black}>Last Name</Typo>
            <Input
              placeholder="Last Name"
              value={userData?.lastName}
              onChangeText={(value) => {
                setUserData({ ...userData, lastName: value });
              }}
            />
            <Typo color={colors.black}>Old Password</Typo>
            <Input
              placeholder="Old Password"
              value={userData?.oldPassword}
              secureTextEntry
              onChangeText={(value) => {
                setUserData({ ...userData, oldPassword: value });
              }}
            />
            <Typo color={colors.black}>New Password</Typo>
            <Input
              placeholder="New Password"
              secureTextEntry
              value={userData?.newPassword}
              onChangeText={(value) => {
                setUserData({ ...userData, newPassword: value });
              }}
            />
          </View>
        </ScrollView>
      </View>
      <View style={styles.footer}>
        <Button onPress={onSubmit} loading={loading} style={{ flex: 1 }}>
          <Typo color={colors.white} fontWeight={"700"}>
            Update
          </Typo>
        </Button>
      </View>
    </ModalWrapper>
  );
};

export default ProfileModal;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-between",
    paddingHorizontal: spacingY._20,
  },
  form: {
    gap: spacingY._30,
    marginTop: spacingY._15,
  },
  avatarContainer: {
    position: "relative",
    alignSelf: "center",
  },
  avatar: {
    alignItems: "center",
    backgroundColor: colors.neutral300,
    height: verticalScale(135),
    width: verticalScale(135),
    borderRadius: 200,
  },
  inputContainer: {
    gap: spacingY._5,
  },
  footer: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "center",
    paddingHorizontal: spacingX._20,
    gap: scale(12),
    paddingTop: spacingY._15,
    borderTopColor: colors.neutral200,
    marginBottom: spacingY._5,
    borderTopWidth: 1,
  },
});
