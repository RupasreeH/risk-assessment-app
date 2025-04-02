import { View, StyleSheet } from "react-native";
import React, { useState } from "react";
import { Choice, ChoiceListProps } from "@/types";
import { CheckBox } from "@rneui/themed";

const ChoiceList = ({ list, onPress }: ChoiceListProps) => {
  const [checkBoxList, setCheckBoxList] = useState(list);
  const handlePress = (item: Choice) => {
    const updatedList = checkBoxList.map((el) =>
      el.label === item.label ? { ...el, value: !el.value } : el
    );
    setCheckBoxList(updatedList);
    onPress(item);
  };
  return (
    <View style={styles.container}>
      {checkBoxList.map((item, index) => (
        <CheckBox
          key={index}
          checked={item.value}
          title={item.label}
          onPress={() => handlePress(item)}
          containerStyle={{
            alignItems: "flex-start",
            backgroundColor: "transparent",
            borderWidth: 0,
          }}
        />
      ))}
    </View>
  );
};

export default ChoiceList;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "transparent",
    justifyContent: "flex-start",
    alignItems: "flex-start",
    position: "relative",
    marginBottom: 10,
  },
});
