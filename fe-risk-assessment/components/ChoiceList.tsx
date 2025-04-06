import { View, StyleSheet, ScrollView } from "react-native";
import React, { useState } from "react";
import { Choice, ChoiceListProps } from "@/types";
import { CheckBox } from "@rneui/themed";
import Typo from "./Typo";
import { colors } from "@/constants/theme";

const ChoiceList = ({ list, onPress }: ChoiceListProps) => {
  const [checkBoxList, setCheckBoxList] = useState(list);
  const handlePress = (item: Choice) => {
    const updatedList = checkBoxList.map((el) =>
      el.url === item.url ? { ...el, value: !el.value } : el
    );
    setCheckBoxList(updatedList);
    onPress(item);
  };

  const getLabel = (item: Choice) => {
    return (
      <View>
        {item.title && (
          <>
            <Typo fontWeight={"700"} color={colors.black} size={12}>
              Title:
            </Typo>
            <Typo color={colors.black} size={12}>
              {item.title}
            </Typo>
          </>
        )}
        {item.description && (
          <>
            <Typo fontWeight={"700"} color={colors.black} size={12}>
              Description:
            </Typo>
            <Typo color={colors.black} size={12}>
              {item.description.replace(/\s+/g, " ").trim()}
            </Typo>
          </>
        )}
        {item.url && (
          <>
            <Typo fontWeight={"700"} color={colors.black} size={12}>
              Url:
            </Typo>
            <Typo color={colors.black} size={12}>
              {item.url}
            </Typo>
          </>
        )}
      </View>
    );
  };
  return (
    <ScrollView>
      <View style={{ borderWidth: 1, borderColor: "transparent" }}>
        {checkBoxList.map((item, index) => (
          <CheckBox
            key={index}
            checked={item.value}
            title={getLabel(item)}
            onPress={() => handlePress(item)}
            containerStyle={{
              alignItems: "flex-start",
              backgroundColor: "transparent",
              borderWidth: 0,
              marginBottom: 10,
              padding: 0,
              marginTop: 0,
              marginLeft: 0,
            }}
          />
        ))}
      </View>
    </ScrollView>
  );
};

export default ChoiceList;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "transparent",
    justifyContent: "flex-start",
    alignItems: "flex-start",
    position: "relative",
  },
});
