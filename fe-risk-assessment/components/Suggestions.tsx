import { View, StyleSheet } from "react-native";
import React, { useEffect, useState } from "react";
import Typo from "./Typo";
import { useAuth } from "@/context/authContext";
import { PII_Weight, PII_Willingness } from "@/constants/piiScores";
import { colors } from "@/constants/theme";

const Suggestions = () => {
  const { results }: any = useAuth();
  const [informationText, setInformationText] = useState<string[]>([]);
  const levels = ["very low", "low", "medium", "high", "critical"];
  const [nextLevel, setNextLevel] = useState<string>(
    levels[levels.indexOf(results.risk_level.toLowerCase()) + 1]
  );
  useEffect(() => {
    if (!results) return;
    const emptyFields = Object.keys(results).filter(
      (key: string) => results[key]?.length === 0
    );
    const willingnessObject = Object.keys(PII_Willingness).filter(
      (key: string) => emptyFields.find((efkey) => efkey === key)
    );
    let currentRiskScore = results.risk_score;
    let information: string[] = [];
    for (const key of willingnessObject) {
      const weight = PII_Weight[key as keyof typeof PII_Weight];
      currentRiskScore = currentRiskScore + weight;
      information.push(key);

      if (
        nextLevel === "very low" &&
        currentRiskScore > 2.74 &&
        currentRiskScore <= 5.58
      ) {
        break;
      } else if (
        nextLevel === "low" &&
        currentRiskScore > 5.58 &&
        currentRiskScore <= 6.87
      ) {
        break;
      } else if (
        nextLevel === "medium" &&
        currentRiskScore > 6.87 &&
        currentRiskScore <= 12.25
      ) {
        break;
      } else if (nextLevel === "high" && currentRiskScore > 12.25) {
        break;
      }
    }
    setInformationText(information);
  }, [results]);
  return (
    <View style={styles.container}>
      <Typo
        size={20}
        fontWeight={"700"}
        style={{ marginBottom: 10, color: colors.primary }}
      >
        User recommendations :
      </Typo>
      <Typo
        size={14}
        fontWeight={"700"}
        style={{
          marginBottom: 10,
        }}
      >
        Your risk score might increase to{" "}
        <Typo
          size={14}
          fontWeight={"700"}
          style={{
            color: colors[nextLevel.toLowerCase() as keyof typeof colors],
          }}
        >
          {nextLevel}
        </Typo>{" "}
        if you expose below information.
      </Typo>
      <View style={{ flexDirection: "column", flexWrap: "wrap" }}>
        {informationText.length > 0 &&
          informationText.map((item: string, index: number) => (
            <View
              style={{
                borderWidth: 0,
                width: "100%",
                marginBottom: 5,
                paddingTop: 5,
              }}
              key={index}
            >
              <Typo size={12} style={{ marginRight: 5 }} key={index}>
                {informationText[index]}
              </Typo>
            </View>
          ))}
      </View>
    </View>
  );
};

export default Suggestions;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    padding: 10,
  },
});
