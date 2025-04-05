import { StyleSheet, Text, TextInput, View } from "react-native";
import React from "react";
import { InputProps } from "@/types";
import { colors, radius, spacingX } from "@/constants/theme";
import { verticalScale } from "@/utils/styling";

const Input = (props: InputProps) => {
  return (
    <View
      style={[
        styles.container,
        props.containerStyle && props.containerStyle,
        props.editable === false ? { backgroundColor: colors.neutral200 } : {},
      ]}
    >
      {props.icon && props.icon}
      <TextInput
        style={[styles.input, props.inputStyle]}
        placeholderTextColor={colors.neutral400}
        ref={props.inputRef && props.inputRef}
        {...props}
      />
      {props.endicon && props.endicon}
    </View>
  );
};

export default Input;

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    height: verticalScale(40),
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.neutral500,
    borderRadius: radius._10,
    borderCurve: "continuous",
    paddingHorizontal: spacingX._15,
    gap: spacingX._10,
  },
  input: {
    flex: 1,
    color: colors.text,
    fontSize: verticalScale(14),
  },
});
