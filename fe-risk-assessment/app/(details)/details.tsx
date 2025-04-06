import { StyleSheet, View } from "react-native";
import React from "react";
import Typo from "../../components/Typo";
import ScreenWrapper from "../../components/ScreenWrapper";
import BackButton from "@/components/BackButton";
import { useAuth } from "@/context/authContext";
import { ColorKeys, colors } from "@/constants/theme";

const Details = () => {
  const { results } = useAuth();
  const getColor = (key: ColorKeys) => {
    return colors[key];
  };
  return (
    <ScreenWrapper>
      <View style={styles.container}>
        <BackButton iconSize={28} />
        <Typo size={20} fontWeight={"800"} style={{ textAlign: "center" }}>
          Details found on internet
        </Typo>
        {results?.risk_level?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Risk Level
            </Typo>
            <Typo
              size={12}
              style={{
                backgroundColor: getColor(
                  results.risk_level.toLowerCase() as ColorKeys
                ),
                padding: 5,
                width: "20%",
                textAlign: "center",
                borderRadius: 5,
                color:
                  ["low", "medium"].indexOf(results.risk_level.toLowerCase()) >
                  -1
                    ? colors.black
                    : colors.white,
              }}
            >
              {results?.risk_level}
            </Typo>
          </View>
        )}
        {results?.risk_score > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Risk Score
            </Typo>
            <Typo size={12}>{results?.risk_score.toFixed(2)}</Typo>
          </View>
        )}
        {results?.Name?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Name
            </Typo>
            <Typo size={12}>{results?.Name?.join("\n")}</Typo>
          </View>
        )}
        {results?.Gender?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Gender
            </Typo>
            <Typo size={12}>{results?.Gender?.join("\n")}</Typo>
          </View>
        )}
        {results?.Email?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Email
            </Typo>
            <Typo size={12}>{results?.Email?.join("\n")}</Typo>
          </View>
        )}
        {results?.DoB?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Date of Birth
            </Typo>
            <Typo size={12}>{results?.DoB?.join("\n")}</Typo>
          </View>
        )}
        {results?.Education?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Education
            </Typo>
            <Typo size={12}>{results?.Education?.join("\n")}</Typo>
          </View>
        )}
        {results?.Phone?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Phone
            </Typo>
            <Typo size={12}>{results?.Phone?.join("\n")}</Typo>
          </View>
        )}
        {results?.Address?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Address
            </Typo>
            <Typo size={12}>{results.Address.join("\n")}</Typo>
          </View>
        )}
        {results["Birth Place"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Birth Place
            </Typo>
            <Typo size={12}>{results["Birth Place"].join("\n")}</Typo>
          </View>
        )}
        {results["Business Phone"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Business Phone
            </Typo>
            <Typo size={12}>{results["Business Phone"].join("\n")}</Typo>
          </View>
        )}
        {results["Credit Card"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Credit Card
            </Typo>
            <Typo size={12}>{results["Credit Card"].join("\n")}</Typo>
          </View>
        )}
        {results["Facebook Account"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Facebook Account
            </Typo>
            <Typo size={12}>{results["Facebook Account"].join("\n")}</Typo>
          </View>
        )}
        {results["Instagram Account"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Instagram Account
            </Typo>
            <Typo size={12}>{results["Instagram Account"].join("\n")}</Typo>
          </View>
        )}
        {results["Passport #"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Passport #
            </Typo>
            <Typo size={12}>{results["Passport #"].join("\n")}</Typo>
          </View>
        )}
        {results["Personal Cell"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Personal Cell
            </Typo>
            <Typo size={12}>{results["Personal Cell"].join("\n")}</Typo>
          </View>
        )}
        {results["Twitter Account"]?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Twitter Account
            </Typo>
            <Typo size={12}>{results["Twitter Account"].join("\n")}</Typo>
          </View>
        )}
        {results?.DDL?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              DDL
            </Typo>
            <Typo size={12}>{results?.DDL?.join("\n")}</Typo>
          </View>
        )}
        {results?.Employer?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Employer
            </Typo>
            <Typo size={12}>{results?.Employer?.join("\n")}</Typo>
          </View>
        )}
        {results?.Location?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              Location
            </Typo>
            <Typo size={12}>{results?.Location?.join("\n")}</Typo>
          </View>
        )}
        {results?.SSN?.length > 0 && (
          <View style={styles.container}>
            <Typo size={16} fontWeight={"500"}>
              SSN
            </Typo>
            <Typo size={12}>{results?.SSN?.join("\n")}</Typo>
          </View>
        )}
      </View>
    </ScreenWrapper>
  );
};

export default Details;

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    padding: 10,
  },
});
