#pragma once // only import the header 1 time

class CalibratedAverageTouchSensor {
private:
  uint8_t touchPin;
  uint32_t averageValue;
  uint32_t deviationValue;

public:
  // Constructor
  CalibratedAverageTouchSensor(uint8_t pin, uint32_t deviation)
    : touchPin(pin),
      averageValue(0),
      deviationValue(deviation > 0 ? deviation : 1) {
  }

  void setDeviation(uint32_t deviation) {
    // Min deviation should be 1
    deviationValue = deviation > 0 ? deviation : 1;
  }

  uint32_t getAverage() const {
    return averageValue;
  }

  uint32_t getDeviation() const {
    return deviationValue;
  }

  // This is a blocking function (time is approx. sampleCount * delayMs)
  void calibrate(uint16_t sampleCount, uint32_t delayBetweenSamplesMs) {
    if (sampleCount == 0) {
      return;
    }

    uint64_t total = 0;

    for (uint16_t i = 0; i < sampleCount; i++) {
      total += touchRead(touchPin);
      delay(delayBetweenSamplesMs);
    }

    averageValue = total / sampleCount;
  }

  bool isTouched() const {
    uint32_t currentValue = touchRead(touchPin);
    return currentValue < (averageValue - deviationValue);
  }
};
