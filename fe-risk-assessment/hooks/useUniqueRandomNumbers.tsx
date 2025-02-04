import { useState, useEffect } from "react";

// Custom hook to generate unique random numbers
export const useUniqueRandomNumbers = (): (() => number) => {
  const [numbers, setNumbers] = useState<number[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  useEffect(() => {
    // Generate and shuffle numbers from 0 to 29
    const shuffledNumbers = Array.from({ length: 30 }, (_, i) => i).sort(
      () => Math.random() - 0.5
    );
    setNumbers(shuffledNumbers);
    setCurrentIndex(0);
  }, []); // Only run on component mount

  const getNextNumber = (): number => {
    // Ensure numbers are initialized and currentIndex is valid
    if (numbers.length === 0) return -1; // Return an invalid number if not initialized yet

    if (currentIndex >= numbers.length) {
      // Reshuffle when all numbers are used
      const reshuffledNumbers = Array.from({ length: 30 }, (_, i) => i).sort(
        () => Math.random() - 0.5
      );
      setNumbers(reshuffledNumbers);
      setCurrentIndex(0);
      return reshuffledNumbers[0]; // Return the first number after reshuffling
    }

    const nextNumber = numbers[currentIndex];
    setCurrentIndex((prevIndex) => prevIndex + 1);
    return nextNumber;
  };

  return getNextNumber;
};
