import { Alert, ScrollView, StyleSheet, View } from "react-native";
import React, { useEffect, useState } from "react";
import { colors, spacingX, spacingY } from "@/constants/theme";
import { scale, verticalScale } from "@/utils/styling";
import ModalWrapper from "@/components/ModalWrapper";
import Typo from "@/components/Typo";
import Button from "@/components/Button";
import Header from "@/components/Header";
import BackButton from "@/components/BackButton";
import Input from "@/components/Input";
import { useAuth } from "@/context/authContext";
import { UserType } from "@/types";

const AddUserModal = () => {
  const { updateSearchUsers, getSearchNames, setUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<string[]>([]);
  const [disableUsers, setDisableUsers] = useState<string[]>([]);
  useEffect(() => {
    if (users.length <= 0) {
      const userList = getSearchNames();
      setUsers(userList);
      setDisableUsers(userList);
    }
  });
  const onSubmit = async () => {
    setLoading(true);
    const userList = users.slice(1);
    const res = await updateSearchUsers(userList ? userList?.join(",") : "");
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
      searchNames: user.searchNames,
    });
    Alert.alert("User Update", "User updated successfully");
    return;
  };

  const onChangeText = (value: string, index: number) => {
    const updatedUsers = [...users];
    updatedUsers[index] = value;
    setUsers(updatedUsers);
  };

  return (
    <ModalWrapper>
      <View style={styles.container}>
        <Header
          title="Add Search Users"
          leftIcon={<BackButton />}
          style={{ marginBottom: spacingY._10 }}
        />
        <ScrollView contentContainerStyle={styles.form}>
          <View>
            <View>
              <Typo size={12} fontWeight={"600"} color="red">
                Please enter each user's full name correctly. Once a name is
                added, it cannot be changed.
              </Typo>
            </View>
          </View>
          <View style={styles.inputContainer}>
            <Typo color={colors.black}>User 1</Typo>
            <Input
              placeholder="Enter User 1 Full Name"
              editable={disableUsers[1] ? false : true}
              value={users[1] ? users[1] : ""}
              onChangeText={(value) => onChangeText(value, 1)}
            />
            <Typo color={colors.black}>User 2</Typo>
            <Input
              placeholder="Enter User 2 Full Name"
              editable={disableUsers[2] ? false : true}
              value={users[2] ? users[2] : ""}
              onChangeText={(value) => onChangeText(value, 2)}
            />
            <Typo color={colors.black}>User 3</Typo>
            <Input
              placeholder="Enter User 3 Full Name"
              editable={disableUsers[3] ? false : true}
              value={users[3] ? users[3] : ""}
              onChangeText={(value) => onChangeText(value, 3)}
            />
            <Typo color={colors.black}>User 4</Typo>
            <Input
              placeholder="Enter User 4 Full Name"
              editable={disableUsers[4] ? false : true}
              value={users[4] ? users[4] : ""}
              onChangeText={(value) => onChangeText(value, 4)}
            />
          </View>
        </ScrollView>
      </View>
      <View style={styles.footer}>
        <Button onPress={onSubmit} loading={loading} style={{ flex: 1 }}>
          <Typo color={colors.white} fontWeight={"500"} size={15}>
            Update
          </Typo>
        </Button>
      </View>
    </ModalWrapper>
  );
};

export default AddUserModal;

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
