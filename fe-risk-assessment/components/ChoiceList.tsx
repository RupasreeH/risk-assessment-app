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
      el.title === item.title ? { ...el, value: !el.value } : el
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
              {item.description}
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
      {checkBoxList?.length <= 0 && (
        <Typo fontWeight={"700"} color={colors.black} size={15}>
          No Data Found.
        </Typo>
      )}
      {checkBoxList?.length > 0 &&
        checkBoxList.map((item, index) => (
          <CheckBox
            key={index}
            checked={item.value}
            title={getLabel(item)}
            onPress={() => handlePress(item)}
            containerStyle={{
              alignItems: "flex-start",
              backgroundColor: "transparent",
              borderWidth: 0,
            }}
          />
        ))}
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
