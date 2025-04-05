import { colors } from "@/constants/theme";
import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ViewStyle } from "react-native";
import Svg, { Path, Circle } from "react-native-svg";

interface GaugeMeterProps {
  score: string;
  size?: number;
  style?: ViewStyle;
  percentage: number;
}

const GaugeMeter: React.FC<GaugeMeterProps> = ({
  score,
  size = 200,
  style,
  percentage,
}) => {
  // Calculate the angles for the gauge paths
  const startAngle = -90;
  const endAngle = 90;
  const radius = size * 0.4;
  const sectionAngle = (endAngle - startAngle) / 4; // Divide into 4 equal sections
  const [refreshKey, setRefreshKey] = useState(Date.now());

  // Function to convert angle to coordinates
  const polarToCartesian = (
    centerX: number,
    centerY: number,
    radius: number,
    angleInDegrees: number
  ) => {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians),
    };
  };

  // Function to create arc path
  const createArc = (start: number, end: number, radius: number): string => {
    const center = size / 2;
    const startPoint = polarToCartesian(center, center, radius, end);
    const endPoint = polarToCartesian(center, center, radius, start);
    const largeArcFlag = end - start <= 180 ? 0 : 1;

    return [
      "M",
      startPoint.x,
      startPoint.y,
      "A",
      radius,
      radius,
      0,
      largeArcFlag,
      0,
      endPoint.x,
      endPoint.y,
    ].join(" ");
  };

  const getPercentage = () => {
    let scorePercentage = 0;
    switch (score?.toLowerCase()) {
      case "low":
        scorePercentage = 12.5;
        break;
      case "medium":
        scorePercentage = 37.5;
        break;
      case "high":
        scorePercentage = 62.5;
        break;
      case "critical":
        scorePercentage = 87.5;
        break;
      default:
        scorePercentage = 0;
        break;
    }
    return scorePercentage;
  };

  useEffect(() => {
    if (!score) {
      return;
    }
    setRefreshKey(Date.now());
  }, [score]);

  // Calculate needle rotation based on percentage
  const needleRotation =
    startAngle + (getPercentage() / 100) * (endAngle - startAngle);

  return (
    <View style={[styles.container, { width: size, height: size }, style]}>
      <Svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        key={refreshKey}
      >
        {/* Background arc */}
        <Path
          d={createArc(startAngle, endAngle, radius)}
          stroke="#333"
          strokeWidth={size * 0.08}
          fill="none"
        />

        {/* First section (Dark Green) */}
        <Path
          d={createArc(startAngle, startAngle + sectionAngle, radius)}
          stroke={colors.low}
          strokeWidth={size * 0.08}
          fill="none"
        />

        {/* Second section (Light Green) */}
        <Path
          d={createArc(
            startAngle + sectionAngle,
            startAngle + sectionAngle * 2,
            radius
          )}
          stroke={colors.medium}
          strokeWidth={size * 0.08}
          fill="none"
        />

        {/* Third section (Yellow) */}
        <Path
          d={createArc(
            startAngle + sectionAngle * 2,
            startAngle + sectionAngle * 3,
            radius
          )}
          stroke={colors.high}
          strokeWidth={size * 0.08}
          fill="none"
        />

        {/* Fourth section (Red) */}
        <Path
          d={createArc(startAngle + sectionAngle * 3, endAngle, radius)}
          stroke={colors.critical}
          strokeWidth={size * 0.08}
          fill="none"
        />

        {/* Needle */}
        <Path
          d={`M ${size / 2} ${size / 2} L ${size / 2} ${size * 0.2}`}
          stroke="#333"
          strokeWidth={size * 0.02}
          fill="none"
          transform={`rotate(${needleRotation}, ${size / 2}, ${size / 2})`}
        />

        {/* Center circle */}
        <Circle cx={size / 2} cy={size / 2} r={size * 0.04} fill="#333" />
      </Svg>

      <Text style={[styles.scoreText, { fontSize: 22 }]}>
        Your risk level is <Text>{score}</Text>
      </Text>
      <Text style={[styles.percentageText, { fontSize: 22 }]}>
        Your risk score is <Text>{percentage.toFixed(3)}</Text>
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "transparent",
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    marginBottom: 10,
  },
  scoreText: {
    color: "#333",
    fontWeight: "bold",
    position: "absolute",
    top: 200,
  },
  percentageText: {
    color: "#333",
    fontWeight: "bold",
    position: "absolute",
    top: 250,
  },
});

export default GaugeMeter;
