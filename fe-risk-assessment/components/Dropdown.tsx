import { View, StyleSheet } from "react-native";
import { Dropdown as RNDropdown } from "react-native-element-dropdown";
import { Option } from "@/types";
import React, { useState } from "react";

interface Props {
  data: Option[];
  onChange?: (item: Option) => void;
  disable?: boolean;
  value: string | null;
  placeholder: string;
  searchPlaceholder: string;
}

const Dropdown = ({
  data,
  onChange,
  disable,
  value,
  placeholder,
  searchPlaceholder,
}: Props) => {
  const [dropdownValue, setDropdownValue] = useState<string | null>(value);
  const onDropdownChange = (item: Option) => {
    setDropdownValue(item.value);
    onChange && onChange(item);
  };

  return (
    <View>
      <RNDropdown
        style={styles.dropdown}
        placeholderStyle={styles.placeholderStyle}
        selectedTextStyle={styles.selectedTextStyle}
        inputSearchStyle={styles.inputSearchStyle}
        iconStyle={styles.iconStyle}
        data={data}
        search
        disable={disable}
        maxHeight={300}
        labelField="label"
        valueField="value"
        placeholder={placeholder}
        searchPlaceholder={searchPlaceholder}
        value={dropdownValue}
        onChange={onDropdownChange}
      />
    </View>
  );
};

export default Dropdown;

const styles = StyleSheet.create({
  dropdown: {
    margin: 5,
    height: 50,
    borderBottomColor: "gray",
    borderBottomWidth: 0.5,
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  icon: {
    marginRight: 5,
  },
  placeholderStyle: {
    fontSize: 16,
  },
  selectedTextStyle: {
    fontSize: 16,
  },
  iconStyle: {
    width: 20,
    height: 20,
  },
  inputSearchStyle: {
    height: 40,
    fontSize: 16,
  },
});
