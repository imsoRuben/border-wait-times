import { useLocalSearchParams } from 'expo-router';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Pressable } from 'react-native';

export default function PortDetailScreen() {
  const { data } = useLocalSearchParams();
  const router = useRouter();

  let parsedData = null;
  try {
    parsedData = typeof data === 'string' ? JSON.parse(data) : null;
  } catch (e) {
    parsedData = null;
  }

  if (!parsedData) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Invalid or missing data</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Pressable style={styles.button} onPress={() => router.back()}>
        <Text style={styles.buttonText}>Go Back</Text>
      </Pressable>
      <Text style={styles.title}>Port Details</Text>
      <View style={styles.dataBlock}>
        {Object.entries(parsedData).map(([key, value]) => {
          if (
            key === 'commercial_vehicle_lanes' ||
            key === 'passenger_vehicle_lanes' ||
            key === 'pedestrian_lanes'
          ) {
            return (
              <View key={key} style={styles.dataText}>
                <Text style={[styles.dataText, { fontWeight: 'bold' }]}>
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </Text>
                {Object.entries(value as Record<string, any>).map(([subKey, subValue]) => {
                  if (typeof subValue === 'object' && subValue !== null) {
                    return Object.entries(subValue).map(([innerKey, innerValue]) => (
                      <Text key={subKey + '-' + innerKey} style={styles.dataText}>
                        {subKey.replace(/_/g, ' ')} - {innerKey.replace(/_/g, ' ')}: {String(innerValue ?? 'No data')}
                      </Text>
                    ));
                  }
                  return (
                    <Text key={subKey} style={styles.dataText}>
                      {subKey.replace(/_/g, ' ')}: {String(subValue ?? 'No data')}
                    </Text>
                  );
                })}
              </View>
            );
          }

          return (
            <Text key={key} style={styles.dataText}>
              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: {String(value ?? 'No data')}
            </Text>
          );
        })}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  json: {
    fontFamily: 'Courier',
    fontSize: 12,
    color: '#333',
  },
  dataBlock: {
    marginBottom: 16,
  },
  dataText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 8,
  },
  button: {
    marginBottom: 16,
    paddingVertical: 12,
    paddingHorizontal: 20,
    backgroundColor: '#007aff',
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});