import React, { useRef, useState } from "react";

import ScreenWrapper from "@/components/ScreenWrapper";
import GaugeMeter from "@/components/Gauge";
import { View, StyleSheet, Pressable } from "react-native";
import Input from "@/components/Input";
import * as Icons from "phosphor-react-native";
import { verticalScale } from "@/utils/styling";
import { colors, radius } from "@/constants/theme";
import { useAuth } from "@/context/authContext";
import Loading from "@/components/Loading";
import { useRouter } from "expo-router";
import Button from "@/components/Button";
import Typo from "@/components/Typo";
import { Choice } from "@/types";
import ChoiceList from "@/components/ChoiceList";

const Home = () => {
  const [isLoading, setIsloading] = useState(false);
  const { search, results, setResults, extract } = useAuth();
  const searchRef = useRef("");
  const router = useRouter();
  const [showCheckBox, setShowCheckBox] = useState(false);
  const [checkBoxList, setCheckBoxList] = useState([]);
  const [selectUrlList, setSelectUrlList] = useState<string[]>([]);
  const [disableInput, setDisableInput] = useState(false);

  const prepareCheckBoxList = (results: any) => {
    if (!results || !results.webpages || results.webpages.length <= 0) {
      return [];
    }
    return results.webpages.map((result: any) => ({
      ...result,
      value: false,
    }));
  };

  const handleSearch = async () => {
    setResults(null);
    setIsloading(true);
    setDisableInput(true);
    const res = await search(searchRef.current);
    setCheckBoxList(prepareCheckBoxList(res.msg));
    setShowCheckBox(true);
    setIsloading(false);
  };

  const handleChoice = (item: Choice) => {
    setSelectUrlList((prevList) =>
      item.value === false
        ? [...prevList, item.url]
        : prevList.filter((url) => item.url !== url)
    );
  };

  const handleSubmit = async () => {
    setShowCheckBox(false);
    setResults(null);
    setIsloading(true);
    const res = await extract(searchRef.current, selectUrlList);
    setResults(res.msg);
    setIsloading(false);
    setDisableInput(false);
  };

  return (
    <ScreenWrapper>
      <View style={styles.container}>
        <Input
          placeholder="Enter name"
          onChangeText={(value) => (searchRef.current = value)}
          editable={!disableInput}
          endicon={
            <View
              style={[
                styles.endIcon,
                {
                  backgroundColor: disableInput
                    ? colors.neutral400
                    : colors.primary,
                },
              ]}
            >
              <Pressable onPress={handleSearch}>
                <Icons.MagnifyingGlass
                  size={verticalScale(26)}
                  color={colors.white}
                  weight="fill"
                />
              </Pressable>
            </View>
          }
        />
      </View>
      {showCheckBox && (
        <View style={styles.checkBoxContainer}>
          <ChoiceList list={checkBoxList} onPress={handleChoice} />
          <Button loading={isLoading} onPress={handleSubmit}>
            <Typo fontWeight={"700"} color={colors.white} size={15}>
              Submit
            </Typo>
          </Button>
        </View>
      )}
      {isLoading && <Loading showSuggestions={true} />}
      {results?.risk_score > 0 && (
        <View style={styles.container}>
          <GaugeMeter
            percentage={results.risk_score}
            score={results.risk_level}
            size={300}
          />
        </View>
      )}
      {results?.risk_score > 0 && (
        <View style={{ padding: 10 }}>
          <Button loading={isLoading} onPress={() => router.push("/details")}>
            <Typo fontWeight={"700"} color={colors.white} size={21}>
              More Details
            </Typo>
          </Button>
        </View>
      )}
      {results?.risk_score === 0 && (
        <View
          style={{ flex: 1, justifyContent: "center", alignItems: "center" }}
        >
          <Typo fontWeight={"500"} color={colors.neutral500} size={25}>
            No Data Found
          </Typo>
        </View>
      )}
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
  },
  checkBoxContainer: {
    backgroundColor: "#ffffff",
    padding: 10,
    marginBottom: 150,
  },
  endIcon: {
    padding: 21,
    borderTopRightRadius: radius._17,
    borderBottomRightRadius: radius._17,
    position: "absolute",
    right: 0,
  },
});

export default Home;
