import { View, StyleSheet } from "react-native";
import React, { useEffect, useState } from "react";
import Typo from "./Typo";
import { useAuth } from "@/context/authContext";
import {
  beta_coefficients,
  resolution_powers,
  weights,
  willingness_measures,
} from "@/constants/piiScores";
import { colors } from "@/constants/theme";

const Suggestions = () => {
  const { results }: any = useAuth();
  const [informationText, setInformationText] = useState<any[]>([]);
  const levels = ["very low", "low", "medium", "high", "critical"];
  const [nextLevel, setNextLevel] = useState<string>(
    levels[levels.indexOf(results.risk_level.toLowerCase()) + 1]
  );

  const calculatePrivacyScore = (
    willingnessMeasure: number,
    resolutionPower: number,
    betaCoefficient: number
  ) => {
    const privacyScore =
      1 /
      Math.exp(betaCoefficient * (1 - willingnessMeasure) * resolutionPower);
    return privacyScore;
  };

  useEffect(() => {
    if (!results) return;
    const emptyFields = Object.keys(results).filter(
      (key: string) => results[key]?.length === 0
    );
    let information: any[] = [];
    emptyFields.forEach((key: string) => {
      if (key === "Phone") {
        return;
      }
      const weight = weights[key as keyof typeof weights];
      const willingness =
        willingness_measures[key as keyof typeof willingness_measures];
      const resolutionPower =
        resolution_powers[key as keyof typeof resolution_powers]; // Assuming a constant resolution power for simplicity
      const betaCoefficient =
        beta_coefficients[key as keyof typeof beta_coefficients]; // Assuming a constant beta coefficient for simplicity
      const privacyScore = calculatePrivacyScore(
        willingness,
        resolutionPower,
        betaCoefficient
      );
      information.push({
        key: key,
        score: weight * privacyScore,
      });
    });

    setInformationText(information.sort((a, b) => a.score - b.score));
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
        fontWeight={"500"}
        style={{
          marginBottom: 10,
        }}
      >
        Disclosing any of the following, along with their individual risk
        scores, may elevate your risk profile.
      </Typo>
      <View style={{ flexDirection: "column", flexWrap: "wrap" }}>
        {informationText.length > 0 &&
          informationText.map((item: string, index: number) => (
            <View
              style={{
                display: "flex",
                flexDirection: "row",
                borderWidth: 0,
                width: "100%",
                marginBottom: 5,
                paddingTop: 5,
              }}
              key={index}
            >
              <Typo size={12} fontWeight={"700"} style={{ marginRight: 5 }}>
                {`${informationText[index].key} : `}
              </Typo>
              <Typo size={12} style={{ marginRight: 5 }}>
                {informationText[index].score.toFixed(2)}
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
