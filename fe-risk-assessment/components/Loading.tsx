import {
  ActivityIndicator,
  ActivityIndicatorProps,
  StyleSheet,
  Text,
  View,
} from "react-native";
import React, { useEffect, useState } from "react";
import { colors } from "@/constants/theme";
import Typo from "./Typo";
import Animated, { FadeInDown } from "react-native-reanimated";
import { useUniqueRandomNumbers } from "@/hooks/useUniqueRandomNumbers";

interface LoadingProps extends ActivityIndicatorProps {
  showSuggestions?: boolean;
}

const Loading = ({
  size = "large",
  color = colors.primary,
  showSuggestions = false,
}: LoadingProps) => {
  const socialMediaPrivacyTips = [
    "Set your social media profiles to private to limit public access.",
    "Avoid sharing your real birthdate, phone number, or home address online.",
    "Disable location tagging on posts to prevent real-time tracking.",
    "Be cautious when sharing vacation or travel plans publicly.",
    "Use a fake birthdate or partial information to protect identity theft risks.",
    "Avoid posting photos that include sensitive documents or credit cards.",
    "Regularly review and delete old posts that may contain personal details.",
    "Limit the amount of personal information shared in bio sections.",
    "Use different usernames for different platforms to prevent tracking.",
    "Be selective when accepting friend or follower requests from unknown people.",
    "Disable facial recognition settings in social media apps.",
    "Use a burner email for sign-ups instead of your primary email.",
    "Turn off ad personalization to limit data tracking by social platforms.",
    "Revoke permissions for third-party apps linked to your social media accounts.",
    "Avoid participating in viral quizzes or challenges that ask personal questions.",
    "Use encrypted messaging services instead of social media DMs for sensitive communication.",
    "Be mindful of metadata in uploaded photos, such as EXIF data that contains location details.",
    "Use a VPN when accessing social media on public networks to protect your IP address.",
    "Regularly check and update your privacy settings as platforms change their policies.",
    "Opt out of data-sharing settings that allow social media platforms to sell your data.",
    "Do not share your workplace or school details publicly.",
    "Limit the visibility of your friend list to prevent targeted phishing attacks.",
    "Turn off read receipts and last seen indicators on messaging apps.",
    "Be cautious about tagging locations in posts until after you leave the place.",
    "Do not share screenshots of private messages that may reveal sensitive data.",
    "Regularly review and remove apps that have access to your social media accounts.",
    "Do not post photos of your home’s exterior or address details.",
    "Use two-factor authentication (2FA) to secure your social media accounts.",
    "Report and block suspicious accounts that try to gather personal details from you.",
    "Avoid linking all your social media accounts publicly to reduce data correlation risks.",
  ];

  const getNextNumber = useUniqueRandomNumbers();

  const [suggestion, setSuggestion] = useState(socialMediaPrivacyTips[1]);
  const [refreshKey, setRefreshKey] = useState(Date.now());

  useEffect(() => {
    // Wait for numbers to be initialized before starting interval
    const intervalId = setInterval(() => {
      const nextIndex = getNextNumber();
      if (nextIndex !== -1) {
        setSuggestion(socialMediaPrivacyTips[nextIndex]);
        setRefreshKey(Date.now());
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }, [getNextNumber]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <ActivityIndicator size={size} color={color} />

      {showSuggestions && (
        <Animated.View
          style={{
            alignItems: "center",
            justifyContent: "center",
            top: 2,
            padding: 10,
          }}
          key={refreshKey}
          entering={FadeInDown.duration(1000)
            .delay(200)
            .springify()
            .damping(12)}
        >
          <Typo
            size={12}
            fontWeight={"700"}
            color={colors.primary}
            style={{ textAlign: "center", color: colors.primary }}
          >
            Security Tips
          </Typo>
          <Typo
            size={12}
            color={colors.loadingText}
            style={{ textAlign: "center" }}
          >
            {suggestion}
          </Typo>
        </Animated.View>
      )}
    </View>
  );
};

export default Loading;

const styles = StyleSheet.create({});
