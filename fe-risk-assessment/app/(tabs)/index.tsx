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

const Home = () => {
  const [isLoading, setIsloading] = useState(false);
  const { search, results, setResults } = useAuth();
  const searchRef = useRef("");
  const router = useRouter();

  const handleSearch = async () => {
    setResults(null);
    setIsloading(true);
    const res = await search(searchRef.current);
    setResults(res.msg);
    setIsloading(false);
  };

  return (
    <ScreenWrapper>
      <View style={styles.container}>
        <Input
          placeholder="Enter name"
          onChangeText={(value) => (searchRef.current = value)}
          editable={!isLoading}
          endicon={
            <View
              style={[
                styles.endIcon,
                {
                  backgroundColor: isLoading
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
      {isLoading && <Loading showSuggestions={true} />}
      {results && (
        <View style={styles.container}>
          <GaugeMeter
            percentage={results.risk_score}
            score={results.risk_level}
            size={300}
          />
        </View>
      )}
      {results && (
        <View style={{ padding: 10 }}>
          <Button loading={isLoading} onPress={() => router.push("/details")}>
            <Typo fontWeight={"700"} color={colors.white} size={21}>
              More Details
            </Typo>
          </Button>
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
  endIcon: {
    padding: 21,
    borderTopRightRadius: radius._17,
    borderBottomRightRadius: radius._17,
    position: "absolute",
    right: 0,
  },
});

export default Home;
